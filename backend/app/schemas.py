"""Pydantic schemas for the destination/package system."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Destination schemas
# ---------------------------------------------------------------------------
class DestinationBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=180)
    country: str = Field(min_length=1, max_length=120)
    region: str = ""
    short_description: str = ""
    description: str = ""
    hero_image: str = ""
    gallery: list[str] = []
    best_time: str = ""
    recommended_duration: str = ""
    highlights: list[str] = []
    things_to_do: list[str] = []
    travel_information: list[str] = []
    is_featured: bool = False
    is_active: bool = True


class DestinationCreate(DestinationBase):
    pass


class DestinationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=160)
    slug: Optional[str] = Field(default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=180)
    country: Optional[str] = Field(default=None, min_length=1, max_length=120)
    region: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    hero_image: Optional[str] = None
    gallery: Optional[list[str]] = None
    best_time: Optional[str] = None
    recommended_duration: Optional[str] = None
    highlights: Optional[list[str]] = None
    things_to_do: Optional[list[str]] = None
    travel_information: Optional[list[str]] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class DestinationRead(BaseModel):
    """Read schema for Destination — tolerates missing MySQL columns."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    # MySQL table only has destination_id + name; all other fields are optional
    slug: str = ""
    country: str = ""
    region: str = ""
    short_description: str = ""
    description: str = ""
    hero_image: str = ""
    gallery: list = []
    best_time: str = ""
    recommended_duration: str = ""
    highlights: list = []
    things_to_do: list = []
    travel_information: list = []
    is_featured: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Itinerary day schemas
# ---------------------------------------------------------------------------
class ItineraryDayBase(BaseModel):
    day_number: int = Field(ge=1)
    title: str = ""
    description: str = ""
    activities: list[str] = []
    meals: str = ""
    accommodation: str = ""
    transportation: str = ""


class ItineraryDayCreate(ItineraryDayBase):
    pass


class ItineraryDayUpdate(BaseModel):
    day_number: Optional[int] = Field(default=None, ge=1)
    title: Optional[str] = None
    description: Optional[str] = None
    activities: Optional[list[str]] = None
    meals: Optional[str] = None
    accommodation: Optional[str] = None
    transportation: Optional[str] = None


class ItineraryDayRead(ItineraryDayBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    package_id: int


# ---------------------------------------------------------------------------
# Package schemas
# ---------------------------------------------------------------------------
class PackageBase(BaseModel):
    destination_id: int
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=220)
    short_description: str = ""
    description: str = ""
    duration_days: int = Field(ge=0, default=0)
    duration_nights: int = Field(ge=0, default=0)
    starting_price: float = Field(ge=0, default=0)
    currency: str = Field(default="USD", max_length=3)
    hero_image: str = ""
    gallery: list[str] = []
    highlights: list[str] = []
    included: list[str] = []
    excluded: list[str] = []
    accommodation_summary: str = ""
    transportation_summary: str = ""
    meal_summary: str = ""
    cancellation_policy: str = ""
    important_information: list[str] = []
    booking_mode: str = Field(default="REQUEST_ONLY", pattern=r"^(REQUEST_ONLY|INSTANT_BOOKING)$")
    is_featured: bool = False
    is_active: bool = True


class PackageCreate(PackageBase):
    itinerary: list[ItineraryDayCreate] = []
    faqs: list["PackageFaqCreate"] = []


class PackageUpdate(BaseModel):
    destination_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    slug: Optional[str] = Field(default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=220)
    short_description: Optional[str] = None
    description: Optional[str] = None
    duration_days: Optional[int] = Field(default=None, ge=0)
    duration_nights: Optional[int] = Field(default=None, ge=0)
    starting_price: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, max_length=3)
    hero_image: Optional[str] = None
    gallery: Optional[list[str]] = None
    highlights: Optional[list[str]] = None
    included: Optional[list[str]] = None
    excluded: Optional[list[str]] = None
    accommodation_summary: Optional[str] = None
    transportation_summary: Optional[str] = None
    meal_summary: Optional[str] = None
    cancellation_policy: Optional[str] = None
    important_information: Optional[list[str]] = None
    booking_mode: Optional[str] = Field(default=None, pattern=r"^(REQUEST_ONLY|INSTANT_BOOKING)$")
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class PackageFaqBase(BaseModel):
    question: str = Field(min_length=1, max_length=320)
    answer: str = ""
    sort_order: int = 0


