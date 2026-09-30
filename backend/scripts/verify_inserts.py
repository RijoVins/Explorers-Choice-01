"""Verify the real CRUD insert paths against MySQL TEXT/JSON columns.

The migration deliberately omits server defaults on LONGTEXT/JSON columns
(TiDB rejects them), so the ORM's Python-side defaults and the Pydantic
schemas must supply every value. This exercises the functions the API calls
(create_destination, create_package, ...) rather than raw ORM construction.

Everything runs inside an outer transaction that is never committed, so the
db.commit() calls inside crud.py cannot persist anything. Verified by a
separate-connection read at the end.
"""
import pathlib
import sys

from sqlalchemy import func, select
from sqlalchemy.orm import Session

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import crud, schemas  # noqa: E402
from app.database import engine  # noqa: E402
import app.models as models  # noqa: E402

results = []


def check(name, ok, detail=""):
    results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" -> {detail}" if detail else ""))


connection = engine.connect()
trans = connection.begin()
session = Session(bind=connection, join_transaction_mode="create_savepoint")

try:
    dest = crud.create_destination(session, schemas.DestinationCreate(
        name="CRUD Destination", slug="crud-destination", country="X"))
    check("create_destination inserts", dest.id is not None, f"id={dest.id}")
    check("  gallery JSON default applied", dest.gallery == [], repr(dest.gallery))
    check("  highlights JSON default applied", dest.highlights == [], repr(dest.highlights))
    check("  description LONGTEXT default applied", dest.description == "", repr(dest.description))
    check("  region LONGTEXT/VARCHAR default applied", dest.region == "", repr(dest.region))

    pkg = crud.create_package(session, schemas.PackageCreate(
        destination_id=dest.id, name="CRUD Package", slug="crud-package",
        itinerary=[schemas.ItineraryDayCreate(day_number=1, title="Day 1")],
        faqs=[]))
    check("create_package inserts", pkg.id is not None, f"id={pkg.id}")
    for field in ("gallery", "highlights", "included", "excluded", "important_information"):
        check(f"  package.{field} JSON default applied", getattr(pkg, field) == [],
              repr(getattr(pkg, field)))
    for field in ("short_description", "description", "accommodation_summary"):
        check(f"  package.{field} LONGTEXT default applied", getattr(pkg, field) == "",
              repr(getattr(pkg, field)))
    check("  package itinerary children inserted", len(pkg.itinerary) == 1,
          f"{len(pkg.itinerary)} day(s)")

    story = crud.create_customer_story(session, schemas.CustomerStoryCreate(
        customer_name="CRUD Story", title="A story"))
    check("create_customer_story inserts", story.id is not None, f"id={story.id}")
    check("  story.photos JSON default applied", story.photos == [], repr(story.photos))

    offer = crud.create_offer(session, schemas.OfferCreate(title="CRUD Offer"))
    check("create_offer inserts", offer.id is not None, f"id={offer.id}")
    check("  offer.description LONGTEXT default applied", offer.description == "",
          repr(offer.description))

    owner = models.User(email="verify-hotel-owner@example.invalid", full_name="Owner",
                        phone="+10000000009", country="X", role="HOTEL_OWNER",
                        password_hash="x")
    session.add(owner)
    session.commit()

    hotel = crud.create_hotel(session, owner.id, schemas.HotelCreate(
        name="CRUD Hotel", location="Somewhere"))
    check("create_hotel inserts", hotel.id is not None, f"id={hotel.id}")
    check("  hotel.amenities JSON default applied", hotel.amenities == [], repr(hotel.amenities))
    check("  hotel.highlights JSON default applied", hotel.highlights == [], repr(hotel.highlights))
    check("  hotel.description LONGTEXT default applied", hotel.description == "",
          repr(hotel.description))

    note_holder = crud.create_destination(session, schemas.DestinationCreate(
        name="Note Host", slug="note-host", country="X"))
    check("explicit JSON values override defaults",
          crud.create_customer_story(session, schemas.CustomerStoryCreate(
              customer_name="Explicit", title="T",
              photos=["https://example.invalid/a.jpg"])).photos
          == ["https://example.invalid/a.jpg"])

except Exception as exc:
    check("CRUD insert paths execute without error", False, f"{type(exc).__name__}: {exc}"[:160])
finally:
    trans.rollback()
    connection.close()

print("\nPERSISTENCE CHECK (separate connection, committed data only)")
session2 = Session(engine)
leaks = []
for model, label in [(models.Destination, "destinations"), (models.Package, "packages"),
                     (models.CustomerStory, "customer_stories"), (models.Offer, "offers"),
                     (models.Hotel, "hotels"), (models.ItineraryDay, "itinerary_days"),
                     (models.User, "users")]:
    n = session2.execute(select(func.count()).select_from(model)).scalar()
    leaks.append(f"{label}={n}")
    check(f"no committed rows left in {label}", n == 0, f"count={n}")
session2.close()
print("  row counts -> " + ", ".join(leaks))

print("\n" + "=" * 62)
failed = [n for n, ok in results if not ok]
print(f"{len(results) - len(failed)}/{len(results)} checks passed")
if failed:
    print("FAILED:")
    for n in failed:
        print("  -", n)
sys.exit(1 if failed else 0)
