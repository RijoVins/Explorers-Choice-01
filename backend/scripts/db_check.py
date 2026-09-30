"""Read-only MySQL connectivity and schema inspection.

Proves the backend can reach the selected MySQL-compatible server and reports
the real tables and columns, so the ORM mapping is validated against facts
rather than assumptions. It uses the same configuration and provider code the
application uses, so it cannot drift from the live connection settings.

This script is STRICTLY READ-ONLY. It issues only SELECT / SHOW / DESCRIBE /
information_schema reads. It never inserts, updates, deletes, alters, creates
or drops anything, and never runs a migration.

Usage:
    python backend/scripts/db_check.py
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

SECRET_KEYS = ("MYSQL_PASSWORD", "DATABASE_URL", "SECRET_KEY", "ADMIN_API_KEY")


def main() -> int:
    from sqlalchemy import inspect, text

    try:
        from app.config import settings
        from app.db import provider
    except Exception as exc:
        print("=" * 72)
        print("READ-ONLY MySQL VERIFICATION")
        print("=" * 72)
        print(f"CONFIG ERROR: {type(exc).__name__}: {exc}")
        print("Nothing was modified.")
        return 1

    print("=" * 72)
    print("READ-ONLY MySQL VERIFICATION")
    print("=" * 72)
    print(f"DATABASE_PROVIDER : {settings.database_provider}")
    if not settings.is_mysql:
        print(f"NOTE: provider is {settings.database_provider!r}, not 'mysql'.")
        print("      This script inspects MySQL; set DATABASE_PROVIDER=mysql first.")
    print(f"MYSQL_HOST        : {settings.mysql_host or '<MYSQL_URL in use>'}")
    print(f"MYSQL_PORT        : {settings.mysql_port}")
    print(f"MYSQL_DATABASE    : {settings.mysql_database or '<MYSQL_URL in use>'}")
    print(f"MYSQL_USER        : {settings.mysql_user or '<MYSQL_URL in use>'}")
    print(f"MYSQL_SSL_MODE    : {settings.mysql_ssl_mode}")
    for key in SECRET_KEYS:
        print(f"{key:<17}: <not printed>")
    print("-" * 72)

    try:
        with provider.engine().connect() as conn:
            print("[1] connectivity        : OK")

            server = conn.execute(text("SELECT VERSION(), DATABASE()")).one()
            print(f"[2] server version      : {server[0]}")
            print(f"[3] current schema      : {server[1]}")

            insp = inspect(conn)
            tables = sorted(insp.get_table_names())
            print(f"[4] tables found        : {len(tables)}")
            if not tables:
                print("    !! No tables in this schema. Nothing to map.")

            for table in tables:
                cols = insp.get_columns(table)
                fks = insp.get_foreign_keys(table)
                uks = insp.get_unique_constraints(table)
                idx = insp.get_indexes(table)
                print("-" * 72)
                print(
                    f"  {table}  ({len(cols)} cols, {len(fks)} FK, "
                    f"{len(uks)} UNIQUE, {len(idx)} IDX)"
                )
                for c in cols:
                    flag = "" if c["nullable"] else " NOT NULL"
                    default = (
                        f" default={c['default']}" if c.get("default") is not None else ""
                    )
                    print(f"    - {c['name']:<32} {str(c['type'])[:38]:<38}{flag}{default}")
                for fk in fks:
                    local = ", ".join(fk.get("constrained_columns") or [])
                    ref = fk.get("referred_table")
                    remote = ", ".join(fk.get("referred_columns") or [])
                    ondel = (fk.get("options") or {}).get("ondelete")
                    tail = f" ON DELETE {ondel}" if ondel else ""
                    print(f"    FK {local} -> {ref}({remote}){tail}")

            print("-" * 72)
            print("ROW COUNTS (read-only)")
            for table in tables:
                try:
                    n = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar()
                    print(f"  {table:<32} {n:>10,}")
                except Exception as exc:
                    print(f"  {table:<32} (count failed: {exc})")

            print("-" * 72)
            print("COMPARISON vs ORM (backend/app/models.py)")
            try:
                import app.models  # noqa: F401
                from app.db import Base

                meta = Base.metadata
            except Exception as exc:
                print(f"  (could not import ORM metadata: {exc})")
                return 0

            # alembic_version is Alembic's own bookkeeping table, not an ORM table.
            bookkeeping = {"alembic_version"}
            want, have = set(meta.tables), set(tables) - bookkeeping
            missing, extra = sorted(want - have), sorted(have - want)
            if missing:
                print(f"  MISSING in MySQL ({len(missing)}): {', '.join(missing)}")
            if extra:
                print(f"  EXTRA in MySQL, not in ORM ({len(extra)}): {', '.join(extra)}")
            if not missing and not extra:
                print("  Table names match the ORM exactly.")
            if have | bookkeeping == set(tables) and "alembic_version" in tables:
                print("  (alembic_version present and excluded from the diff.)")

            for table in sorted(want & have):
                want_cols = {c.name for c in meta.tables[table].columns}
                have_cols = {c["name"] for c in insp.get_columns(table)}
                miss_c = sorted(want_cols - have_cols)
                extra_c = sorted(have_cols - want_cols)
                if miss_c or extra_c:
                    print(f"  {table}:")
                    if miss_c:
                        print(f"    missing columns: {', '.join(miss_c)}")
                    if extra_c:
                        print(f"    extra columns  : {', '.join(extra_c)}")

        print("=" * 72)
        print("RESULT: read-only verification completed. No data was modified.")
        return 0
    except Exception as exc:
        print("-" * 72)
        print(f"RESULT: FAILED to connect: {type(exc).__name__}: {exc}")
        print("No data was modified.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
