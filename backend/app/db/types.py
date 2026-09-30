"""Provider-neutral database types.

The ORM models are shared by both the MySQL and the Supabase (PostgreSQL)
provider, so column types must be expressed in a dialect-neutral way while
still producing correct DDL and correct Python values on each backend.

Two differences between MySQL and PostgreSQL matter here:

* MySQL ``DATETIME`` has no timezone concept. PostgreSQL ``TIMESTAMPTZ``
  does. Naive datetimes returned by the MySQL driver would be serialised by
  Pydantic without a UTC designator, changing the JSON response format the
  frontend parses. ``UTCDateTime`` stores naive UTC on MySQL and re-attaches
  ``timezone.utc`` on read, so both providers return identical aware values.
* MySQL ``TEXT`` is capped at 64 KiB and raises "Data too long for column"
  rather than truncating. PostgreSQL ``TEXT`` is unbounded. ``LongText``
  maps to ``LONGTEXT`` on MySQL so long-form content (itineraries, stories,
  internal notes) can never overflow.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, Text
from sqlalchemy.dialects import mysql as mysql_dialect
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    """Timezone-aware UTC timestamp on any backend.

    PostgreSQL  -> TIMESTAMP WITH TIME ZONE
    MySQL       -> DATETIME(fsp=6) holding naive UTC, re-attached as UTC on read
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
        if dialect.name != "mysql":
            # PostgreSQL TIMESTAMPTZ stores the instant, so the aware value is
            # passed through unchanged. Stripping the offset here would make the
            # server reinterpret it in its own session timezone and shift it.
            return value
        # MySQL DATETIME carries no offset, so normalise to naive UTC on the way
        # in and re-attach UTC on the way out.
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
    """Unbounded text on PostgreSQL, ``LONGTEXT`` on MySQL."""

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