class PackageFaqCreate(PackageFaqBase):
    pass


class PackageFaqUpdate(BaseModel):
    question: Optional[str] = Field(default=None, min_length=1, max_length=320)
    answer: Optional[str] = None
    sort_order: Optional[int] = None


class PackageFaqRead(PackageFaqBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PackageRead(BaseModel):
    """Read schema for Package — tolerates missing MySQL columns."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    destination_id: Optional[int] = None
    slug: str = ""
    short_description: str = ""
    description: str = ""
    duration_days: int = 0
    duration_nights: int = 0
    starting_price: float = 0.0
    currency: str = "INR"
    hero_image: str = ""
    gallery: list = []
    highlights: list = []
    included: list = []
    excluded: list = []
    accommodation_summary: str = ""
    transportation_summary: str = ""
    meal_summary: str = ""
    cancellation_policy: str = ""
    important_information: list = []
    booking_mode: str = "REQUEST_ONLY"
    is_featured: bool = False
    is_active: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    destination: Optional[DestinationRead] = None
    itinerary: list[ItineraryDayRead] = []
    faqs: list[PackageFaqRead] = []


class PackageSummary(BaseModel):
    """Lightweight package read for listing views — tolerates missing MySQL columns."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    destination_id: Optional[int] = None
    slug: str = ""
    short_description: str = ""
    description: str = ""
    duration_days: int = 0
    duration_nights: int = 0
    starting_price: float = 0.0
    currency: str = "INR"
    hero_image: str = ""
    gallery: list = []
    highlights: list = []
    included: list = []
    excluded: list = []
    accommodation_summary: str = ""
    transportation_summary: str = ""
    meal_summary: str = ""
    cancellation_policy: str = ""
    important_information: list = []
    booking_mode: str = "REQUEST_ONLY"
    is_featured: bool = False
    is_active: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    destination: Optional[DestinationRead] = None


PackageCreate.model_rebuild()


# ---------------------------------------------------------------------------
# Booking schemas
# ---------------------------------------------------------------------------
class BookingCreate(BaseModel):
    package_slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=220)
    travel_date: date
    adults: int = Field(ge=1, le=20)
    children: int = Field(default=0, ge=0, le=20)
    infants: int = Field(default=0, ge=0, le=10)
    departure_information: str = Field(default="", max_length=1000)
    full_name: str = Field(min_length=2, max_length=160)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    phone: str = Field(min_length=5, max_length=60)
    country: str = Field(min_length=2, max_length=120)
    special_requirements: str = Field(default="", max_length=4000)
    notes: str = Field(default="", max_length=4000)
    # BUG-18: optional idempotency key so a retried request returns the same booking.
    idempotency_key: Optional[str] = Field(default=None, min_length=8, max_length=64)


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_reference: str
    package_name: str
    destination_name: str
    travel_date: date
    adults: int
    children: int
    infants: int
    subtotal: float
    taxes: float
    total: float
    currency: str
    status: str
    payment_status: str
    booking_mode: str
    created_at: datetime


class BookingConfirmationRead(BaseModel):
    """A safe, non-sensitive subset of a booking for the public confirmation
    page. Never exposes contact details or any PII."""

    model_config = ConfigDict(from_attributes=True)

    booking_reference: str
    package_name: str
    destination_name: str
    duration_days: int
    travel_date: date
    adults: int
    children: int
    infants: int
    subtotal: float
    taxes: float
    total: float
    currency: str
    status: str
    payment_status: str
    booking_mode: str
    created_at: datetime


class BookingStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(PENDING|PENDING_CONFIRMATION|CONFIRMED|PAYMENT_PENDING|PARTIALLY_PAID|PAID|UPCOMING|TRAVELLING|COMPLETED|CANCELLED)$")
    payment_status: Optional[str] = Field(default=None, pattern=r"^(NOT_REQUIRED|PENDING|PARTIALLY_PAID|PAID|FAILED|REFUNDED)$")


class BookingDetail(BaseModel):
    """Authorized owner/admin view of a single booking."""

    model_config = ConfigDict(from_attributes=True)

    booking_reference: str
    package_id: int
    package_slug: str = ""
    package_name: str
    destination_name: str
    duration_days: int
    travel_date: date
    adults: int
    children: int
    infants: int
    departure_information: str
    country: str
    special_requirements: str
    notes: str
    subtotal: float
    taxes: float
    total: float
    currency: str
    status: str
    payment_status: str
    booking_mode: str
    created_at: datetime
    updated_at: datetime
    payments: list["PaymentRead"] = []
    documents: list["DocumentRead"] = []


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    amount: float
    currency: str
    status: str
    provider: str
    provider_reference: str
    created_at: datetime
    updated_at: datetime


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_type: str
    title: str
    file_name: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Customer authentication + profile
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(default="", max_length=60)
    country: str = Field(default="", max_length=120)
    requested_role: str = Field(default="CUSTOMER", pattern=r"^(CUSTOMER|TRAVEL_AGENT|HOTEL_OWNER)$")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if len(v.encode("utf-8")) > 1024:
            raise ValueError("Password is too long.")
        return v


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str = ""
    phone: str = ""
    country: str = "India"
    role: str = "CUSTOMER"
    auth_provider: str = "EMAIL"
    is_staff: bool = False
    created_at: datetime | None = None


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    password: str = Field(min_length=1, max_length=128)


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=160)
    phone: Optional[str] = Field(default=None, max_length=60)
    country: Optional[str] = Field(default=None, max_length=120)


class ForgotPasswordRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1, max_length=300)
    password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# ---------------------------------------------------------------------------
# Staff / roles
# ---------------------------------------------------------------------------
class UserBasicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_staff: bool


class StaffCreate(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(default="", max_length=60)
    country: str = Field(default="", max_length=120)
    role: str = Field(pattern=r"^(TRAVEL_AGENT|MANAGER|ACCOUNTANT|ADMIN)$")


class StaffUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=160)
    phone: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = Field(default=None, pattern=r"^(TRAVEL_AGENT|MANAGER|ACCOUNTANT|ADMIN)$")
    is_active: Optional[bool] = None


class StaffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    phone: str
    country: str
    role: str
    is_staff: bool
    is_active: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Booking notes + admin booking detail
# ---------------------------------------------------------------------------
class BookingNoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    body: str
    created_at: datetime
    author: Optional[UserBasicRead] = None


class BookingNoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class TravellerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    traveller_type: str
    quantity: int


class BookingAdminDetail(BookingDetail):
    id: int
    full_name: str
    email: str
    phone: str
    user: Optional[UserBasicRead] = None
    travellers: list[TravellerRead] = []
    internal_notes: list[BookingNoteRead] = []
    payments: list[PaymentRead] = []
    documents: list[DocumentRead] = []


class PaymentUpdate(BaseModel):
    status: str = Field(pattern=r"^(PENDING|PARTIALLY_PAID|PAID|FAILED|REFUNDED)$")
    provider_reference: Optional[str] = Field(default=None, max_length=160)


class ManualPaymentCreate(BaseModel):
    booking_id: int
    amount: float = Field(gt=0)
    currency: Optional[str] = Field(default=None, max_length=3)  # derived from booking if omitted
    status: str = Field(default="PAID", pattern=r"^(PENDING|PARTIALLY_PAID|PAID|FAILED|REFUNDED)$")
    provider: str = Field(default="manual", max_length=64)
    provider_reference: str = Field(default="", max_length=160)


class DocumentAdminRead(DocumentRead):
    booking_id: int


