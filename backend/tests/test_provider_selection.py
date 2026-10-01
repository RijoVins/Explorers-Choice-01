"""Provider selection, dialect compatibility and no-fallback guarantees.

These tests never open a database connection: the engine is lazy and the
MySQL URL points at a host that is never contacted. They run offline.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

MYSQL_ENV = {
    "DATABASE_PROVIDER": "mysql",
    "MYSQL_HOST": "mysql.invalid",
    "MYSQL_PORT": "4000",
    "MYSQL_DATABASE": "explorers_choice_db",
    "MYSQL_USER": "someuser",
    "MYSQL_PASSWORD": "somepassword",
    "MYSQL_SSL_MODE": "verify-ca",
    "MYSQL_SSL_CA": str(BACKEND_DIR / "certs" / "test-ca.pem"),
    "EXPLORERS_ALLOW_INSECURE": "true",
}


@pytest.fixture
def clean_env(monkeypatch):
    """Drop every DB-related variable so each test starts from a known state."""
    for key in list(os.environ):
        if key.startswith(("DATABASE_", "DB_", "MYSQL_")):
            monkeypatch.delenv(key, raising=False)
    yield monkeypatch


def _fresh_settings(clean_env, env: dict):
    for key, value in env.items():
        clean_env.setenv(key, value)
    # A real .env would leak in here; point the settings object at nothing.
    for module in [m for m in list(sys.modules) if m.startswith("app.")]:
        del sys.modules[module]
    settings_mod = importlib.import_module("app.config")
    importlib.reload(settings_mod)
    return settings_mod.settings


# --------------------------------------------------------------------------
# Provider selection
# --------------------------------------------------------------------------

def test_mysql_is_the_selected_provider(clean_env):
    settings = _fresh_settings(clean_env, MYSQL_ENV)
    assert settings.active_provider == "mysql"
    assert settings.is_mysql is True


def test_unknown_provider_is_rejected(clean_env):
    """Only 'mysql' is valid; anything else must fail at startup."""
    with pytest.raises(Exception) as excinfo:
        _fresh_settings(clean_env, {**MYSQL_ENV, "DATABASE_PROVIDER": "oracle"})
    assert "oracle" in str(excinfo.value).lower() or "DATABASE_PROVIDER" in str(excinfo.value)


def test_mysql_requires_credentials(clean_env):
    env = dict(MYSQL_ENV)
    env["MYSQL_PASSWORD"] = ""
    with pytest.raises(Exception) as excinfo:
        _fresh_settings(clean_env, env)
    assert "MYSQL_PASSWORD" in str(excinfo.value)


def test_unverified_tls_is_refused(clean_env):
    env = dict(MYSQL_ENV)
    env["MYSQL_SSL_MODE"] = "required"
    with pytest.raises(Exception) as excinfo:
        _fresh_settings(clean_env, env)
    assert "MYSQL_SSL_MODE" in str(excinfo.value)


# --------------------------------------------------------------------------
# Provider implementations
# --------------------------------------------------------------------------

def test_mysql_url_is_built_and_tls_is_verified(clean_env):
    from app.db.providers import MySQLProvider

    settings = _fresh_settings(clean_env, MYSQL_ENV)
    url = MySQLProvider(settings).build_url()
    assert url.startswith("mysql+pymysql://")
    assert "ssl_verify_cert=true" in url
    assert "ssl_verify_identity" not in url  # verify-ca does not pin hostname


def test_verify_full_pins_hostname(clean_env):
    from app.db.providers import MySQLProvider

    settings = _fresh_settings(clean_env, {**MYSQL_ENV, "MYSQL_SSL_MODE": "verify-full"})
    url = MySQLProvider(settings).build_url()
    assert "ssl_verify_identity=true" in url


def test_password_with_special_chars_is_encoded(clean_env):
    from app.db.providers import MySQLProvider

    settings = _fresh_settings(clean_env, {**MYSQL_ENV, "MYSQL_PASSWORD": "p@ss:w/rd#1"})
    url = MySQLProvider(settings).build_url()
    assert "p%40ss%3Aw%2Frd%231" in url


def test_mysql_disables_startup_migrations(clean_env):
    from app.db.providers import MySQLProvider

    settings = _fresh_settings(clean_env, MYSQL_ENV)
    assert MySQLProvider(settings).run_migrations_on_startup() is False


def test_only_mysql_provider_exists(clean_env):
    """Only mysql is registered; no other backend can be selected."""
    from app.db import providers

    settings = _fresh_settings(clean_env, MYSQL_ENV)
    provider = providers.get_provider(settings)
    assert provider.name == "mysql"
    assert set(providers.PROVIDERS) == {"mysql"}


def test_unresolvable_provider_never_falls_back(clean_env):
    """An unusable selection must raise, not quietly use another backend."""
    from app.db import providers

    settings = _fresh_settings(clean_env, MYSQL_ENV)
    settings.database_provider = "nonexistent"
    with pytest.raises(ValueError):
        providers.get_provider(settings)


# --------------------------------------------------------------------------
# Dialect compatibility of the shared models
# --------------------------------------------------------------------------

def _ddl(dialect_module, dialect_name):
    """Render the full schema DDL for one dialect, offline."""
    from sqlalchemy import create_mock_engine
    import app.models  # noqa: F401  (registers tables on Base.metadata)
    from app.database import Base

    statements: list[str] = []
    engine = create_mock_engine(
        f"{dialect_name}://",
        lambda sql, *a, **kw: statements.append(str(sql.compile(dialect=engine.dialect))),
    )
    Base.metadata.create_all(engine, checkfirst=False)
    return statements


def test_models_compile_for_mysql(clean_env):
    _fresh_settings(clean_env, MYSQL_ENV)
    statements = _ddl("pymysql", "mysql")
    assert statements
    joined = "\n".join(statements)
    # Dialect-neutral timestamp type must become MySQL DATETIME, not TIMESTAMPTZ.
    assert "DATETIME(6)" in joined
    assert "TIMESTAMP WITH TIME ZONE" not in joined
    # Unbounded text, so long itineraries/stories cannot overflow 64 KiB.
    assert "LONGTEXT" in joined
    assert joined.count(" TEXT ") == 0
    # Every table the ORM knows about is emitted.
    for table in (
        "users", "destinations", "packages", "itinerary_days", "bookings",
        "payments", "enquiries", "hotels", "train_bookings", "cab_bookings",
        "audit_logs", "settings", "offers", "customer_stories",
    ):
        assert f"CREATE TABLE {table}" in joined, table


def test_expected_table_set(clean_env):
    _fresh_settings(clean_env, MYSQL_ENV)
    import app.models  # noqa: F401
    from app.database import Base

    tables = set(Base.metadata.tables)
    expected = {
        "users", "password_reset_tokens", "destinations", "packages",
        "itinerary_days", "package_faqs", "bookings", "booking_travellers",
        "payments", "booking_documents", "booking_notes", "enquiries",
        "customer_stories", "offers", "audit_logs", "settings", "hotels",
        "train_bookings", "cab_bookings",
    }
    assert tables == expected, f"unexpected tables: {tables ^ expected}"


# --------------------------------------------------------------------------
# Datetime round-trip keeps the JSON response format identical
# --------------------------------------------------------------------------

def test_utc_datetime_roundtrip_is_aware_on_mysql(clean_env):
    from datetime import datetime, timezone
    from sqlalchemy.dialects import mysql

    _fresh_settings(clean_env, MYSQL_ENV)
    from app.db.types import UTCDateTime

    column = UTCDateTime()
    aware = datetime(2026, 9, 29, 12, 30, 45, tzinfo=timezone.utc)

    # MySQL stores naive UTC ...
    stored = column.process_bind_param(aware, mysql.dialect())
    assert stored.tzinfo is None and stored.hour == 12
    # ... and hands an aware datetime back, so Pydantic emits the correct JSON.
    loaded = column.process_result_value(stored, mysql.dialect())
    assert loaded.tzinfo is not None and loaded == aware



@pytest.fixture
def clean_env(monkeypatch):
    """Drop every DB-related variable so each test starts from a known state."""
    for key in list(os.environ):
        if key.startswith(("DATABASE_", "DB_", "MYSQL_")):
            monkeypatch.delenv(key, raising=False)
    yield monkeypatch


def _fresh_settings(clean_env, env: dict):
    for key, value in env.items():
        clean_env.setenv(key, value)
    # A real .env would leak in here; point the settings object at nothing.
    for module in [m for m in list(sys.modules) if m.startswith("app.")]:
        del sys.modules[module]
    settings_mod = importlib.import_module("app.config")
    importlib.reload(settings_mod)
    return settings_mod.settings


# --------------------------------------------------------------------------
# Provider selection
# --------------------------------------------------------------------------

def test_mysql_is_the_selected_provider(clean_env):
    settings = _fresh_settings(clean_env, MYSQL_ENV)
    assert settings.active_provider == "mysql"
    assert settings.is_mysql is True
    assert settings.is_supabase is False


def test_supabase_can_be_reselected(clean_env):
    settings = _fresh_settings(clean_env, SUPABASE_ENV)
    assert settings.active_provider == "supabase"
    assert settings.is_supabase is True
    assert settings.is_mysql is False


def test_unknown_provider_is_rejected(clean_env):
    with pytest.raises(Exception) as excinfo:
        _fresh_settings(clean_env, {**MYSQL_ENV, "DATABASE_PROVIDER": "oracle"})
    assert "DATABASE_PROVIDER" in str(excinfo.value)


def test_mysql_requires_credentials(clean_env):
    env = dict(MYSQL_ENV)
    env["MYSQL_PASSWORD"] = ""
    with pytest.raises(Exception) as excinfo:
        _fresh_settings(clean_env, env)
    assert "MYSQL_PASSWORD" in str(excinfo.value)


def test_unverified_tls_is_refused(clean_env):
    env = dict(MYSQL_ENV)
    env["MYSQL_SSL_MODE"] = "required"
    with pytest.raises(Exception) as excinfo:
        _fresh_settings(clean_env, env)
    assert "MYSQL_SSL_MODE" in str(excinfo.value)


def test_supabase_url_still_validated_when_supabase_is_active(clean_env):
    env = dict(SUPABASE_ENV)
    env["DATABASE_URL"] = ""
    with pytest.raises(Exception) as excinfo:
        _fresh_settings(clean_env, env)
    assert "DATABASE_URL" in str(excinfo.value)


def test_supabase_url_not_required_when_mysql_is_active(clean_env):
    """Reactivating MySQL must not depend on Supabase credentials working."""
    env = dict(MYSQL_ENV)
    env["DATABASE_URL"] = ""
    settings = _fresh_settings(clean_env, env)
    assert settings.is_mysql is True


# --------------------------------------------------------------------------
# Provider implementations
# --------------------------------------------------------------------------

def test_mysql_url_is_built_and_tls_is_verified(clean_env):
    from app.db.providers import MySQLProvider

    settings = _fresh_settings(clean_env, MYSQL_ENV)
    url = MySQLProvider(settings).build_url()
    assert url.startswith("mysql+pymysql://")
    assert "ssl_verify_cert=true" in url
    assert "ssl_verify_identity" not in url  # verify-ca does not pin hostname


def test_verify_full_pins_hostname(clean_env):
    from app.db.providers import MySQLProvider

    settings = _fresh_settings(clean_env, {**MYSQL_ENV, "MYSQL_SSL_MODE": "verify-full"})
    url = MySQLProvider(settings).build_url()
    assert "ssl_verify_identity=true" in url


def test_password_with_special_chars_is_encoded(clean_env):
    from app.db.providers import MySQLProvider

    settings = _fresh_settings(clean_env, {**MYSQL_ENV, "MYSQL_PASSWORD": "p@ss:w/rd#1"})
    url = MySQLProvider(settings).build_url()
    assert "p%40ss%3Aw%2Frd%231" in url


def test_supabase_url_used_verbatim(clean_env):
    from app.db.providers import SupabaseProvider

    settings = _fresh_settings(clean_env, SUPABASE_ENV)
    assert SupabaseProvider(settings).build_url() == SUPABASE_ENV["DATABASE_URL"]


def test_mysql_disables_startup_migrations(clean_env):
    from app.db.providers import MySQLProvider, SupabaseProvider

    settings = _fresh_settings(clean_env, MYSQL_ENV)
    assert MySQLProvider(settings).run_migrations_on_startup() is False
    assert SupabaseProvider(settings).run_migrations_on_startup() is True


def test_only_one_provider_is_constructed(clean_env):
    """No fallback: exactly one provider exists, chosen by the setting."""
    from app.db import providers

    settings = _fresh_settings(clean_env, MYSQL_ENV)
    provider = providers.get_provider(settings)
    assert provider.name == "mysql"
    # Repeated resolution is stable: the choice is never revisited per request.
    assert providers.get_provider(settings).name == "mysql"
    assert provider is not providers.get_provider(settings)  # fresh instance, same target
    # Only the two known backends exist; nothing else can be selected.
    assert set(providers.PROVIDERS) == {"mysql", "supabase"}


def test_unresolvable_provider_never_falls_back(clean_env):
    """An unusable selection must raise, not quietly use the other backend."""
    from app.db import providers

    settings = _fresh_settings(clean_env, MYSQL_ENV)
    settings.database_provider = "supabase-missing-host"
    with pytest.raises(ValueError):
        providers.get_provider(settings)


# --------------------------------------------------------------------------
# Dialect compatibility of the shared models
# --------------------------------------------------------------------------

def _ddl(dialect_module, dialect_name):
    """Render the full schema DDL for one dialect, offline.

    Uses the engine's own dialect so MySQL-specific types actually appear;
    ``str(CreateTable(...))`` would silently fall back to the generic dialect.
    """
    from sqlalchemy import create_mock_engine
    import app.models  # noqa: F401  (registers tables on Base.metadata)
    from app.database import Base

    statements: list[str] = []
    engine = create_mock_engine(
        f"{dialect_name}://",
        lambda sql, *a, **kw: statements.append(str(sql.compile(dialect=engine.dialect))),
    )
    Base.metadata.create_all(engine, checkfirst=False)
    return statements


def test_models_compile_for_mysql(clean_env):
    _fresh_settings(clean_env, MYSQL_ENV)
    statements = _ddl("pymysql", "mysql")
    assert statements
    joined = "\n".join(statements)
    # Dialect-neutral timestamp type must become MySQL DATETIME, not TIMESTAMPTZ.
    assert "DATETIME(6)" in joined
    assert "TIMESTAMP WITH TIME ZONE" not in joined
    # Unbounded text, so long itineraries/stories cannot overflow 64 KiB.
    assert "LONGTEXT" in joined
    assert joined.count(" TEXT ") == 0
    # Every table the ORM knows about is emitted.
    for table in (
        "users", "destinations", "packages", "itinerary_days", "bookings",
        "payments", "enquiries", "hotels", "train_bookings", "cab_bookings",
        "audit_logs", "settings", "offers", "customer_stories",
    ):
        assert f"CREATE TABLE {table}" in joined, table


def test_models_compile_for_postgresql(clean_env):
    """Supabase reactivation must keep working: same models, Postgres DDL."""
    _fresh_settings(clean_env, SUPABASE_ENV)
    statements = _ddl("psycopg", "postgresql")
    assert statements
    joined = "\n".join(statements)
    assert "TIMESTAMP WITH TIME ZONE" in joined
    assert "LONGTEXT" not in joined


def test_expected_table_set(clean_env):
    _fresh_settings(clean_env, MYSQL_ENV)
    import app.models  # noqa: F401
    from app.database import Base

    tables = set(Base.metadata.tables)
    expected = {
        "users", "password_reset_tokens", "destinations", "packages",
        "itinerary_days", "package_faqs", "bookings", "booking_travellers",
        "payments", "booking_documents", "booking_notes", "enquiries",
        "customer_stories", "offers", "audit_logs", "settings", "hotels",
        "train_bookings", "cab_bookings",
    }
    assert tables == expected, f"unexpected tables: {tables ^ expected}"


# --------------------------------------------------------------------------
# Datetime round-trip keeps the JSON response format identical
# --------------------------------------------------------------------------

def test_utc_datetime_roundtrip_is_aware_on_both_backends(clean_env):
    from datetime import datetime, timezone
    from sqlalchemy.dialects import mysql, postgresql

    _fresh_settings(clean_env, MYSQL_ENV)
    from app.db.types import UTCDateTime

    column = UTCDateTime()
    aware = datetime(2026, 9, 29, 12, 30, 45, tzinfo=timezone.utc)

    # MySQL stores naive UTC ...
    stored = column.process_bind_param(aware, mysql.dialect())
    assert stored.tzinfo is None and stored.hour == 12
    # ... and hands an aware datetime back, so Pydantic emits the same JSON.
    loaded = column.process_result_value(stored, mysql.dialect())
    assert loaded.tzinfo is not None and loaded == aware

    # PostgreSQL keeps a genuinely timezone-aware column: the compiled DDL for
    # the supabase provider still says TIMESTAMP WITH TIME ZONE.
    from sqlalchemy.schema import CreateColumn
    from sqlalchemy import Table, Column, MetaData

    table = Table("t_probe", MetaData(), Column("at", column))
    ddl = str(CreateColumn(table.c.at).compile(dialect=postgresql.dialect())).strip()
    assert ddl == "at TIMESTAMP WITH TIME ZONE", ddl
    assert column.process_bind_param(aware, postgresql.dialect()) == aware


def test_default_tls_mode_verifies_hostname(clean_env):
    """Secure by default: omitting MYSQL_SSL_MODE must still check the hostname."""
    env = dict(MYSQL_ENV)
    env.pop("MYSQL_SSL_MODE")
    settings = _fresh_settings(clean_env, env)
    from app.db.providers import MySQLProvider

    assert settings.mysql_ssl_mode == "verify-full"
    assert "ssl_verify_identity=true" in MySQLProvider(settings).build_url()
