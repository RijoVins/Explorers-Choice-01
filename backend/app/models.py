"""SQLAlchemy models for the destination/package system.

Relationships:
  Destination 1───* Package
  Package     1───* ItineraryDay

Uses JSON (JSONB on PostgreSQL) for array/dict fields to keep the schema
flexible for travel content (highlights, galleries, inclusions, etc.).
"""
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base
from .db.types import LongText, UTCDateTime


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def json_column(default_factory: callable) -> Mapped[list]:
    """Helper for JSON columns defaulting to an empty list."""
    return mapped_column(JSON, default=default_factory)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    auth_provider: Mapped[str] = mapped_column(
        String(20), nullable=False, default="EMAIL", server_default="EMAIL"
    )  # EMAIL | GOOGLE
    provider_account_id: Mapped[str | None] = mapped_column(
        String(160), nullable=True, default=None, index=True
    )  # provider-specific identity (e.g. Google "sub")
    full_name: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(60), default="")
    country: Mapped[str] = mapped_column(String(120), default="")
    role: Mapped[str] = mapped_column(
        String(32), nullable=False, default="CUSTOMER", index=True
    )  # CUSTOMER | TRAVEL_AGENT | MANAGER | ACCOUNTANT | ADMIN
    requested_role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # bumped on password change/reset
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")
    train_bookings: Mapped[list["TrainBooking"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    cab_bookings: Mapped[list["CabBooking"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    hotels: Mapped[list["Hotel"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    user: Mapped["User"] = relationship(back_populates="reset_tokens")


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    short_description: Mapped[str] = mapped_column(LongText, default="")
    description: Mapped[str] = mapped_column(LongText, default="")
    hero_image: Mapped[str] = mapped_column(String(500), default="")
    gallery: Mapped[list] = json_column(list)
    best_time: Mapped[str] = mapped_column(String(160), default="")
    recommended_duration: Mapped[str] = mapped_column(String(120), default="")
    highlights: Mapped[list] = json_column(list)
    things_to_do: Mapped[list] = json_column(list)
    travel_information: Mapped[list] = json_column(list)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utcnow, onupdate=utcnow
    )

    packages: Mapped[list["Package"]] = relationship(
        back_populates="destination",
        cascade="all, delete-orphan",
        order_by="Package.name",
    )


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(
        ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    short_description: Mapped[str] = mapped_column(LongText, default="")
    description: Mapped[str] = mapped_column(LongText, default="")
    duration_days: Mapped[int] = mapped_column(Integer, default=0)
    duration_nights: Mapped[int] = mapped_column(Integer, default=0)
    starting_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    hero_image: Mapped[str] = mapped_column(String(500), default="")
    gallery: Mapped[list] = json_column(list)
    highlights: Mapped[list] = json_column(list)
    included: Mapped[list] = json_column(list)
    excluded: Mapped[list] = json_column(list)
    accommodation_summary: Mapped[str] = mapped_column(LongText, default="")
    transportation_summary: Mapped[str] = mapped_column(LongText, default="")
    meal_summary: Mapped[str] = mapped_column(LongText, default="")
    cancellation_policy: Mapped[str] = mapped_column(LongText, default="")
    important_information: Mapped[list] = json_column(list)
    booking_mode: Mapped[str] = mapped_column(String(32), default="REQUEST_ONLY")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utcnow, onupdate=utcnow
    )

    destination: Mapped["Destination"] = relationship(back_populates="packages")
    itinerary: Mapped[list["ItineraryDay"]] = relationship(
        back_populates="package",
        cascade="all, delete-orphan",
        order_by="ItineraryDay.day_number",
    )


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    package_id: Mapped[int] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(240), default="")
    description: Mapped[str] = mapped_column(LongText, default="")
    activities: Mapped[list] = json_column(list)
    meals: Mapped[str] = mapped_column(String(160), default="")
    accommodation: Mapped[str] = mapped_column(String(240), default="")
    transportation: Mapped[str] = mapped_column(String(240), default="")

    package: Mapped["Package"] = relationship(back_populates="itinerary")

    __table_args__ = (
        UniqueConstraint("package_id", "day_number", name="uq_itinerary_day_package_number"),
    )


class PackageFaq(Base):
    """Optional FAQ entries attached to a package (shown on package page)."""

    __tablename__ = "package_faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    package_id: Mapped[int] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question: Mapped[str] = mapped_column(String(320), nullable=False)
    answer: Mapped[str] = mapped_column(LongText, default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    package: Mapped["Package"] = relationship(back_populates="faqs")


Package.faqs = relationship(
    "PackageFaq",
    back_populates="package",
    cascade="all, delete-orphan",
    order_by="PackageFaq.sort_order",
)


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_reference: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("packages.id", ondelete="RESTRICT"), nullable=False, index=True)
    travel_date: Mapped[date] = mapped_column(Date, nullable=False)
    adults: Mapped[int] = mapped_column(Integer, nullable=False)
    children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    infants: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    departure_information: Mapped[str] = mapped_column(LongText, default="")
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(60), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    special_requirements: Mapped[str] = mapped_column(LongText, default="")
    notes: Mapped[str] = mapped_column(LongText, default="")
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    taxes: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING_CONFIRMATION", index=True)
    payment_status: Mapped[str] = mapped_column(String(32), nullable=False, default="NOT_REQUIRED")
    package_name: Mapped[str] = mapped_column(String(200), nullable=False)
    destination_name: Mapped[str] = mapped_column(String(160), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    booking_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    # BUG-18: optional client-supplied idempotency key to prevent duplicate
    # bookings when a successful response is lost and the client retries.
    idempotency_key: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)

    package: Mapped["Package"] = relationship()
    user: Mapped[Optional["User"]] = relationship(back_populates="bookings")
    travellers: Mapped[list["BookingTraveller"]] = relationship(back_populates="booking", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="booking", cascade="all, delete-orphan")
    documents: Mapped[list["BookingDocument"]] = relationship(back_populates="booking", cascade="all, delete-orphan")


class BookingTraveller(Base):
    __tablename__ = "booking_travellers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    traveller_type: Mapped[str] = mapped_column(String(16), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    booking: Mapped["Booking"] = relationship(back_populates="travellers")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    provider: Mapped[str] = mapped_column(String(64), default="")
    provider_reference: Mapped[str] = mapped_column(String(160), default="")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)

    booking: Mapped["Booking"] = relationship(back_populates="payments")

    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payment_amount_non_negative"),
    )


class BookingDocument(Base):
    """A downloadable document for a booking, authored by staff."""

    __tablename__ = "booking_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_secure: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    booking: Mapped["Booking"] = relationship(back_populates="documents")


class BookingNote(Base):
    """Internal operations note attached to a booking (never customer-visible)."""

    __tablename__ = "booking_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    body: Mapped[str] = mapped_column(LongText, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    booking: Mapped["Booking"] = relationship(back_populates="internal_notes")
    author: Mapped[Optional["User"]] = relationship(foreign_keys=[user_id])


Booking.internal_notes = relationship(
    "BookingNote",
    back_populates="booking",
    cascade="all, delete-orphan",
    order_by="BookingNote.created_at.desc()",
)


class Enquiry(Base):
    """CRM lead captured from the site or logged in by staff."""

    __tablename__ = "enquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(60), default="")
    country: Mapped[str] = mapped_column(String(120), default="")
    destination_interest: Mapped[str] = mapped_column(String(160), default="")
    package_id: Mapped[int | None] = mapped_column(ForeignKey("packages.id", ondelete="SET NULL"), nullable=True)
    package_name: Mapped[str] = mapped_column(String(200), default="")
    travel_date_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    travel_date_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    travellers: Mapped[int] = mapped_column(Integer, default=2)
    budget: Mapped[str] = mapped_column(String(120), default="")
    message: Mapped[str] = mapped_column(LongText, default="")
    notes: Mapped[str] = mapped_column(LongText, default="")
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="NEW", index=True
    )  # NEW → CONTACTED → REQUIREMENTS_COLLECTED → PLANNING → QUOTE_SENT → NEGOTIATION → WON|LOST
    assigned_staff_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    last_contact_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    next_action: Mapped[str] = mapped_column(String(320), default="")
    next_action_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)

    package: Mapped[Optional["Package"]] = relationship()
    assigned_staff: Mapped[Optional["User"]] = relationship()


