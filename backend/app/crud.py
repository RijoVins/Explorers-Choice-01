"""CRUD operations for destinations, packages, itineraries, users and bookings."""
from datetime import date, datetime, timedelta, timezone
import re
import secrets

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from . import models, schemas


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
def get_user(db: Session, user_id: int | None = None, email: str | None = None) -> models.User | None:
    query = select(models.User)
    if user_id is not None:
        query = query.where(models.User.id == user_id)
    elif email is not None:
        query = query.where(models.User.email == email)
    else:
        return None
    return db.scalars(query).first()


def create_user(db: Session, data: schemas.UserCreate, password_hash: str) -> models.User:
    if data.requested_role == "HOTEL_OWNER":
        user = models.User(
            email=data.email.strip().lower(),
            password_hash=password_hash,
            full_name=data.full_name.strip(),
            phone=data.phone.strip(),
            country=data.country.strip(),
            role="HOTEL_OWNER",
            requested_role=None,
        )
    else:
        user = models.User(
            email=data.email.strip().lower(),
            password_hash=password_hash,
            full_name=data.full_name.strip(),
            phone=data.phone.strip(),
            country=data.country.strip(),
            requested_role=data.requested_role if data.requested_role != "CUSTOMER" else None,
        )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_provider(
    db: Session, *, provider: str, provider_account_id: str
) -> models.User | None:
    return db.scalars(
        select(models.User).where(
            models.User.auth_provider == provider,
            models.User.provider_account_id == provider_account_id,
        )
    ).first()


def create_google_user(
    db: Session, *, email: str, full_name: str, provider_account_id: str
) -> models.User:
    """Create a new account purely authenticated via Google (no password)."""
    user = models.User(
        email=email.strip().lower(),
        password_hash=None,
        full_name=(full_name or "").strip(),
        auth_provider="GOOGLE",
        provider_account_id=provider_account_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def link_google_account(
    db: Session, user: models.User, provider_account_id: str
) -> models.User:
    """Attach a Google identity to an existing account (auto account linking)."""
    user.auth_provider = "GOOGLE"
    user.provider_account_id = provider_account_id
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: models.User, data: schemas.ProfileUpdate) -> models.User:
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: models.User) -> None:
    """Permanently delete a user account.

    Related rows that reference the user are detached first (their foreign keys
    are SET NULL), while the user's own records such as reset tokens are removed.
    """
    uid = user.id
    db.execute(update(models.Booking).where(models.Booking.user_id == uid).values(user_id=None))
    db.execute(update(models.BookingNote).where(models.BookingNote.user_id == uid).values(user_id=None))
    db.execute(update(models.Enquiry).where(models.Enquiry.assigned_staff_id == uid).values(assigned_staff_id=None))
    db.execute(update(models.AuditLog).where(models.AuditLog.user_id == uid).values(user_id=None))
    db.execute(update(models.Setting).where(models.Setting.updated_by == uid).values(updated_by=None))
    db.execute(delete(models.PasswordResetToken).where(models.PasswordResetToken.user_id == uid))
    db.delete(user)
    db.commit()


def create_password_reset(db: Session, user: models.User, token_hash: str) -> models.PasswordResetToken:
    record = models.PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(record)
    db.commit()
    return record


def get_valid_reset_token(db: Session, token_hash: str) -> models.PasswordResetToken | None:
    now = datetime.now(timezone.utc)
    return db.scalars(
        select(models.PasswordResetToken)
        .where(
            models.PasswordResetToken.token_hash == token_hash,
            models.PasswordResetToken.used_at.is_(None),
            models.PasswordResetToken.expires_at > now,
        )
    ).first()


def mark_reset_token_used(db: Session, record: models.PasswordResetToken) -> None:
    record.used_at = datetime.now(timezone.utc)
    db.commit()


def set_user_password(db: Session, user: models.User, password_hash: str) -> None:
    user.password_hash = password_hash
    user.token_version = (user.token_version or 0) + 1
    db.commit()


def reset_user_password(
    db: Session, record: models.PasswordResetToken, user: models.User, password_hash: str
) -> None:
    """Mark the token used and change the password in a single transaction."""
    record.used_at = datetime.now(timezone.utc)
    user.password_hash = password_hash
    user.token_version = (user.token_version or 0) + 1
    db.commit()


