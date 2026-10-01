"""Provider-neutral database types.

The ORM models target MySQL (including TiDB Cloud). Column types are expressed
in a dialect-neutral way while still producing correct DDL and correct Python
values.

Two MySQL-specific considerations handled here:

* MySQL ``DATETIME`` has no timezone concept. ``UTCDateTime`` stores naive UTC
  on MySQL and re-attaches ``timezone.utc`` on read, so all values returned
  to the application are always timezone-aware.
* MySQL ``TEXT`` is capped at 64 KiB and raises "Data too long for column"
  rather than truncating. ``LongText`` maps to ``LONGTEXT`` on MySQL so
  long-form content (itineraries, stories, internal notes) can never overflow.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, Text
from sqlalchemy.dialects import mysql as mysql_dialect
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    """Timezone-aware UTC timestamp stored as naive DATETIME on MySQL.

    Stores naive UTC in the database; re-attaches ``timezone.utc`` on read
    so all application-level datetime values are always timezone-aware.
    """

    impl = DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect):  # noqa: ANN001, ANN201
        if dialect.name == "mysql":
            return dialect.type_descriptor(mysql_dialect.DATETIME(fsp=6))
        return dialect.type_descriptor(DateTime(timezone=True))

    def process_bind_param(self, value: Optional[datetime], dialect) -> Optional[datetime]:
        if value is None:
            return None
        # MySQL DATETIME carries no offset, so normalise to naive UTC on the way in.
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value: Optional[datetime], dialect) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class LongText(TypeDecorator):
    """``LONGTEXT`` on MySQL for unbounded text storage."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):  # noqa: ANN001, ANN201
        if dialect.name == "mysql":
            return dialect.type_descriptor(mysql_dialect.LONGTEXT())
        return dialect.type_descriptor(Text())


def to_utc(value: Any) -> Any:
    """Normalise any datetime coming from a driver to aware UTC."""
    if isinstance(value, datetime) and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
