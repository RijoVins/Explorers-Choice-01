"""Shared database access layer.

All application code obtains its session through :func:`get_db`. Which
backend that session talks to is decided once, at import time, by
``DATABASE_PROVIDER``. Route handlers and CRUD helpers contain no
provider-specific code, so switching providers is a configuration change
rather than a code change.
"""
from __future__ import annotations

import logging
from typing import Iterator

from sqlalchemy.orm import Session, sessionmaker

from ..config import settings
from .providers import DatabaseProvider, get_provider
from .base import Base  # noqa: F401  (re-exported for models/migrations)
from . import types  # noqa: F401  (re-exported for models)

logger = logging.getLogger("explorers.db")

# Resolved once. Application code never branches on the provider.
provider: DatabaseProvider = get_provider(settings)
engine = provider.engine()

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a session on the selected provider.

    A session that fails to connect raises here and propagates to the error
    handler. It is never retried against the other provider.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def dispose() -> None:
    """Close pooled connections. Used on shutdown and by tests."""
    engine.dispose()


__all__ = [
    "Base",
    "DatabaseProvider",
    "SessionLocal",
    "dispose",
    "engine",
    "get_db",
    "get_provider",
    "provider",
    "types",
]
