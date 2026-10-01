"""Backwards-compatible re-exports of the shared database access layer.

The implementation lives in :mod:`app.db`. Existing imports such as
``from .database import Base, get_db`` keep working unchanged.
"""
from __future__ import annotations

from .db import (  # noqa: F401
    Base,
    DatabaseProvider,
    SessionLocal,
    dispose,
    engine,

    get_db,
    get_provider,
    provider,
)


__all__ = [
    "Base",
    "DatabaseProvider",
    "SessionLocal",
    "dispose",
    "engine",
    "get_db",
    "get_provider",
    "provider",
]
