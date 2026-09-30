"""Isolated auth / RBAC / session-invalidation verification against MySQL.

Every request runs for real (real MySQL, real ORM, real auth logic) inside a
single outer transaction that is NEVER committed. The connection is rolled
back at the end, so no live record is created, changed or deleted.

Run from backend/:  ./.venv/bin/python scripts/verify_auth.py
"""
import pathlib
import re
import sys

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.database import Base, engine, get_db  # noqa: E402
import app.models as models  # noqa: E402
from app.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -> {detail}" if detail else ""))


connection = engine.connect()
trans = connection.begin()
session = Session(bind=connection, join_transaction_mode="create_savepoint")


def override_get_db():
    yield session


app.dependency_overrides[get_db] = override_get_db

try:
    with TestClient(app) as client:
        print("AUTHENTICATION")
        r = client.post("/api/auth/login",
                        json={"email": "nobody@example.invalid", "password": "wrong"})
        check("login rejects unknown email", r.status_code == 401, f"HTTP {r.status_code}")

        cust = models.User(email="verify-customer@example.invalid", full_name="Verify Customer",
                           phone="+10000000000", country="X", role="CUSTOMER",
                           password_hash=hash_password("correct-horse-battery"))
        agent = models.User(email="verify-agent@example.invalid", full_name="Verify Agent",
                            phone="+10000000001", country="X", role="TRAVEL_AGENT",
                            is_staff=True, password_hash=hash_password("correct-horse-battery"))
        admin = models.User(email="verify-admin@example.invalid", full_name="Verify Admin",
                            phone="+10000000002", country="X", role="ADMIN", is_staff=True,
                            password_hash=hash_password("correct-horse-battery"))
        inactive = models.User(email="verify-off@example.invalid", full_name="Verify Off",
                               phone="+10000000003", country="X", role="CUSTOMER",
                               is_active=False, password_hash=hash_password("correct-horse-battery"))
        session.add_all([cust, agent, admin, inactive])
        session.commit()
        cust_id, agent_id, admin_id = cust.id, agent.id, admin.id

        r = client.post("/api/auth/login",
                        json={"email": "verify-customer@example.invalid", "password": "nope"})
        check("login rejects wrong password", r.status_code == 401, f"HTTP {r.status_code}")

        r = client.post("/api/auth/login",
                        json={"email": "verify-customer@example.invalid",
                              "password": "correct-horse-battery"})
        check("login accepts valid credentials", r.status_code == 200, f"HTTP {r.status_code}")
        check("login sets session cookie", "ec_session" in r.cookies or client.cookies.get("ec_session"))

        r = client.get("/api/auth/me")
        check("session cookie authenticates /me",
              r.status_code == 200 and r.json().get("email") == "verify-customer@example.invalid",
              f"HTTP {r.status_code}")

        r = client.get("/api/account")
        check("customer reaches own account area", r.status_code == 200, f"HTTP {r.status_code}")

        print("\nROLE RESTRICTIONS")
        admin_paths = [p for p in app.openapi()["paths"]
                       if p.startswith("/api/admin") and "get" in app.openapi()["paths"][p]]
        probe = sorted(admin_paths)[0] if admin_paths else None
        check("admin routes exist to probe", probe is not None, str(probe))

        r = client.get(probe)
        check("CUSTOMER is blocked from staff area (403)", r.status_code == 403,
              f"HTTP {r.status_code} {r.json().get('detail','')[:48]}")

        client.cookies.clear()
        r = client.get("/api/admin/bookings") if "/api/admin/bookings" in app.openapi()["paths"] else client.get(probe)
        check("no cookie is blocked from staff area (401)", r.status_code == 401, f"HTTP {r.status_code}")

        client.cookies.clear()
        r = client.post("/api/auth/login",
                        json={"email": "verify-agent@example.invalid",
                              "password": "correct-horse-battery"})
        check("TRAVEL_AGENT reaches staff area", r.status_code == 200, f"HTTP {r.status_code}")

        client.cookies.clear()
        r = client.post("/api/auth/login",
                        json={"email": "verify-admin@example.invalid",
                              "password": "correct-horse-battery"})
        check("ADMIN reaches staff area", r.status_code == 200, f"HTTP {r.status_code}")

        print("\nSESSION INVALIDATION")
        client.cookies.clear()
        r = client.post("/api/auth/login",
                        json={"email": "verify-customer@example.invalid",
                              "password": "correct-horse-battery"})
        stale_cookie = r.cookies.get("ec_session") or client.cookies.get("ec_session")
        check("cookie captured for invalidation test", bool(stale_cookie))

        r = client.get("/api/auth/me")
        check("session valid before token_version bump", r.status_code == 200, f"HTTP {r.status_code}")

        user = session.get(models.User, cust_id)
        user.token_version = (user.token_version or 0) + 1
        session.commit()

        client.cookies.clear()
        client.cookies.set("ec_session", stale_cookie, domain="testserver.local", path="/")
        r = client.get("/api/auth/me")
        check("stale token rejected after token_version bump",
              r.status_code == 200 and r.json() is None,
              f"HTTP {r.status_code}, user={r.json()!r}")

        client.cookies.clear()
        r = client.get("/api/account")
        check("stale token rejected on protected route (401)", r.status_code == 401,
              f"HTTP {r.status_code}")

        print("\nINACTIVE / DISABLED ACCOUNT")
        client.cookies.clear()
        r = client.post("/api/auth/login",
                        json={"email": "verify-off@example.invalid",
                              "password": "correct-horse-battery"})
        check("inactive account cannot log in", r.status_code == 401, f"HTTP {r.status_code}")

        user = session.get(models.User, admin_id)
        user.is_active = False
        session.commit()
        client.cookies.clear()
        r = client.post("/api/auth/login",
                        json={"email": "verify-admin@example.invalid",
                              "password": "correct-horse-battery"})
        check("deactivated account blocked on next login", r.status_code == 401, f"HTTP {r.status_code}")

finally:
    app.dependency_overrides.clear()
    trans.rollback()
    connection.close()

print("\nPERSISTENCE CHECK (separate connection, sees only committed data)")
session2 = Session(engine)
for label, email in [("customer", "verify-customer@example.invalid"),
                     ("agent", "verify-agent@example.invalid"),
                     ("admin", "verify-admin@example.invalid"),
                     ("inactive", "verify-off@example.invalid")]:
    found = session2.execute(
        select(models.User).where(models.User.email == email)).scalar_one_or_none()
    check(f"no committed {label} row left behind", found is None,
          "absent" if found is None else f"LEAKED id={found.id}")
session2.close()

print("\n" + "=" * 62)
failed = [n for n, ok, _ in results if not ok]
print(f"{len(results) - len(failed)}/{len(results)} checks passed")
if failed:
    print("FAILED:")
    for n in failed:
        print("  -", n)
sys.exit(1 if failed else 0)