# ---------------------------------------------------------------------------
# Enquiry CRM
# ---------------------------------------------------------------------------
class EnquiryCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=160)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    phone: str = ""
    country: str = ""
    destination_interest: str = ""
    package_id: Optional[int] = None
    travel_date_from: Optional[date] = None
    travel_date_to: Optional[date] = None
    travellers: int = Field(default=2, ge=1, le=50)
    budget: str = ""
    message: str = ""
    notes: str = ""
    status: str = Field(default="NEW", pattern=r"^(NEW|CONTACTED|REQUIREMENTS_COLLECTED|PLANNING|QUOTE_SENT|NEGOTIATION|WON|LOST)$")
    assigned_staff_id: Optional[int] = None
    next_action: str = ""
    next_action_at: Optional[date] = None


class PublicEnquiryCreate(BaseModel):
    """GAP-01: restricted schema for the public contact form.

    Excludes staff-only fields (status, assignment, internal notes) so a public
    submission cannot set them.
    """

    customer_name: str = Field(min_length=1, max_length=160)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    phone: str = Field(default="", max_length=60)
    country: str = Field(default="", max_length=120)
    destination_interest: str = Field(default="", max_length=160)
    travellers: int = Field(default=2, ge=1, le=50)
    budget: str = Field(default="", max_length=120)
    message: str = Field(default="", max_length=4000)


class EnquiryUpdate(BaseModel):
    customer_name: Optional[str] = Field(default=None, min_length=1, max_length=160)
    email: Optional[str] = Field(default=None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    phone: Optional[str] = None
    country: Optional[str] = None
    destination_interest: Optional[str] = None
    package_id: Optional[int] = None
    travel_date_from: Optional[date] = None
    travel_date_to: Optional[date] = None
    travellers: Optional[int] = Field(default=None, ge=1, le=50)
    budget: Optional[str] = None
    message: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern=r"^(NEW|CONTACTED|REQUIREMENTS_COLLECTED|PLANNING|QUOTE_SENT|NEGOTIATION|WON|LOST)$")
    assigned_staff_id: Optional[int] = None
    last_contact_at: Optional[datetime] = None
    next_action: Optional[str] = None
    next_action_at: Optional[date] = None


class EnquiryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    email: str
    phone: str
    country: str
    destination_interest: str
    package_id: Optional[int] = None
    package_name: str
    travel_date_from: Optional[date] = None
    travel_date_to: Optional[date] = None
    travellers: int
    budget: str
    message: str
    notes: str
    status: str
    assigned_staff_id: Optional[int] = None
    assigned_staff: Optional[UserBasicRead] = None
    last_contact_at: Optional[datetime] = None
    next_action: str
    next_action_at: Optional[date] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Customer stories + offers
# ---------------------------------------------------------------------------
class CustomerStoryBase(BaseModel):
    customer_name: str = Field(min_length=1, max_length=160)
    destination: str = ""
    package_id: Optional[int] = None
    story: str = ""
    photos: list[str] = []
    travel_date: Optional[date] = None
    is_featured: bool = False
    is_published: bool = True


class CustomerStoryCreate(CustomerStoryBase):
    pass


class CustomerStoryUpdate(BaseModel):
    customer_name: Optional[str] = Field(default=None, min_length=1, max_length=160)
    destination: Optional[str] = None
    package_id: Optional[int] = None
    story: Optional[str] = None
    photos: Optional[list[str]] = None
    travel_date: Optional[date] = None
    is_featured: Optional[bool] = None
    is_published: Optional[bool] = None


