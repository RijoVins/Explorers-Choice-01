"""Authentication + RBAC verification against a DISPOSABLE MySQL test database.

Run only against `explorers_choice_test`. The script aborts if the resolved
engine points at any other database, so it can never write synthetic users to
the active application schema.

    MYSQL_DATABASE=explorers_choice_test ./.venv/bin/python scripts/verify_rbac_testdb.py

Everything here uses the application's real authentication and permission code
(security.get_current_user, require_admin, require_roles, require_hotel_owner,
crud.reset_user_password) through the real FastAPI app over TestClient.
"""
import os
import pathlib
import secrets
import sys

TEST_DB = "explorers_choice_test"
os.environ["MYSQL_DATABASE"] = TEST_DB
os.environ["DATABASE_PROVIDER"] = "mysql"

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import func, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
import app.models as models  # noqa: E402
from app import crud  # noqa: E402
from app.security import hash_password  # noqa: E402
from app.routes.auth import _hash_token  # noqa: E402
from app.main import app  # noqa: E402

resolved = engine.url.database
if resolved != TEST_DB:
    print(f"ABORT: engine points at {resolved!r}, refusing to write outside {TEST_DB!r}")
    sys.exit(2)
print(f"target database: {resolved}  (disposable test schema)")
print(f"active app db  : explorers_choice_app  (never written by this script)\n")

ROLES = ["CUSTOMER", "HOTEL_OWNER", "TRAVEL_AGENT", "ACCOUNTANT", "MANAGER", "ADMIN"]
PASSWORD = "synthetic-test-password"
# A real browser always sends Origin on state-changing requests; the app's CSRF
# guard rejects unsafe requests carrying a session cookie without a valid one.
ORIGIN = "http://localhost:3000"
HEADERS = {"Origin": ORIGIN}
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -> {detail}" if detail else ""))


def as_role(client, token):
    client.cookies.clear()
    client.cookies.set("ec_session", token, domain="testserver.local", path="/")


db = Session(engine)
db.query(models.User).delete()
db.query(models.PasswordResetToken).delete()
db.commit()

tokens = {}
for i, role in enumerate(ROLES):
    db.add(models.User(
        email=f"rbac-{role.lower()}@test.invalid",
        full_name=f"Synthetic {role}",
        phone=f"+1555000{i:04d}", country="Testland",
        role=role,
        is_staff=role != "HOTEL_OWNER" and role != "CUSTOMER",
        password_hash=hash_password(PASSWORD),
    ))
# A staff role with is_staff=False, to prove the is_staff gate is enforced.
db.add(models.User(email="rbac-flagship@test.invalid", full_name="Synthetic Flagged",
                   phone="+1555000999", country="Testland",
                   role="MANAGER", is_staff=False, password_hash=hash_password(PASSWORD)))
db.add(models.User(email="rbac-weakpw@test.invalid", full_name="Synthetic Weak",
                   phone="+1555000998", country="Testland",
                   role="CUSTOMER", password_hash=hash_password(PASSWORD)))
db.commit()
print(f"seeded {len(ROLES) + 2} synthetic users in {TEST_DB}\n")

