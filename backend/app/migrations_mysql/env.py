"""Alembic environment for the **MySQL** provider only.

Deliberately separate from ``app/migrations``, which is the PostgreSQL
history. Neither environment may touch the other backend:

* ``app/migrations``      raises if ``DATABASE_PROVIDER=mysql``.
* this environment        raises unless ``DATABASE_PROVIDER=mysql``.

Migrations are never run automatically at startup for MySQL. Apply them
explicitly:

    python -m alembic -c alembic_mysql.ini upgrade head
"""
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.config import settings  # noqa: E402
from app.db import Base, provider  # noqa: E402
import app.models  # noqa: E402, F401 — registers models on Base.metadata

if not settings.is_mysql:
    raise RuntimeError(
        "These migrations are MySQL-only. Set DATABASE_PROVIDER=mysql to apply "
        "them, or use `python -m alembic upgrade head` (alembic.ini) for the "
        "Supabase/PostgreSQL schema."
    )

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _url() -> str:
    # Take the URL from the resolved provider so this can never diverge from
    # the URL the application itself connects with.
    return provider.build_url().replace("%", "%%")


def run_migrations_offline() -> None:
    context.configure(
        url=_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine

    connectable = create_engine(_url(), poolclass=pool.NullPool, future=True)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            # MySQL cannot ALTER most columns in place; batch mode emits a
            # table rebuild instead, which is what future migrations need.
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
