import os
import sys

# Ensure the backend project root is on the import path before importing the app.
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from sqlalchemy import pool  # noqa: E402
from alembic import context  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import Base  # noqa: E402
import app.models  # noqa: E402, F401 — registers models with Base.metadata

# The migration history in this directory targets PostgreSQL (it uses
# postgresql.JSONB). Refuse to run it against MySQL, whose schema is owned
# outside this application and must never be altered automatically.
if settings.is_mysql:
    raise RuntimeError(
        "Alembic migrations target PostgreSQL and are disabled when "
        "DATABASE_PROVIDER=mysql. The MySQL schema is managed externally. "
        "Set DATABASE_PROVIDER=supabase to run migrations against PostgreSQL."
    )

config = context.config
# alembic uses configparser under the hood, which treats % as an interpolation
# token unless escaped as %%. We must escape url-encoded passwords to prevent errors.
escaped_url = settings.database_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", escaped_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import engine_from_config

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()