class CustomerStoryRead(BaseModel):
    """Read schema for CustomerStory — tolerates missing MySQL columns."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    # MySQL stories table only has: story_id, user_id, booking_item_id,
    # title, content, status, published_at, created_at
    customer_name: str = "A traveller"
    destination: str = ""
    package_id: Optional[int] = None
    package_name: str = ""
    story: str = ""
    photos: list = []
    travel_date: Optional[date] = None
    is_featured: bool = False
    is_published: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OfferBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    code: str = ""
    description: str = ""
    discount_type: str = Field(default="PERCENT", pattern=r"^(PERCENT|FIXED)$")
    discount_value: float = Field(ge=0, default=0)
    package_id: Optional[int] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: bool = True


class OfferCreate(OfferBase):
    pass


class OfferUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    code: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[str] = Field(default=None, pattern=r"^(PERCENT|FIXED)$")
    discount_value: Optional[float] = Field(default=None, ge=0)
    package_id: Optional[int] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: Optional[bool] = None


class OfferRead(OfferBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    package_name: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Audit log + settings
# ---------------------------------------------------------------------------
class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    username: str
    action: str
    entity: str
    entity_id: str
    details: str
    created_at: datetime


class SettingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: dict
    updated_at: datetime


class SettingUpdate(BaseModel):
    value: dict


# ---------------------------------------------------------------------------
# Admin dashboard
# ---------------------------------------------------------------------------
class DashboardMetric(BaseModel):
    label: str
    value: int


class DashboardAction(BaseModel):
    kind: str  # booking_departure | enquiry_followup
    id: int
    title: str
    when: str
    href: str


class DashboardPaymentItem(BaseModel):
    booking_ref: str
    amount: float
    currency: str
    status: str
    created_at: datetime


class DashboardCustomerItem(BaseModel):
    id: int
    name: str
    email: str
    last_activity: datetime


class AdminDashboardRead(BaseModel):
    new_enquiries: int
    pending_bookings: int
    confirmed_bookings: int
    upcoming_trips: int
    total_bookings: int
    today_actions: list[DashboardAction]
    recent_payments: list[DashboardPaymentItem]
    recent_customers: list[DashboardCustomerItem]
    booking_status_counts: dict[str, int]


# ---------------------------------------------------------------------------
# Customers (admin)
# ---------------------------------------------------------------------------
class CustomerAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    phone: str
    country: str
    role: str
    requested_role: Optional[str] = None
    is_active: bool
    created_at: datetime

    booking_count: int = 0
    enquiry_count: int = 0
    total_spent: float = 0


class CustomerAdminDetail(CustomerAdminRead):
    bookings: list[BookingAdminDetail] = []
    enquiries: list[EnquiryRead] = []


# ---------------------------------------------------------------------------
# Hotels (hotel owner listings)
# ---------------------------------------------------------------------------
class HotelBase(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    location: str = Field(min_length=1, max_length=160)
    destination: str = Field(default="", max_length=160)
    tagline: str = Field(default="", max_length=240)
    description: str = Field(default="", max_length=4000)
    image: str = Field(default="", max_length=500)
    price_per_night: float = Field(default=0, ge=0)
    currency: str = Field(default="INR", max_length=3)
    amenities: list[str] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)


class HotelCreate(HotelBase):
    pass


class AdminHotelCreate(HotelCreate):
    """Hotel creation by staff — includes the publish flag and optional owner."""
    is_published: bool = True
    owner_id: int | None = None


class HotelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    location: str | None = Field(default=None, min_length=1, max_length=160)
    destination: str | None = Field(default=None, max_length=160)
    tagline: str | None = Field(default=None, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    image: str | None = Field(default=None, max_length=500)
    price_per_night: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=3)
    amenities: list[str] | None = None
    highlights: list[str] | None = None
    is_published: bool | None = None


class HotelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str = ""
    name: str = ""
    location: str = ""
    destination: str = ""
    tagline: str = ""
    description: str = ""
    image: str = ""
    price_per_night: float = 0.0
    currency: str = "INR"
    amenities: list[str] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class HotelOwnerRead(HotelRead):
    owner_id: int = 0
    is_published: bool = True


# ---------------------------------------------------------------------------
# Train ticket booking & search
# ---------------------------------------------------------------------------
class StationInfo(BaseModel):
    code: str
    name: str
    city: str
    state: str


class TrainClassAvailability(BaseModel):
    travel_class: str
    class_name: str
    fare: float
    status: str
    status_type: str  # AVAILABLE | RAC | WL


class TrainScheduleItem(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    from_station_code: str
    from_station_name: str
    to_station_code: str
    to_station_name: str
    departure_time: str
    arrival_time: str
    duration: str
    running_days: list[str]
    classes: list[TrainClassAvailability]
    has_pantry: bool = True


class PassengerInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=1, le=120)
    gender: str = Field(pattern=r"^(M|F|O|Male|Female|Other)$")
    berth_preference: Optional[str] = "No Preference"


class TrainBookingCreate(BaseModel):
    train_number: str = Field(min_length=3, max_length=10)
    train_name: str = Field(min_length=1, max_length=160)
    from_station_code: str = Field(min_length=2, max_length=10)
    from_station_name: str = Field(min_length=1, max_length=120)
    to_station_code: str = Field(min_length=2, max_length=10)
    to_station_name: str = Field(min_length=1, max_length=120)
    journey_date: date
    departure_time: str = Field(min_length=3, max_length=10)
    arrival_time: str = Field(min_length=3, max_length=10)
    duration: str = Field(default="", max_length=30)
    travel_class: str = Field(min_length=1, max_length=10)
    quota: str = Field(default="GENERAL", max_length=30)
    passengers: list[PassengerInput] = Field(min_length=1, max_length=6)
    contact_name: str = Field(min_length=2, max_length=160)
    contact_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    contact_phone: str = Field(min_length=5, max_length=60)
    idempotency_key: Optional[str] = Field(default=None, max_length=64)


class TrainBookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_reference: str
    pnr_number: str
    train_number: str
    train_name: str
    from_station_code: str
    from_station_name: str
    to_station_code: str
    to_station_name: str
    journey_date: date
    departure_time: str
    arrival_time: str
    duration: str
    travel_class: str
    quota: str
    passengers: list[dict]
    contact_name: str
    contact_email: str
    contact_phone: str
    base_fare: float
    convenience_fee: float
    gst: float
    total_amount: float
    currency: str
    status: str
    created_at: datetime


class PnrStatusRead(BaseModel):
    pnr_number: str
    train_number: str
    train_name: str
    from_station: str
    to_station: str
    journey_date: str
    travel_class: str
    chart_prepared: bool
    status: str
    passengers: list[dict]


class LiveTrainStatusRead(BaseModel):
    train_number: str
    train_name: str
    current_station: str
    status_message: str
    delay_minutes: int
    last_updated: str
    next_station: str
    estimated_arrival: str


# ---------------------------------------------------------------------------
# Cab / car rental booking
# ---------------------------------------------------------------------------
class CabBookingCreate(BaseModel):
    trip_type: str = Field(pattern=r"^(LOCAL|AIRPORT_TRANSFER|OUTSTATION)$")
    cab_type: str = Field(min_length=1, max_length=40)
    pickup_location: str = Field(min_length=2, max_length=300)
    drop_location: str = Field(min_length=2, max_length=300)
    pickup_date: date
    pickup_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    distance_kms: float = Field(default=0, ge=0, le=5000)
    passengers: int = Field(default=1, ge=1, le=12)
    full_name: str = Field(min_length=2, max_length=160)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    phone: str = Field(min_length=5, max_length=60)
    special_requirements: str = Field(default="", max_length=4000)
    idempotency_key: Optional[str] = Field(default=None, min_length=8, max_length=64)


class CabBookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_reference: str
    trip_type: str
    cab_type: str
    pickup_location: str
    drop_location: str
    pickup_date: date
    pickup_time: str
    distance_kms: float
    passengers: int
    full_name: str
    email: str
    phone: str
    special_requirements: str
    base_fare: float
    convenience_fee: float
    gst: float
    total_amount: float
    currency: str
    status: str
    created_at: datetime


BookingDetail.model_rebuild()
BookingAdminDetail.model_rebuild()
CustomerAdminDetail.model_rebuild()
HotelOwnerRead.model_rebuild()
TrainBookingRead.model_rebuild()
