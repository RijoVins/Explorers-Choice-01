"""Declarative base shared by every ORM model.

Kept in its own module so that both :mod:`app.db` and :mod:`app.models`
can import it without a circular dependency.
"""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