class CustomerStory(Base):
    """Featured traveller testimonials (replaces reviews)."""

    __tablename__ = "customer_stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(160), nullable=False)
    destination: Mapped[str] = mapped_column(String(160), default="")
    package_id: Mapped[int | None] = mapped_column(ForeignKey("packages.id", ondelete="SET NULL"), nullable=True)
    package_name: Mapped[str] = mapped_column(String(200), default="")
    story: Mapped[str] = mapped_column(LongText, default="")
    photos: Mapped[list] = json_column(list)
    travel_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)

    package: Mapped[Optional["Package"]] = relationship()


class Offer(Base):
    """Marketing offer that can be shown on packages."""

    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(40), default="", index=True)
    description: Mapped[str] = mapped_column(LongText, default="")
    discount_type: Mapped[str] = mapped_column(String(16), default="PERCENT")  # PERCENT | FIXED
    discount_value: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    package_id: Mapped[int | None] = mapped_column(ForeignKey("packages.id", ondelete="SET NULL"), nullable=True)
    package_name: Mapped[str] = mapped_column(String(200), default="")
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)

    package: Mapped[Optional["Package"]] = relationship()


class AuditLog(Base):
    """Immutable record of important staff/admin actions."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    username: Mapped[str] = mapped_column(String(254), default="")
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), default="")
    details: Mapped[str] = mapped_column(LongText, default="")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, index=True)

    user: Mapped[Optional["User"]] = relationship()


class Setting(Base):
    """Company-wide key/value settings edited by administrators."""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, onupdate=utcnow)


class Hotel(Base):
    """A hotel listing submitted by a self-registered hotel owner."""

    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    destination: Mapped[str] = mapped_column(String(160), default="")
    tagline: Mapped[str] = mapped_column(String(240), default="")
    description: Mapped[str] = mapped_column(LongText, default="")
    image: Mapped[str] = mapped_column(String(500), default="")
    price_per_night: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    amenities: Mapped[list] = json_column(list)
    highlights: Mapped[list] = json_column(list)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utcnow, onupdate=utcnow
    )

    owner: Mapped["User"] = relationship(back_populates="hotels")


class TrainBooking(Base):
    """A train ticket booking created by a customer."""

    __tablename__ = "train_bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_reference: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    pnr_number: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    train_number: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    train_name: Mapped[str] = mapped_column(String(160), nullable=False)
    from_station_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    from_station_name: Mapped[str] = mapped_column(String(120), nullable=False)
    to_station_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    to_station_name: Mapped[str] = mapped_column(String(120), nullable=False)
    journey_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    departure_time: Mapped[str] = mapped_column(String(10), nullable=False)
    arrival_time: Mapped[str] = mapped_column(String(10), nullable=False)
    duration: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    travel_class: Mapped[str] = mapped_column(String(10), nullable=False)  # 1A, 2A, 3A, 3E, CC, EC, SL, 2S
    quota: Mapped[str] = mapped_column(String(30), nullable=False, default="GENERAL")
    passengers: Mapped[list] = json_column(list)  # list of {name, age, gender, berth_preference, seat_number, status}
    contact_name: Mapped[str] = mapped_column(String(160), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    contact_phone: Mapped[str] = mapped_column(String(60), nullable=False)
    base_fare: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    convenience_fee: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    gst: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="CONFIRMED", index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utcnow, onupdate=utcnow
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="train_bookings")


class CabBooking(Base):
    """A cab / car rental booking request placed by a customer.

    Bookings are stored as requests with an estimated fare; the Explorers
    Choice team confirms the final price and dispatches a driver. The admin
    receives an immediate email notification when a booking is placed.
    """

    __tablename__ = "cab_bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_reference: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # LOCAL | AIRPORT_TRANSFER | OUTSTATION
    trip_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    cab_type: Mapped[str] = mapped_column(String(40), nullable=False)  # e.g. Hatchback, Sedan, SUV
    pickup_location: Mapped[str] = mapped_column(String(300), nullable=False)
    drop_location: Mapped[str] = mapped_column(String(300), nullable=False)
    pickup_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    pickup_time: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    distance_kms: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    passengers: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(60), nullable=False)
    special_requirements: Mapped[str] = mapped_column(LongText, default="")
    base_fare: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    convenience_fee: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    gst: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING_CONFIRMATION", index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime, default=utcnow, onupdate=utcnow
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="cab_bookings")