# ---------------------------------------------------------------------------
# Destinations
# ---------------------------------------------------------------------------
def list_destinations(db: Session, *, active_only: bool = True, featured_only: bool = False):
    query = select(models.Destination).order_by(models.Destination.name)
    if active_only:
        query = query.where(models.Destination.is_active.is_(True))
    if featured_only:
        query = query.where(models.Destination.is_featured.is_(True))
    return db.scalars(query).all()


def get_destination(db: Session, destination_id: int | None = None, slug: str | None = None):
    query = select(models.Destination)
    if destination_id is not None:
        query = query.where(models.Destination.id == destination_id)
    elif slug is not None:
        query = query.where(models.Destination.slug == slug)
    else:
        return None
    return db.scalars(query).first()


def create_destination(db: Session, data: schemas.DestinationCreate) -> models.Destination:
    destination = models.Destination(**data.model_dump())
    db.add(destination)
    db.commit()
    db.refresh(destination)
    return destination


def update_destination(
    db: Session, destination: models.Destination, data: schemas.DestinationUpdate
) -> models.Destination:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(destination, field, value)
    db.commit()
    db.refresh(destination)
    return destination


def delete_destination(db: Session, destination: models.Destination, *, hard: bool = False) -> None:
    if hard:
        db.delete(destination)
        db.commit()
    else:
        destination.is_active = False
        db.commit()


# ---------------------------------------------------------------------------
# Packages
# ---------------------------------------------------------------------------
def _package_base_query():
    return select(models.Package).options(
        selectinload(models.Package.destination),
        selectinload(models.Package.itinerary),
        selectinload(models.Package.faqs),
    )


def list_packages(db: Session, *, active_only: bool = True, featured_only: bool = False):
    query = _package_base_query().order_by(models.Package.name)
    if active_only:
        query = query.where(models.Package.is_active.is_(True))
    if featured_only:
        query = query.where(models.Package.is_featured.is_(True))
    return db.scalars(query).unique().all()


def get_package(
    db: Session, package_id: int | None = None, slug: str | None = None
) -> models.Package | None:
    query = _package_base_query()
    if package_id is not None:
        query = query.where(models.Package.id == package_id)
    elif slug is not None:
        query = query.where(models.Package.slug == slug)
    else:
        return None
    return db.scalars(query).unique().first()


def get_packages_by_destination(db: Session, destination_id: int, *, active_only: bool = True):
    query = _package_base_query().where(models.Package.destination_id == destination_id)
    if active_only:
        query = query.where(models.Package.is_active.is_(True))
    return db.scalars(query).unique().all()


def create_package(db: Session, data: schemas.PackageCreate) -> models.Package:
    payload = data.model_dump(exclude={"itinerary", "faqs"})
    package = models.Package(**payload)
    package.itinerary = [
        models.ItineraryDay(**day.model_dump()) for day in data.itinerary
    ]
    package.faqs = [
        models.PackageFaq(**faq.model_dump()) for faq in data.faqs
    ]
    db.add(package)
    db.commit()
    return get_package(db, package_id=package.id)


def update_package(
    db: Session, package: models.Package, data: schemas.PackageUpdate
) -> models.Package:
    payload = data.model_dump(exclude_unset=True, exclude={"itinerary", "faqs"})
    for field, value in payload.items():
        setattr(package, field, value)
    db.commit()
    return get_package(db, package_id=package.id)


def delete_package(db: Session, package: models.Package, *, hard: bool = False) -> None:
    if hard:
        db.delete(package)
        db.commit()
    else:
        package.is_active = False
        db.commit()


def upsert_itinerary_days(
    db: Session, package: models.Package, days: list[schemas.ItineraryDayCreate]
) -> list[models.ItineraryDay]:
    """Replace all itinerary days for a package in one operation."""
    if days is None:
        return package.itinerary
    for existing in list(package.itinerary):
        db.delete(existing)
    db.flush()
    new_days = [models.ItineraryDay(**day.model_dump()) for day in days]
    package.itinerary = new_days
    db.commit()
    return get_package(db, package_id=package.id).itinerary


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------
def generate_booking_reference(db: Session) -> str:
    """Generate a public, non-sequential booking reference."""
    while True:
        reference = f"EC-{date.today().year}-{secrets.token_hex(6).upper()}"
        exists = db.scalar(select(models.Booking.id).where(models.Booking.booking_reference == reference))
        if exists is None:
            return reference


