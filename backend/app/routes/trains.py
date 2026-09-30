"""Train ticket search, PNR lookup, live status, and booking endpoints."""
from datetime import date
import random
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..database import get_db
from ..email_service import send_train_booking_notification_email
from ..train_api import (
    fetch_pnr_status_from_external,
    generate_berth_allocation,
    generate_pnr,
    get_live_train_status,
    lookup_pnr_status,
    search_stations,
    search_stations_external,
    search_trains_between_stations,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Station Search
# ---------------------------------------------------------------------------
@router.get("/stations", response_model=list[schemas.StationInfo])
async def get_stations(q: str = Query(default="", max_length=50)):
    """Search railway stations by code, city, or station name."""
    if q.strip():
        external = await search_stations_external(q.strip())
        if external is not None:
            return external
    return search_stations(q)


# ---------------------------------------------------------------------------
# Search Trains
# ---------------------------------------------------------------------------
@router.get("/search", response_model=list[schemas.TrainScheduleItem])
async def search_trains(
    from_station: str = Query(min_length=2, max_length=10),
    to_station: str = Query(min_length=2, max_length=10),
    journey_date: date = Query(alias="date"),
    _rl: None = Depends(security.rate_limit("search-trains", limit=60, window_seconds=60)),
):
    """Search available trains, classes, live fares, and seat availability."""
    if journey_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Journey date cannot be in the past.",
        )
    return await search_trains_between_stations(from_station, to_station, journey_date)


# ---------------------------------------------------------------------------
# PNR Status Lookup
# ---------------------------------------------------------------------------
@router.get("/pnr/{pnr}", response_model=schemas.PnrStatusRead)
async def get_pnr_status(
    pnr: str,
    db: Session = Depends(get_db),
    _rl: None = Depends(security.rate_limit("pnr-lookup", limit=30, window_seconds=60)),
):
    """Check live PNR status, coach/berth confirmation, and charting details."""
    clean_pnr = pnr.replace("-", "").replace(" ", "").strip()
    res = lookup_pnr_status(db, clean_pnr)
    if not res:
        res = await fetch_pnr_status_from_external(clean_pnr)
    if not res:
        raise HTTPException(status_code=404, detail="PNR not found or invalid format.")
    return res


# ---------------------------------------------------------------------------
# Live Train Running Status
# ---------------------------------------------------------------------------
@router.get("/live/{train_number}", response_model=schemas.LiveTrainStatusRead)
async def get_train_live(
    train_number: str,
    _rl: None = Depends(security.rate_limit("live-train", limit=30, window_seconds=60)),
):
    """Check live running position and delay status of a train."""
    res = await get_live_train_status(train_number)
    if not res:
        raise HTTPException(status_code=404, detail="Live status unavailable for this train.")
    return res


