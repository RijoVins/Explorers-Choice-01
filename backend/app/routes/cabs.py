"""Cab / car rental booking endpoints.

Customers place a booking request with their route and requirements. An
immediate email notification is sent to the admin
(infoexplorerschoice@gmail.com by default) and a copy is sent to the customer.
Bookings are stored as requests to be quoted and confirmed by the Explorers
Choice team.
"""
from datetime import date
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..database import get_db
from ..email_service import send_cab_booking_notification_email

router = APIRouter()


@router.post("/bookings", response_model=schemas.CabBookingRead, status_code=status.HTTP_201_CREATED)
def create_cab_booking(
    data: schemas.CabBookingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(security.optional_current_user),
    _rl: None = Depends(security.rate_limit("create-cab-booking", limit=15, window_seconds=600)),
):
    """Place a cab booking request and notify the admin by email."""
    if data.pickup_date <= date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pickup date must be in the future.",
        )

    # Idempotency check to prevent duplicate bookings on retry
    if data.idempotency_key:
        existing = db.query(models.CabBooking).filter(
            models.CabBooking.idempotency_key == data.idempotency_key
        ).first()
        if existing:
            return existing

    booking_ref = f"CB-2026-{uuid.uuid4().hex[:8].upper()}"

    # Quote-based pricing: fares are set to zero and confirmed by the Explorers
    # Choice team after the request is received.
    booking = models.CabBooking(
        booking_reference=booking_ref,
        user_id=user.id if user else None,
        trip_type=data.trip_type,
        cab_type=data.cab_type.strip(),
        pickup_location=data.pickup_location.strip(),
        drop_location=data.drop_location.strip(),
        pickup_date=data.pickup_date,
        pickup_time=data.pickup_time,
        distance_kms=data.distance_kms,
        passengers=data.passengers,
        full_name=data.full_name.strip(),
        email=data.email.strip().lower(),
        phone=data.phone.strip(),
        special_requirements=data.special_requirements,
        base_fare=0,
        convenience_fee=0,
        gst=0,
        total_amount=0,
        currency="INR",
        status="PENDING_CONFIRMATION",
        idempotency_key=data.idempotency_key,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    booking_dict = {
        "booking_reference": booking.booking_reference,
        "trip_type": booking.trip_type,
        "cab_type": booking.cab_type,
        "pickup_location": booking.pickup_location,
        "drop_location": booking.drop_location,
        "pickup_date": booking.pickup_date,
        "pickup_time": booking.pickup_time,
        "distance_kms": float(booking.distance_kms),
        "passengers": booking.passengers,
        "full_name": booking.full_name,
        "email": booking.email,
        "phone": booking.phone,
        "special_requirements": booking.special_requirements,
        "base_fare": float(booking.base_fare),
        "convenience_fee": float(booking.convenience_fee),
        "gst": float(booking.gst),
        "total_amount": float(booking.total_amount),
        "currency": booking.currency,
        "status": booking.status,
    }
    background_tasks.add_task(send_cab_booking_notification_email, booking_dict)

    return booking


@router.get("/bookings/reference/{reference}", response_model=schemas.CabBookingRead)
def get_cab_booking_by_reference(
    reference: str,
    db: Session = Depends(get_db),
    _rl: None = Depends(security.rate_limit("lookup-cab-booking", limit=30, window_seconds=300)),
):
    """Lookup a cab booking by its booking reference."""
    booking = db.query(models.CabBooking).filter(
        models.CabBooking.booking_reference == reference
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Cab booking not found.")
    return booking


@router.get("/my-bookings", response_model=list[schemas.CabBookingRead])
def get_my_cab_bookings(
    db: Session = Depends(get_db),
    user=Depends(security.get_current_user),
):
    """List all cab bookings belonging to the currently authenticated user."""
    return (
        db.query(models.CabBooking)
        .filter(models.CabBooking.user_id == user.id)
        .order_by(models.CabBooking.pickup_date.desc())
        .all()
    )