def create_booking(
    db: Session, data: schemas.BookingCreate, user_id: int | None = None
) -> models.Booking | None:
    # BUG-18: if an idempotency key was supplied and a booking already exists
    # for it, return that booking instead of creating a duplicate.
    idem_key = getattr(data, "idempotency_key", None)
    if idem_key:
        existing = db.scalars(
            select(models.Booking).where(models.Booking.idempotency_key == idem_key)
        ).first()
        if existing is not None:
            return existing

    package = get_package(db, slug=data.package_slug)
    if package is None or not package.is_active or not package.destination.is_active:
        return None

    subtotal = round(float(package.starting_price) * (data.adults + data.children), 2)
    taxes = 0.0
    booking_mode = package.booking_mode
    status = "PAYMENT_PENDING" if booking_mode == "INSTANT_BOOKING" else "PENDING_CONFIRMATION"
    payment_status = "PENDING" if booking_mode == "INSTANT_BOOKING" else "NOT_REQUIRED"
    booking = models.Booking(
        booking_reference=generate_booking_reference(db),
        user_id=user_id,
        package_id=package.id,
        travel_date=data.travel_date,
        adults=data.adults,
        children=data.children,
        infants=data.infants,
        departure_information=data.departure_information.strip(),
        full_name=(data.full_name or "").strip(),
        email=(data.email or "").strip().lower(),
        phone=(data.phone or "").strip(),
        country=(data.country or "").strip(),
        special_requirements=data.special_requirements.strip(),
        notes=data.notes.strip(),
        subtotal=subtotal,
        taxes=taxes,
        total=round(subtotal + taxes, 2),
        currency=package.currency.upper(),
        status=status,
        payment_status=payment_status,
        package_name=package.name,
        destination_name=package.destination.name,
        duration_days=package.duration_days,
        booking_mode=booking_mode,
        idempotency_key=idem_key,
    )
    booking.travellers = [
        models.BookingTraveller(traveller_type="ADULT", quantity=data.adults),
        models.BookingTraveller(traveller_type="CHILD", quantity=data.children),
        models.BookingTraveller(traveller_type="INFANT", quantity=data.infants),
    ]
    db.add(booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # BUG-18: a concurrent retry with the same idempotency key won the race.
        # Return the already-created booking rather than creating a duplicate.
        if idem_key:
            existing = db.scalars(
                select(models.Booking).where(models.Booking.idempotency_key == idem_key)
            ).first()
            if existing is not None:
                return existing
        # Otherwise this is a reference collision under concurrent creation;
        # retry with a fresh reference (extremely unlikely: 48 bits of entropy).
        booking.booking_reference = generate_booking_reference(db)
        db.add(booking)
        db.commit()
    db.refresh(booking)
    return booking


def list_bookings(
    db: Session, *, user_id: int | None = None, admin_view: bool = False, booking_status: str | None = None
) -> list[models.Booking]:
    query = select(models.Booking).order_by(models.Booking.travel_date.asc(), models.Booking.created_at.desc())
    if admin_view:
        if booking_status:
            query = query.where(models.Booking.status == booking_status)
    elif user_id is not None:
        query = query.where(models.Booking.user_id == user_id)
    return db.scalars(query).all()


def get_booking(db: Session, booking_id: int) -> models.Booking | None:
    return db.get(models.Booking, booking_id)


def get_booking_by_reference(db: Session, reference: str) -> models.Booking | None:
    return db.scalars(
        select(models.Booking).where(models.Booking.booking_reference == reference)
    ).first()


def update_booking_status(
    db: Session, booking: models.Booking, data: schemas.BookingStatusUpdate, actor: models.User | None = None
) -> models.Booking:
    booking.status = data.status
    # BUG-05: the general booking PATCH must NOT accept payment_status changes.
    # Only the dedicated /payment endpoint (restricted to FINANCE roles) may do that.
    # data.payment_status is intentionally ignored here.
    db.commit()
    db.refresh(booking)
    audit(db, user=actor, action="updated booking", entity="booking", entity_id=booking.booking_reference,
          details=f"status → {booking.status}")
    return booking


def update_booking_payment_status(
    db: Session, booking: models.Booking, payment_status: str, actor: models.User | None = None
) -> models.Booking:
    booking.payment_status = payment_status
    db.commit()
    db.refresh(booking)
    audit(db, user=actor, action="updated payment status", entity="booking",
          entity_id=booking.booking_reference, details=payment_status)
    return booking


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------
def list_payments(db: Session, booking_id: int) -> list[models.Payment]:
    return db.scalars(select(models.Payment).where(models.Payment.booking_id == booking_id).order_by(models.Payment.created_at.asc())).all()


def get_payment(db: Session, payment_id: int) -> models.Payment | None:
    return db.get(models.Payment, payment_id)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
def list_documents(db: Session, booking_id: int) -> list[models.BookingDocument]:
    return db.scalars(
        select(models.BookingDocument).where(models.BookingDocument.booking_id == booking_id).order_by(models.BookingDocument.created_at.desc())
    ).all()


def get_document(db: Session, document_id: int, *, booking_id: int | None = None) -> models.BookingDocument | None:
    query = select(models.BookingDocument).where(models.BookingDocument.id == document_id)
    if booking_id is not None:
        query = query.where(models.BookingDocument.booking_id == booking_id)
    return db.scalars(query).first()


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------
def audit(
    db: Session,
    *,
    user: models.User | None,
    action: str,
    entity: str,
    entity_id: str = "",
    details: str = "",
) -> models.AuditLog:
    record = models.AuditLog(
        user_id=user.id if user else None,
        username=user.email if user else "",
        action=action,
        entity=entity,
        entity_id=entity_id or "",
        details=details or "",
    )
    db.add(record)
    db.commit()
    return record


def list_audit_logs(db: Session, *, limit: int = 60) -> list[models.AuditLog]:
    return db.scalars(
        select(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(limit)
    ).all()


# ---------------------------------------------------------------------------
# Staff
# ---------------------------------------------------------------------------
def create_staff(db: Session, data: schemas.StaffCreate, password_hash: str) -> models.User:
    user = models.User(
        email=data.email.strip().lower(),
        password_hash=password_hash,
        full_name=data.full_name.strip(),
        phone=data.phone.strip(),
        country=data.country.strip(),
        role=data.role,
        is_staff=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_staff(db: Session) -> list[models.User]:
    return db.scalars(
        select(models.User).where(models.User.is_staff.is_(True)).order_by(models.User.full_name)
    ).all()


def update_staff(db: Session, staff: models.User, data: schemas.StaffUpdate) -> models.User:
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(staff, field, value)
    if data.role is not None:
        staff.role = data.role
        staff.is_staff = data.role != "CUSTOMER"
        staff.requested_role = None
    db.commit()
    db.refresh(staff)
    return staff


def list_staff_for_assign(db: Session) -> list[models.User]:
    return db.scalars(select(models.User).where(models.User.is_staff.is_(True))).all()


# ---------------------------------------------------------------------------
# Enquiries (CRM)
# ---------------------------------------------------------------------------
ENQUIRY_STAGES = ["NEW", "CONTACTED", "REQUIREMENTS_COLLECTED", "PLANNING", "QUOTE_SENT", "NEGOTIATION", "WON", "LOST"]


def list_enquiries(db: Session, *, status: str | None = None, assigned_staff_id: int | None = None, limit: int = 300) -> list[models.Enquiry]:
    query = select(models.Enquiry).order_by(models.Enquiry.created_at.desc()).limit(limit)
    if status:
        query = query.where(models.Enquiry.status == status)
    if assigned_staff_id:
        query = query.where(models.Enquiry.assigned_staff_id == assigned_staff_id)
    return db.scalars(query).all()


def get_enquiry(db: Session, enquiry_id: int) -> models.Enquiry | None:
    return db.get(models.Enquiry, enquiry_id)


def create_enquiry(db: Session, data: schemas.EnquiryCreate, actor: models.User | None = None) -> models.Enquiry:
    payload = data.model_dump()
    if payload.get("package_id"):
        package = get_package(db, package_id=payload["package_id"])
        if package:
            payload["package_name"] = package.name
            payload.setdefault("destination_interest", payload.get("destination_interest") or package.destination.name)
    enquiry = models.Enquiry(**payload)
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    audit(db, user=actor, action="created enquiry", entity="enquiry", entity_id=str(enquiry.id), details=enquiry.customer_name)
    return enquiry


def update_enquiry(db: Session, enquiry: models.Enquiry, data: schemas.EnquiryUpdate, actor: models.User | None = None) -> models.Enquiry:
    payload = data.model_dump(exclude_unset=True)
    if payload.get("package_id"):
        package = get_package(db, package_id=payload["package_id"])
        if package:
            payload["package_name"] = package.name
    for field, value in payload.items():
        if value is not None:
            setattr(enquiry, field, value)
    db.commit()
    db.refresh(enquiry)
    audit(db, user=actor, action="updated enquiry", entity="enquiry", entity_id=str(enquiry.id), details=f"status → {enquiry.status}")
    return enquiry


def delete_enquiry(db: Session, enquiry: models.Enquiry) -> None:
    db.delete(enquiry)
    db.commit()


# ---------------------------------------------------------------------------
# Customer stories
# ---------------------------------------------------------------------------
def list_customer_stories(db: Session, *, published_only: bool = False) -> list[models.CustomerStory]:
    query = select(models.CustomerStory).order_by(models.CustomerStory.created_at.desc())
    if published_only:
        query = query.where(models.CustomerStory.is_published.is_(True))
    return db.scalars(query).all()


def get_customer_story(db: Session, story_id: int) -> models.CustomerStory | None:
    return db.get(models.CustomerStory, story_id)


def create_customer_story(db: Session, data: schemas.CustomerStoryCreate, actor: models.User | None = None) -> models.CustomerStory:
    payload = data.model_dump()
    if payload.get("package_id"):
        package = get_package(db, package_id=payload["package_id"])
        if package:
            payload["package_name"] = package.name
    story = models.CustomerStory(**payload)
    db.add(story)
    db.commit()
    db.refresh(story)
    audit(db, user=actor, action="created customer story", entity="customer_story", entity_id=str(story.id))
    return story


def update_customer_story(db: Session, story: models.CustomerStory, data: schemas.CustomerStoryUpdate, actor: models.User | None = None) -> models.CustomerStory:
    payload = data.model_dump(exclude_unset=True)
    if payload.get("package_id"):
        package = get_package(db, package_id=payload["package_id"])
        if package:
            payload["package_name"] = package.name
    for field, value in payload.items():
        if value is not None:
            setattr(story, field, value)
    db.commit()
    db.refresh(story)
    audit(db, user=actor, action="updated customer story", entity="customer_story", entity_id=str(story.id))
    return story


def delete_customer_story(db: Session, story: models.CustomerStory, actor: models.User | None = None) -> None:
    story_id = story.id
    db.delete(story)
    db.commit()
    audit(db, user=actor, action="deleted customer story", entity="customer_story", entity_id=str(story_id))


# ---------------------------------------------------------------------------
# Offers
# ---------------------------------------------------------------------------
def list_offers(db: Session, *, active_only: bool = False) -> list[models.Offer]:
    query = select(models.Offer).order_by(models.Offer.created_at.desc())
    if active_only:
        query = query.where(models.Offer.is_active.is_(True))
    return db.scalars(query).all()


def get_offer(db: Session, offer_id: int) -> models.Offer | None:
    return db.get(models.Offer, offer_id)


def create_offer(db: Session, data: schemas.OfferCreate, actor: models.User | None = None) -> models.Offer:
    payload = data.model_dump()
    if payload.get("package_id"):
        package = get_package(db, package_id=payload["package_id"])
        if package:
            payload["package_name"] = package.name
    offer = models.Offer(**payload)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    audit(db, user=actor, action="created offer", entity="offer", entity_id=str(offer.id), details=offer.title)
    return offer


def update_offer(db: Session, offer: models.Offer, data: schemas.OfferUpdate, actor: models.User | None = None) -> models.Offer:
    payload = data.model_dump(exclude_unset=True)
    if payload.get("package_id"):
        package = get_package(db, package_id=payload["package_id"])
        if package:
            payload["package_name"] = package.name
    for field, value in payload.items():
        if value is not None:
            setattr(offer, field, value)
    db.commit()
    db.refresh(offer)
    audit(db, user=actor, action="updated offer", entity="offer", entity_id=str(offer.id))
    return offer


def delete_offer(db: Session, offer: models.Offer, actor: models.User | None = None) -> None:
    offer_id = offer.id
    db.delete(offer)
    db.commit()
    audit(db, user=actor, action="deleted offer", entity="offer", entity_id=str(offer_id))


# ---------------------------------------------------------------------------
# Booking notes + documents + payments (operations)
# ---------------------------------------------------------------------------
def list_booking_notes(db: Session, booking_id: int) -> list[models.BookingNote]:
    return list(
        db.scalars(
            select(models.BookingNote)
            .options(selectinload(models.BookingNote.author))
            .where(models.BookingNote.booking_id == booking_id)
            .order_by(models.BookingNote.created_at.desc())
        ).all()
    )


def add_booking_note(db: Session, booking_id: int, body: str, actor: models.User | None = None) -> models.BookingNote:
    note = models.BookingNote(booking_id=booking_id, user_id=actor.id if actor else None, body=body.strip())
    db.add(note)
    db.commit()
    db.refresh(note)
    audit(db, user=actor, action="added note", entity="booking", entity_id=str(booking_id))
    return note


def _reconcile_payment_status(db: Session, booking: models.Booking) -> None:
    """BUG-06: Derive and apply booking.payment_status from its payment ledger.

    Rules:
    - If any payment row is PAID and covers the full booking total → PAID.
    - If some amount is paid but not the full total → PARTIALLY_PAID.
    - If all payments failed or were refunded → FAILED / REFUNDED.
    - Otherwise → PENDING.
    Does not change bookings that have payment_status NOT_REQUIRED.
    """
    if booking.payment_status == "NOT_REQUIRED":
        return
    payments = db.scalars(
        select(models.Payment).where(models.Payment.booking_id == booking.id)
    ).all()
    paid_total = sum(float(p.amount) for p in payments if p.status == "PAID")
    booking_total = float(booking.total or 0)
    has_refunded = any(p.status == "REFUNDED" for p in payments)
    has_failed = any(p.status == "FAILED" for p in payments)
    if booking_total > 0 and paid_total >= booking_total:
        booking.payment_status = "PAID"
    elif paid_total > 0:
        booking.payment_status = "PARTIALLY_PAID"
    elif has_refunded and paid_total == 0:
        booking.payment_status = "REFUNDED"
    elif has_failed and paid_total == 0:
        booking.payment_status = "FAILED"
    else:
        booking.payment_status = "PENDING"
    # Commit is handled by the caller.


def add_payment(db: Session, data: schemas.ManualPaymentCreate, actor: models.User | None = None) -> models.Payment:
    booking = get_booking(db, data.booking_id)
    if booking is None:
        raise ValueError(f"Booking {data.booking_id} not found")
    # BUG-02: always inherit currency from the booking; reject mismatches.
    currency = booking.currency.upper()
    if data.currency is not None and data.currency.upper() != currency:
        raise ValueError(
            f"Payment currency {data.currency.upper()} does not match booking currency {currency}."
        )
    payment = models.Payment(
        booking_id=data.booking_id,
        amount=data.amount,
        currency=currency,
        status=data.status,
        provider=data.provider,
        provider_reference=data.provider_reference,
    )
    db.add(payment)
    db.flush()  # get payment.id without committing yet
    # BUG-06: reconcile booking payment status inside the same transaction.
    _reconcile_payment_status(db, booking)
    db.commit()
    db.refresh(payment)
    audit(db, user=actor, action="recorded payment", entity="booking", entity_id=str(data.booking_id), details=f"{data.amount} {currency}")
    return payment


def update_payment_status(db: Session, payment: models.Payment, data: schemas.PaymentUpdate, actor: models.User | None = None) -> models.Payment:
    payment.status = data.status
    if data.provider_reference is not None:
        payment.provider_reference = data.provider_reference
    # BUG-06: reconcile booking payment status inside the same transaction.
    booking = get_booking(db, payment.booking_id)
    if booking is not None:
        _reconcile_payment_status(db, booking)
    db.commit()
    db.refresh(payment)
    audit(db, user=actor, action="updated payment", entity="booking", entity_id=str(payment.booking_id), details=f"payment {payment.id} → {payment.status}")
    return payment


def add_document(db: Session, booking_id: int, document_type: str, title: str, file_name: str, file_path: str, actor: models.User | None = None) -> models.BookingDocument:
    document = models.BookingDocument(
        booking_id=booking_id,
        document_type=document_type,
        title=title.strip(),
        file_name=file_name,
        file_path=file_path,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    audit(db, user=actor, action="attached document", entity="booking", entity_id=str(booking_id), details=f"{title} ({document_type})")
    return document


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
def get_setting(db: Session, key: str, default: dict | None = None) -> dict:
    record = db.scalar(select(models.Setting).where(models.Setting.key == key))
    return record.value if record else default


def list_settings(db: Session) -> list[models.Setting]:
    return db.scalars(select(models.Setting).order_by(models.Setting.key)).all()


def set_setting(db: Session, key: str, value: dict, actor: models.User | None = None) -> models.Setting:
    record = db.scalar(select(models.Setting).where(models.Setting.key == key))
    if record is None:
        record = models.Setting(key=key, value=value, updated_by=actor.id if actor else None)
        db.add(record)
    else:
        record.value = value
        record.updated_by = actor.id if actor else None
    db.commit()
    db.refresh(record)
    return record


# ---------------------------------------------------------------------------
# Dashboard + customers (admin)
# ---------------------------------------------------------------------------
def dashboard_metrics(db: Session) -> dict:
    today = date.today()
    in_30 = today + timedelta(days=30)
    from sqlalchemy import func

    status_counts = dict(
        db.execute(
            select(models.Booking.status, func.count(models.Booking.id))
            .group_by(models.Booking.status)
        ).all()
    )
    new_enquiries = db.scalar(
        select(func.count(models.Enquiry.id)).where(models.Enquiry.status == "NEW")
    ) or 0
    pending = sum(status_counts.get(s, 0) for s in ("PENDING", "PENDING_CONFIRMATION"))
    confirmed = status_counts.get("CONFIRMED", 0)
    upcoming = db.scalar(
        select(func.count(models.Booking.id)).where(
            models.Booking.travel_date.between(today, in_30),
            models.Booking.status.in_(("CONFIRMED", "PAID", "PAYMENT_PENDING", "UPCOMING")),
        )
    ) or 0
    total_bookings = sum(status_counts.values())

    departures = db.scalars(
        select(models.Booking).where(
            models.Booking.travel_date.between(today, in_30),
            models.Booking.status.notin_(("CANCELLED", "COMPLETED")),
        ).order_by(models.Booking.travel_date.asc()).limit(6)
    ).all()
    followups = db.scalars(
        select(models.Enquiry).where(models.Enquiry.next_action_at.isnot(None)).order_by(models.Enquiry.next_action_at.asc()).limit(6)
    ).all()
    actions = []
    for b in departures:
        actions.append({
            "kind": "booking_departure",
            "id": b.id,
            "title": f"{b.destination_name} departs {b.travel_date.isoformat()}",
            "when": b.travel_date.isoformat(),
            "href": f"/admin/bookings/{b.id}",
        })
    for e in followups[:3]:
        if e.next_action_at and e.next_action_at <= in_30:
            actions.append({
                "kind": "enquiry_followup",
                "id": e.id,
                "title": f"{e.customer_name} — {e.next_action or 'follow up'}",
                "when": e.next_action_at.isoformat(),
                "href": f"/admin/enquiries/{e.id}",
            })
    actions = actions[:8]

    recent_payments = db.scalars(
        select(models.Payment).options(selectinload(models.Payment.booking)).order_by(models.Payment.created_at.desc()).limit(6)
    ).all()
    recent_customers = db.scalars(
        select(models.User).order_by(models.User.created_at.desc()).limit(6)
    ).all()

    return {
        "new_enquiries": new_enquiries,
        "pending_bookings": pending,
        "confirmed_bookings": confirmed,
        "upcoming_trips": upcoming,
        "total_bookings": total_bookings,
        "today_actions": actions,
        "recent_payments": [
            {"booking_ref": p.booking.booking_reference, "amount": float(p.amount), "currency": p.currency,
             "status": p.status, "created_at": p.created_at}
            for p in recent_payments
        ],
        "recent_customers": [
            {"id": u.id, "name": u.full_name or u.email, "email": u.email, "last_activity": u.updated_at}
            for u in recent_customers
        ],
        "booking_status_counts": {k: v for k, v in status_counts.items()},
    }


def list_customers(db: Session, *, limit: int = 200) -> list[models.User]:
    return list(
        db.scalars(
            select(models.User)
            .options(selectinload(models.User.bookings))
            .where(models.User.role == "CUSTOMER")
            .order_by(models.User.created_at.desc())
            .limit(limit)
        ).all()
    )


def get_customer_detail(db: Session, user_id: int) -> models.User | None:
    user = db.get(models.User, user_id)
    if user is None or user.role != "CUSTOMER":
        return None
    user.bookings = list(
        db.scalars(
            select(models.Booking)
            .options(
                selectinload(models.Booking.payments),
                selectinload(models.Booking.documents),
                selectinload(models.Booking.travellers),
                selectinload(models.Booking.internal_notes),
            )
            .where(models.Booking.user_id == user_id)
            .order_by(models.Booking.created_at.desc())
        ).all()
    )
    user.enquiries = db.scalars(
        select(models.Enquiry).where(models.Enquiry.email == user.email).order_by(models.Enquiry.created_at.desc())
    ).all()
    return user


def list_all_documents(db: Session) -> list[models.BookingDocument]:
    return db.scalars(
        select(models.BookingDocument).order_by(models.BookingDocument.created_at.desc()).limit(200)
    ).all()


# ---------------------------------------------------------------------------
# Hotels (hotel owner listings)
# ---------------------------------------------------------------------------
def slugify(value: str) -> str:
    """Best-effort slug from a natural language name."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:120]


def _unique_hotel_slug(db: Session, base: str) -> str:
    clean = slugify(base) or "hotel"
    candidate = clean
    n = 2
    while get_hotel_by_slug(db, candidate) is not None:
        candidate = f"{clean}-{n}"
        n += 1
        if n > 500:
            candidate = f"{clean}-{secrets.token_hex(3)}"
            break
    return candidate


def get_hotel(db: Session, hotel_id: int) -> models.Hotel | None:
    return db.get(models.Hotel, hotel_id)


def get_hotel_by_slug(db: Session, slug: str) -> models.Hotel | None:
    return db.scalars(
        select(models.Hotel).where(models.Hotel.slug == slug)
    ).first()


def list_owner_hotels(db: Session, owner_id: int) -> list[models.Hotel]:
    return db.scalars(
        select(models.Hotel)
        .where(models.Hotel.owner_id == owner_id)
        .order_by(models.Hotel.created_at.desc())
    ).all()


def list_published_hotels(db: Session) -> list[models.Hotel]:
    return db.scalars(
        select(models.Hotel)
        .where(models.Hotel.is_published.is_(True))
        .order_by(models.Hotel.created_at.desc())
    ).all()


def list_all_hotels(db: Session) -> list[models.Hotel]:
    return db.scalars(
        select(models.Hotel).order_by(models.Hotel.created_at.desc())
    ).all()


def create_hotel(db: Session, owner_id: int, data: schemas.HotelCreate) -> models.Hotel:
    hotel = models.Hotel(
        owner_id=owner_id,
        slug=_unique_hotel_slug(db, data.name),
        name=data.name.strip(),
        location=data.location.strip(),
        destination=data.destination.strip(),
        tagline=data.tagline.strip(),
        description=data.description.strip(),
        image=data.image.strip(),
        price_per_night=data.price_per_night,
        currency=data.currency.strip().upper() or "INR",
        amenities=[a.strip() for a in data.amenities if a.strip()],
        highlights=[h.strip() for h in data.highlights if h.strip()],
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return hotel


def create_admin_hotel(
    db: Session, actor_id: int, data: schemas.AdminHotelCreate
) -> models.Hotel:
    """Create a hotel on behalf of an admin; assigns an explicit owner when given."""
    hotel = models.Hotel(
        owner_id=data.owner_id or actor_id,
        slug=_unique_hotel_slug(db, data.name),
        name=data.name.strip(),
        location=data.location.strip(),
        destination=data.destination.strip(),
        tagline=data.tagline.strip(),
        description=data.description.strip(),
        image=data.image.strip(),
        price_per_night=data.price_per_night,
        currency=data.currency.strip().upper() or "INR",
        amenities=[a.strip() for a in data.amenities if a.strip()],
        highlights=[h.strip() for h in data.highlights if h.strip()],
        is_published=data.is_published,
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return hotel


def update_hotel(db: Session, hotel: models.Hotel, data: schemas.HotelUpdate) -> models.Hotel:
    patch = data.model_dump(exclude_unset=True)
    if "name" in patch and patch["name"]:
        hotel.slug = _unique_hotel_slug(db, patch["name"])
    for field, value in patch.items():
        if field == "currency" and value:
            value = value.strip().upper() or "INR"
        if field in ("amenities", "highlights") and value is not None:
            value = [item.strip() for item in value if item.strip()]
        setattr(hotel, field, value)
    db.commit()
    db.refresh(hotel)
    return hotel


def delete_hotel(db: Session, hotel: models.Hotel) -> None:
    db.delete(hotel)
    db.commit()