# ---------------------------------------------------------------------------
# Create Train Booking
# ---------------------------------------------------------------------------
@router.post("/bookings", response_model=schemas.TrainBookingRead, status_code=status.HTTP_201_CREATED)
async def create_train_booking(
    data: schemas.TrainBookingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(security.optional_current_user),
    _rl: None = Depends(security.rate_limit("create-train-booking", limit=15, window_seconds=600)),
):
    """Book a train ticket, assign confirmed berths, and send email confirmations."""
    if data.journey_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Journey date must be in the future.",
        )

    # Idempotency check
    if data.idempotency_key:
        existing = db.query(models.TrainBooking).filter(
            models.TrainBooking.idempotency_key == data.idempotency_key
        ).first()
        if existing:
            return existing

    # Find train and fare
    trains = await search_trains_between_stations(
        data.from_station_code, data.to_station_code, data.journey_date
    )
    selected_train = next((t for t in trains if t["train_number"] == data.train_number), None)

    base_single_fare = 1250.0
    if selected_train:
        matched_class = next(
            (c for c in selected_train["classes"] if c["travel_class"].upper() == data.travel_class.upper()),
            None,
        )
        if matched_class:
            base_single_fare = float(matched_class["fare"])

    passenger_count = len(data.passengers)
    base_fare = round(base_single_fare * passenger_count, 2)
    convenience_fee = round(20.0 * passenger_count, 2)
    # GST 5% on AC classes
    is_ac = data.travel_class.upper() in ["1A", "2A", "3A", "3E", "CC", "EC"]
    gst = round(base_fare * 0.05, 2) if is_ac else 0.0
    total_amount = round(base_fare + convenience_fee + gst, 2)

    # Generate reference and PNR
    booking_ref = f"TR-2026-{uuid.uuid4().hex[:8].upper()}"
    pnr = generate_pnr()

    # Assign seats and berths
    allocated_passengers = []
    for idx, p in enumerate(data.passengers):
        seat_berth = generate_berth_allocation(
            data.travel_class, idx, p.berth_preference or "No Preference"
        )
        allocated_passengers.append({
            "name": p.name.strip(),
            "age": p.age,
            "gender": p.gender.upper(),
            "berth_preference": p.berth_preference or "No Preference",
            "seat_number": seat_berth,
            "status": "CNF",
        })

    booking = models.TrainBooking(
        booking_reference=booking_ref,
        pnr_number=pnr,
        user_id=user.id if user else None,
        train_number=data.train_number.strip(),
        train_name=data.train_name.strip(),
        from_station_code=data.from_station_code.strip().upper(),
        from_station_name=data.from_station_name.strip(),
        to_station_code=data.to_station_code.strip().upper(),
        to_station_name=data.to_station_name.strip(),
        journey_date=data.journey_date,
        departure_time=data.departure_time.strip(),
        arrival_time=data.arrival_time.strip(),
        duration=data.duration.strip(),
        travel_class=data.travel_class.strip().upper(),
        quota=data.quota.strip().upper(),
        passengers=allocated_passengers,
        contact_name=data.contact_name.strip(),
        contact_email=data.contact_email.strip().lower(),
        contact_phone=data.contact_phone.strip(),
        base_fare=base_fare,
        convenience_fee=convenience_fee,
        gst=gst,
        total_amount=total_amount,
        currency="INR",
        status="CONFIRMED",
        idempotency_key=data.idempotency_key,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Dispatch notification email in background
    booking_dict = {
        "booking_reference": booking.booking_reference,
        "pnr_number": booking.pnr_number,
        "train_number": booking.train_number,
        "train_name": booking.train_name,
        "from_station_code": booking.from_station_code,
        "from_station_name": booking.from_station_name,
        "to_station_code": booking.to_station_code,
        "to_station_name": booking.to_station_name,
        "journey_date": booking.journey_date,
        "departure_time": booking.departure_time,
        "arrival_time": booking.arrival_time,
        "duration": booking.duration,
        "travel_class": booking.travel_class,
        "quota": booking.quota,
        "passengers": booking.passengers,
        "contact_name": booking.contact_name,
        "contact_email": booking.contact_email,
        "contact_phone": booking.contact_phone,
        "total_amount": float(booking.total_amount),
        "currency": booking.currency,
        "status": booking.status,
    }
    background_tasks.add_task(send_train_booking_notification_email, booking_dict)

    return booking


# ---------------------------------------------------------------------------
# Lookup Booking by Reference
# ---------------------------------------------------------------------------
@router.get("/bookings/reference/{reference}", response_model=schemas.TrainBookingRead)
def get_train_booking_by_reference(
    reference: str,
    db: Session = Depends(get_db),
    _rl: None = Depends(security.rate_limit("lookup-train-booking", limit=30, window_seconds=300)),
):
    """Lookup a train ticket by its booking reference."""
    booking = db.query(models.TrainBooking).filter(
        models.TrainBooking.booking_reference == reference
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Train booking not found.")
    return booking


# ---------------------------------------------------------------------------
# Customer's Train Bookings
# ---------------------------------------------------------------------------
@router.get("/my-bookings", response_model=list[schemas.TrainBookingRead])
def get_my_train_bookings(
    db: Session = Depends(get_db),
    user=Depends(security.get_current_user),
):
    """List all train bookings belonging to the currently authenticated user."""
    return (
        db.query(models.TrainBooking)
        .filter(models.TrainBooking.user_id == user.id)
        .order_by(models.TrainBooking.journey_date.desc())
        .all()
    )
