"""Staff operations API: dashboard, CRM, customers, payments, documents,
offers, stories, staff management, settings and the audit log.

Every endpoint is protected with role-based access control tied to the
session cookie; CUSTOMER accounts receive 403/401. Package, destination,
itinerary and booking management live in their own routers.
"""
import os
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, models, schemas, security
from ..database import get_db
from ..security import require_admin, require_roles

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "booking_docs"
ALLOWED_DOC_TYPES = {"invoice", "hotel_voucher", "confirmation", "travel_docs"}

AGENT_OR_ABOVE = ("TRAVEL_AGENT", "MANAGER", "ADMIN")
FINANCE = ("ACCOUNTANT", "MANAGER", "ADMIN")
CONTENT = ("MANAGER", "ADMIN")


def _safe_stem(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", Path(name).name)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@router.get("/dashboard", response_model=schemas.AdminDashboardRead)
def admin_dashboard(db: Session = Depends(get_db), user=Depends(require_admin)):
    return crud.dashboard_metrics(db)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------
@router.get("/customers", response_model=list[schemas.CustomerAdminRead])
def admin_customers(db: Session = Depends(get_db), user=Depends(require_admin)):
    customers = crud.list_customers(db)
    enquiry_counts = {
        email.lower(): count
        for email, count in db.execute(
            select(models.Enquiry.email, func.count(models.Enquiry.id)).group_by(models.Enquiry.email)
        ).all()
    }
    for customer in customers:
        bookings = customer.bookings
        customer.booking_count = len(bookings)
        customer.enquiry_count = enquiry_counts.get(customer.email.lower(), 0)
        customer.total_spent = sum(float(b.total) for b in bookings if b.status != "CANCELLED")
    return customers


@router.get("/customers/{customer_id}", response_model=schemas.CustomerAdminDetail)
def admin_customer_detail(customer_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    customer = crud.get_customer_detail(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.booking_count = len(customer.bookings)
    customer.enquiry_count = len(customer.enquiries)
    customer.total_spent = sum(float(b.total) for b in customer.bookings if b.status != "CANCELLED")
    return customer


@router.patch("/customers/{customer_id}/role", response_model=schemas.StaffRead,
              dependencies=[Depends(require_roles("ADMIN"))])
def promote_customer(customer_id: int, data: schemas.StaffUpdate, db: Session = Depends(get_db)):
    customer = crud.get_user(db, user_id=customer_id)
    if customer is None or customer.is_staff:
        raise HTTPException(status_code=404, detail="Customer not found")
    if data.role is None:
        raise HTTPException(status_code=422, detail="A staff role is required")
    return crud.update_staff(db, customer, data)


@router.delete("/customers/{customer_id}")
def admin_delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_roles("ADMIN")),
):
    customer = crud.get_user(db, user_id=customer_id)
    if customer is None or customer.is_staff:
        raise HTTPException(status_code=404, detail="Customer not found")
    crud.audit(
        db,
        user=current,
        action="deleted customer",
        entity="customer",
        entity_id=str(customer.id),
        details=customer.email,
    )
    crud.delete_user(db, customer)
    return {"detail": "Customer deleted successfully"}


# ---------------------------------------------------------------------------
# Enquiries (CRM)
# ---------------------------------------------------------------------------
@router.get("/enquiries", response_model=list[schemas.EnquiryRead])
def admin_enquiries(
    enquiry_status: str | None = None,
    assigned_staff_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    return crud.list_enquiries(db, status=enquiry_status, assigned_staff_id=assigned_staff_id)


@router.post("/enquiries", response_model=schemas.EnquiryRead, status_code=status.HTTP_201_CREATED)
def admin_create_enquiry(data: schemas.EnquiryCreate, db: Session = Depends(get_db), user=Depends(require_admin)):
    return crud.create_enquiry(db, data, actor=user)


@router.get("/enquiries/{enquiry_id}", response_model=schemas.EnquiryRead)
def admin_get_enquiry(enquiry_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    enquiry = crud.get_enquiry(db, enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return enquiry


@router.patch("/enquiries/{enquiry_id}", response_model=schemas.EnquiryRead)
def admin_update_enquiry(enquiry_id: int, data: schemas.EnquiryUpdate, db: Session = Depends(get_db), user=Depends(require_admin)):
    enquiry = crud.get_enquiry(db, enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return crud.update_enquiry(db, enquiry, data, actor=user)


@router.delete("/enquiries/{enquiry_id}", dependencies=[Depends(require_roles(*CONTENT))])
def admin_delete_enquiry(enquiry_id: int, db: Session = Depends(get_db)):
    enquiry = crud.get_enquiry(db, enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    crud.delete_enquiry(db, enquiry)
    return {"detail": "Enquiry deleted successfully"}


# ---------------------------------------------------------------------------
# Booking operations: notes, documents, payments
# ---------------------------------------------------------------------------
@router.get("/bookings/{booking_id}/notes", response_model=list[schemas.BookingNoteRead])
def booking_notes(booking_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    return crud.list_booking_notes(db, booking_id)


@router.post("/bookings/{booking_id}/notes", response_model=schemas.BookingNoteRead, status_code=status.HTTP_201_CREATED)
def booking_add_note(booking_id: int, data: schemas.BookingNoteCreate, db: Session = Depends(get_db), user=Depends(require_admin)):
    if crud.get_booking(db, booking_id) is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return crud.add_booking_note(db, booking_id, data.body, actor=user)


@router.get("/bookings/{booking_id}/payments", response_model=list[schemas.PaymentRead])
def booking_payments(booking_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    return crud.list_payments(db, booking_id)


@router.patch("/bookings/{booking_id}/payment", response_model=schemas.BookingRead,
              dependencies=[Depends(require_roles(*FINANCE))])
def booking_update_payment(
    booking_id: int,
    data: schemas.BookingStatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*FINANCE)),
):
    booking = crud.get_booking(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if data.payment_status is None:
        raise HTTPException(status_code=400, detail="payment_status is required")
    return crud.update_booking_payment_status(db, booking, data.payment_status, actor=user)


@router.post("/payments", response_model=schemas.PaymentRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles(*FINANCE))])
def record_payment(
    data: schemas.ManualPaymentCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*FINANCE)),
):
    if crud.get_booking(db, data.booking_id) is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    try:
        return crud.add_payment(db, data, actor=user)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.patch("/payments/{payment_id}", response_model=schemas.PaymentRead,
              dependencies=[Depends(require_roles(*FINANCE))])
def update_payment(
    payment_id: int,
    data: schemas.PaymentUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(*FINANCE)),
):
    payment = crud.get_payment(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return crud.update_payment_status(db, payment, data, actor=user)


@router.post("/bookings/{booking_id}/documents", response_model=schemas.DocumentRead, status_code=status.HTTP_201_CREATED)
def booking_attach_document(
    booking_id: int,
    document_type: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    if crud.get_booking(db, booking_id) is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if document_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported document type")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    original_name = file.filename or "document"
    safe_ext = re.sub(r"[^A-Za-z0-9]", "", Path(original_name).suffix.lstrip("."))[:8]
    # BUG-03: use a UUID-based storage name to prevent same-name overwrites.
    stored_stem = f"{booking_id}_{uuid.uuid4().hex}"
    stored_name = f"{stored_stem}.{safe_ext}" if safe_ext else stored_stem
    dest = UPLOAD_DIR / stored_name
    MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB
    # BUG-19: read in bounded chunks so oversized uploads never fill memory.
    content_parts: list[bytes] = []
    total = 0
    for chunk in iter(lambda: file.file.read(65536), b""):
        total += len(chunk)
        if total > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 20 MB.")
        content_parts.append(chunk)
    content = b"".join(content_parts)
    dest.write_bytes(content)
    try:
        document = crud.add_document(
            db, booking_id, document_type, title, original_name, str(dest), actor=user
        )
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    return document


@router.get("/documents", response_model=list[schemas.DocumentAdminRead])
def all_documents(db: Session = Depends(get_db), user=Depends(require_admin)):
    return crud.list_all_documents(db)


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    document = crud.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    resolved = Path(document.file_path).resolve()
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="That file is no longer available")
    return FileResponse(
        str(resolved),
        media_type="application/octet-stream",
        filename=document.file_name or resolved.name,
    )


# ---------------------------------------------------------------------------
# Offers + customer stories (CONTENT permission)
# ---------------------------------------------------------------------------
@router.get("/offers", response_model=list[schemas.OfferRead])
def admin_offers(db: Session = Depends(get_db), user=Depends(require_admin)):
    return crud.list_offers(db)


@router.post("/offers", response_model=schemas.OfferRead, status_code=status.HTTP_201_CREATED)
def admin_create_offer(data: schemas.OfferCreate, db: Session = Depends(get_db),
                       user: models.User = Depends(require_roles(*CONTENT))):
    return crud.create_offer(db, data, actor=user)


@router.patch("/offers/{offer_id}", response_model=schemas.OfferRead)
def admin_update_offer(offer_id: int, data: schemas.OfferUpdate, db: Session = Depends(get_db),
                       user: models.User = Depends(require_roles(*CONTENT))):
    offer = crud.get_offer(db, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    return crud.update_offer(db, offer, data, actor=user)


@router.delete("/offers/{offer_id}")
def admin_delete_offer(offer_id: int, db: Session = Depends(get_db),
                       user: models.User = Depends(require_roles(*CONTENT))):
    offer = crud.get_offer(db, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    crud.delete_offer(db, offer, actor=user)
    return {"detail": "Offer deleted successfully"}


@router.get("/customer-stories", response_model=list[schemas.CustomerStoryRead])
def admin_stories(db: Session = Depends(get_db), user=Depends(require_admin)):
    """All stories including unpublished drafts.

    The public, unauthenticated list lives at GET /api/customer-stories in
    routes/stories.py. Keeping it out of this router means this endpoint is no
    longer shadowed and staff can finally see drafts.
    """
    return crud.list_customer_stories(db)


@router.post("/customer-stories", response_model=schemas.CustomerStoryRead, status_code=status.HTTP_201_CREATED)
def admin_create_story(data: schemas.CustomerStoryCreate, db: Session = Depends(get_db),
                       user: models.User = Depends(require_roles(*CONTENT))):
    return crud.create_customer_story(db, data, actor=user)


@router.patch("/customer-stories/{story_id}", response_model=schemas.CustomerStoryRead)
def admin_update_story(story_id: int, data: schemas.CustomerStoryUpdate, db: Session = Depends(get_db),
                       user: models.User = Depends(require_roles(*CONTENT))):
    story = crud.get_customer_story(db, story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return crud.update_customer_story(db, story, data, actor=user)


@router.delete("/customer-stories/{story_id}")
def admin_delete_story(story_id: int, db: Session = Depends(get_db),
                       user: models.User = Depends(require_roles(*CONTENT))):
    story = crud.get_customer_story(db, story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    crud.delete_customer_story(db, story, actor=user)
    return {"detail": "Story deleted successfully"}


# ---------------------------------------------------------------------------
# Staff (ADMIN only)
# ---------------------------------------------------------------------------
@router.get("/staff", response_model=list[schemas.StaffRead], dependencies=[Depends(require_roles("ADMIN"))])
def list_staff(db: Session = Depends(get_db)):
    return crud.list_staff(db)


@router.post("/staff", response_model=schemas.StaffRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_roles("ADMIN"))])
def create_staff(data: schemas.StaffCreate, db: Session = Depends(get_db)):
    if crud.get_user(db, email=data.email):
        raise HTTPException(status_code=409, detail="A user with that email already exists")
    try:
        return crud.create_staff(db, data, security.hash_password(data.password))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A user with that email already exists")


@router.patch("/staff/{staff_id}", response_model=schemas.StaffRead)
def update_staff(
    staff_id: int,
    data: schemas.StaffUpdate,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_roles("ADMIN")),
):
    staff = crud.get_user(db, user_id=staff_id)
    if staff is None or not staff.is_staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    if data.is_active is False and staff.id == current.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")
    if (data.role is not None and data.role != "ADMIN" and staff.role == "ADMIN") or (data.is_active is False and staff.role == "ADMIN"):
        active_admins = [u for u in crud.list_staff(db) if u.is_active and u.role == "ADMIN" and u.id != staff.id]
        if not active_admins:
            raise HTTPException(status_code=400, detail="Cannot deactivate or demote the last active administrator")
    return crud.update_staff(db, staff, data)


@router.delete("/staff/{staff_id}")
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(require_roles("ADMIN")),
):
    staff = crud.get_user(db, user_id=staff_id)
    if staff is None or not staff.is_staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    if staff.id == current.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    crud.audit(
        db,
        user=current,
        action="deleted staff member",
        entity="staff",
        entity_id=str(staff.id),
        details=f"{staff.email} ({staff.role})",
    )
    crud.delete_user(db, staff)
    return {"detail": "Staff member deleted successfully"}


# ---------------------------------------------------------------------------
# Staff assignments lookup (for CRM assign dropdown)
# ---------------------------------------------------------------------------
@router.get("/staff-assign", response_model=list[schemas.StaffRead],
            dependencies=[Depends(require_admin)])
def staff_assign_list(db: Session = Depends(get_db)):
    return crud.list_staff_for_assign(db)


# ---------------------------------------------------------------------------
# Settings (ADMIN only)
# ---------------------------------------------------------------------------
@router.get("/settings", response_model=list[schemas.SettingRead], dependencies=[Depends(require_roles("ADMIN"))])
def list_settings(db: Session = Depends(get_db)):
    return crud.list_settings(db)


@router.put("/settings/{key}", response_model=schemas.SettingRead)
def update_setting(key: str, data: schemas.SettingUpdate, db: Session = Depends(get_db),
                   user: models.User = Depends(require_roles("ADMIN"))):
    if not re.match(r"^[a-z0-9_.-]{1,120}$", key):
        raise HTTPException(status_code=400, detail="Invalid setting key")
    record = crud.set_setting(db, key, data.value, actor=user)
    crud.audit(db, user=user, action="updated setting", entity="setting", entity_id=key)
    return record


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------
@router.get("/audit-log", response_model=list[schemas.AuditLogRead],
            dependencies=[Depends(require_roles("MANAGER", "ADMIN"))])
def audit_log(db: Session = Depends(get_db)):
    return crud.list_audit_logs(db)