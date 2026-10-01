"""Database provider implementations.

A provider owns everything specific to the MySQL database backend: how the
connection URL is built, which engine options apply, and how a connectivity
check is performed.  The only supported provider is MySQL (including
TiDB Cloud which is MySQL-compatible).

There is deliberately **no fallback logic here**. If MySQL is unreachable,
the application fails loudly.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger("explorers.db")


class DatabaseProvider(ABC):
    """One database backend the application can talk to."""

    name: str
    dialect: str

    @abstractmethod
    def build_url(self) -> str:
        """Return the SQLAlchemy URL for this provider."""

    @abstractmethod
    def engine_options(self) -> dict[str, Any]:
        """Backend-specific ``create_engine`` keyword arguments."""

    @abstractmethod
    def run_migrations_on_startup(self) -> bool:
        """Whether Alembic may mutate the schema during application startup."""

    def connectivity_probe(self) -> None:
        """Raise if the database cannot be reached. Must not modify data."""
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    def engine(self) -> Engine:
        """Create the engine. Connection pooling is configured per backend."""
        return create_engine(
            self.build_url(),
            future=True,
            **self.engine_options(),
        )


class MySQLProvider(DatabaseProvider):
    """MySQL-compatible backend (MySQL 8, MariaDB, TiDB).

    Connection details are read as discrete variables rather than a single
    URL so that a password containing ``@``, ``:``, ``/`` or ``#`` cannot
    corrupt the URL. ``MYSQL_URL`` is still honoured if you prefer one.
    """

    name = "mysql"
    dialect = "mysql"

    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def build_url(self) -> str:
        explicit = (self.settings.mysql_url or "").strip()
        if explicit:
            return explicit

        user = quote_plus(self.settings.mysql_user)
        password = quote_plus(self.settings.mysql_password)
        host = self.settings.mysql_host
        port = self.settings.mysql_port
        database = quote_plus(self.settings.mysql_database)
        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"

        ssl_mode = (self.settings.mysql_ssl_mode or "verify-ca").strip().lower()
        if ssl_mode != "none":
            # PyMySQL receives these as connect() kwargs via the URL query
            # string. Verification stays on: "required" alone would encrypt
            # without proving the server is who it claims to be.
            ssl_params = []
            if self.settings.mysql_ssl_ca:
                ssl_params.append(f"ssl_ca={self.settings.mysql_ssl_ca}")
            ssl_params.append("ssl_verify_cert=true")
            if ssl_mode == "verify-full":
                # Also checks that the certificate matches the hostname.
                ssl_params.append("ssl_verify_identity=true")
            url += "&" + "&".join(ssl_params)
        return url

    def engine_options(self) -> dict[str, Any]:
        options: dict[str, Any] = {
            "pool_pre_ping": True,
            "pool_recycle": 1800,
            "pool_timeout": 30,
        }
        # connect_args fail fast instead of hanging a request thread.
        options["connect_args"] = {"connect_timeout": 10, "read_timeout": 30}
        if self.settings.mysql_pool_size is not None:
            options["pool_size"] = self.settings.mysql_pool_size
        if self.settings.mysql_max_overflow is not None:
            options["max_overflow"] = self.settings.mysql_max_overflow
        if self.settings.mysql_pool_recycle is not None:
            options["pool_recycle"] = self.settings.mysql_pool_recycle
        return options

    def run_migrations_on_startup(self) -> bool:
        # The MySQL schema is owned by the DBA and is never rewritten by this
        # application. Startup only verifies connectivity.
        return False


PROVIDERS: dict[str, type[DatabaseProvider]] = {
    MySQLProvider.name: MySQLProvider,
}


def get_provider(settings: Any) -> DatabaseProvider:
    """Resolve ``DATABASE_PROVIDER`` to exactly one provider instance.

    Only ``mysql`` is supported. Anything else raises at startup.
    """
    key = (settings.database_provider or "").strip().lower()
    provider_cls = PROVIDERS.get(key)
    if provider_cls is None:
        raise ValueError(
            f"DATABASE_PROVIDER={key!r} is not supported. "
            f"Only 'mysql' is accepted."
        )
    provider = provider_cls(settings)
    logger.info("Database provider resolved: %s", provider.name)
    return provider