with TestClient(app) as client:
    print("SUCCESSFUL LOGIN")
    for role in ROLES:
        r = client.post("/api/auth/login", headers=HEADERS,
                        json={"email": f"rbac-{role.lower()}@test.invalid", "password": PASSWORD})
        token = client.cookies.get("ec_session")
        check(f"login succeeds for {role}", r.status_code == 200 and bool(token),
              f"HTTP {r.status_code}")
        if token:
            tokens[role] = token

    r = client.get("/api/auth/me")
    check("issued cookie authenticates /api/auth/me",
          r.status_code == 200 and r.json().get("role") is not None,
          f"role={r.json().get('role') if r.status_code == 200 else None}")

    print("\nSESSION INVALIDATION AFTER PASSWORD RESET (real /reset-password)")
    as_role(client, tokens["CUSTOMER"])
    r = client.get("/api/account")
    check("session valid before reset", r.status_code == 200, f"HTTP {r.status_code}")
    stale = tokens["CUSTOMER"]

    raw_token = secrets.token_urlsafe(32)
    user = crud.get_user(db, email="rbac-customer@test.invalid")
    crud.create_password_reset(db, user, _hash_token(raw_token))
    check("reset token recorded for user", user.id is not None, f"user_id={user.id}")

    r = client.post("/api/auth/reset-password", headers=HEADERS,
                    json={"token": "definitely-not-a-real-token", "password": "newpass-123"})
    check("bogus reset token rejected", r.status_code == 400, f"HTTP {r.status_code}")

    r = client.post("/api/auth/reset-password", headers=HEADERS,
                    json={"token": raw_token, "password": "brand-new-password-456"})
    check("valid reset token accepted", r.status_code == 200, f"HTTP {r.status_code}")

    as_role(client, stale)
    r = client.get("/api/account")
    check("old session rejected on protected route after reset", r.status_code == 401,
          f"HTTP {r.status_code}")
    r = client.get("/api/auth/me")
    check("old session resolves to no user after reset",
          r.status_code == 200 and r.json() is None, f"user={r.json()!r}")

    client.cookies.clear()
    r = client.post("/api/auth/login", headers=HEADERS,
                    json={"email": "rbac-customer@test.invalid", "password": PASSWORD})
    check("old password rejected after reset", r.status_code == 401, f"HTTP {r.status_code}")
    r = client.post("/api/auth/login", headers=HEADERS,
                    json={"email": "rbac-customer@test.invalid", "password": "brand-new-password-456"})
    check("new password accepted after reset", r.status_code == 200, f"HTTP {r.status_code}")
    tokens["CUSTOMER"] = client.cookies.get("ec_session")

    r = client.post("/api/auth/reset-password", headers=HEADERS,
                    json={"token": raw_token, "password": "replay-attempt-789"})
    check("used reset token cannot be replayed", r.status_code == 400, f"HTTP {r.status_code}")

    print("\nRBAC: require_admin  (GET /api/admin/bookings)")
    for role, allowed in [("CUSTOMER", False), ("HOTEL_OWNER", False),
                          ("TRAVEL_AGENT", True), ("ACCOUNTANT", True),
                          ("MANAGER", True), ("ADMIN", True)]:
        as_role(client, tokens[role])
        r = client.get("/api/admin/bookings")
        ok = (r.status_code in (200, 404)) if allowed else (r.status_code == 403)
        check(f"{role} {'allowed' if allowed else 'denied'} on staff area", ok,
              f"HTTP {r.status_code}")

    print("\nRBAC: require_roles('ADMIN')  (PATCH /api/admin/customers/1/role)")
    for role, allowed in [("CUSTOMER", False), ("HOTEL_OWNER", False),
                          ("TRAVEL_AGENT", False), ("ACCOUNTANT", False),
                          ("MANAGER", False), ("ADMIN", True)]:
        as_role(client, tokens[role])
        r = client.patch("/api/admin/customers/1/role", headers=HEADERS, json={"role": "MANAGER"})
        ok = (r.status_code != 403) if allowed else (r.status_code == 403)
        check(f"{role} {'allowed' if allowed else 'denied'} on role management", ok,
              f"HTTP {r.status_code}")

    print("\nRBAC: require_roles(*FINANCE = ACCOUNTANT, MANAGER, ADMIN)  (POST /api/admin/payments)")
    for role, allowed in [("CUSTOMER", False), ("HOTEL_OWNER", False),
                          ("TRAVEL_AGENT", False), ("ACCOUNTANT", True),
                          ("MANAGER", True), ("ADMIN", True)]:
        as_role(client, tokens[role])
        r = client.post("/api/admin/payments", headers=HEADERS, json={})
        ok = (r.status_code != 403) if allowed else (r.status_code == 403)
        check(f"{role} {'allowed' if allowed else 'denied'} on finance actions", ok,
              f"HTTP {r.status_code}")

    print("\nRBAC: require_roles(*CONTENT = MANAGER, ADMIN)  (DELETE /api/admin/enquiries/1)")
    for role, allowed in [("CUSTOMER", False), ("HOTEL_OWNER", False),
                          ("TRAVEL_AGENT", False), ("ACCOUNTANT", False),
                          ("MANAGER", True), ("ADMIN", True)]:
        as_role(client, tokens[role])
        r = client.delete("/api/admin/enquiries/1", headers=HEADERS)
        ok = (r.status_code != 403) if allowed else (r.status_code == 403)
        check(f"{role} {'allowed' if allowed else 'denied'} on content actions", ok,
              f"HTTP {r.status_code}")

    print("\nRBAC: require_hotel_owner  (GET /api/hotel-owner/hotels)")
    for role, allowed in [("CUSTOMER", False), ("HOTEL_OWNER", True),
                          ("TRAVEL_AGENT", False), ("ACCOUNTANT", False),
                          ("MANAGER", False), ("ADMIN", False)]:
        as_role(client, tokens[role])
        r = client.get("/api/hotel-owner/hotels")
        ok = (r.status_code == 200) if allowed else (r.status_code == 403)
        check(f"{role} {'allowed' if allowed else 'denied'} on hotel-owner area", ok,
              f"HTTP {r.status_code}")

    print("\nCSRF GUARD (must stay enforced)")
    as_role(client, tokens["ADMIN"])
    r = client.post("/api/admin/payments", json={})
    check("unsafe request with session cookie but no Origin blocked (403)", r.status_code == 403,
          f"HTTP {r.status_code}")
    r = client.post("/api/admin/payments", headers={"Origin": "https://evil.invalid"}, json={})
    check("unsafe request with a foreign Origin blocked (403)", r.status_code == 403,
          f"HTTP {r.status_code}")
    r = client.post("/api/admin/payments", headers=HEADERS, json={})
    check("unsafe request with a valid Origin passes the CSRF guard", r.status_code != 403,
          f"HTTP {r.status_code}")

    print("\nRBAC: is_staff gate (role=MANAGER but is_staff=False)")
    client.cookies.clear()
    r = client.post("/api/auth/login", headers=HEADERS,
                    json={"email": "rbac-flagship@test.invalid", "password": PASSWORD})
    check("MANAGER with is_staff=False can log in", r.status_code == 200, f"HTTP {r.status_code}")
    r = client.get("/api/admin/bookings")
    check("MANAGER with is_staff=False denied on staff area (403)", r.status_code == 403,
          f"HTTP {r.status_code}")
    r = client.get("/api/hotel-owner/hotels")
    check("MANAGER with is_staff=False denied on hotel-owner area (403)",
          r.status_code == 403, f"HTTP {r.status_code}")

print("\nSYNTHETIC DATA PRESENT ONLY IN THE TEST DATABASE")
db2 = Session(engine)
print(f"  users in {TEST_DB}: "
      f"{db2.execute(select(func.count()).select_from(models.User)).scalar()}")
db2.close()

print("\n" + "=" * 66)
failed = [n for n, ok in results if not ok]
print(f"{len(results) - len(failed)}/{len(results)} checks passed")
if failed:
    print("FAILED:")
    for n in failed:
        print("  -", n)
db.close()
sys.exit(1 if failed else 0)
