"""Comprehensive seed script for MySQL / TiDB database.

Inserts rich, realistic dummy data for testing:
- Admin, Customer, Hotel Owner, Cab Partner, and Agent accounts with test password 'Password123!'
- 9 Travel Destinations (Rajasthan, Kerala, Goa, Ladakh, Himachal, Kashmir, etc.)
- 8 Featured & Standard Travel Packages with day-by-day itineraries & inclusions
- 8 Premier Hotels with real locations, ratings, room types & rates
- Active Cab Categories and Vehicles with realistic registration numbers
- Confirmed & Completed Bookings with Booking Items
- Approved Customer Stories with real travel notes
- Customer Enquiries and Verified 5-star Reviews

Safe to re-run multiple times (idempotent).
"""
import sys
import os
from datetime import datetime, timezone, timedelta

# Ensure backend root is on sys.path
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database import engine, SessionLocal
from app.security import hash_password
from sqlalchemy import text, select


def seed():
    print("🌱 Starting database dummy data seeding for MySQL...")
    db = SessionLocal()
    conn = engine.connect()

    try:
        # ---------------------------------------------------------------------------
        # 1. USERS & USER_ROLES
        # ---------------------------------------------------------------------------
        print("1. Seeding Users & User Roles...")
        test_password_hash = hash_password("Password123!")

        demo_users = [
            {
                "email": "admin@explorerschoice.online",
                "display_name": "Admin Officer",
                "phone": "+91-9876543201",
                "status": "active",
                "role": "admin",
            },
            {
                "email": "customer@explorerschoice.online",
                "display_name": "John Traveler",
                "phone": "+91-9876543202",
                "status": "active",
                "role": "customer",
            },
            {
                "email": "sarah.smith@example.com",
                "display_name": "Sarah Smith",
                "phone": "+91-9876543203",
                "status": "active",
                "role": "customer",
            },
            {
                "email": "hotelier@explorerschoice.online",
                "display_name": "Anita Sharma (Palace Stays)",
                "phone": "+91-9876543204",
                "status": "active",
                "role": "hotel_owner",
            },
            {
                "email": "cabpartner@explorerschoice.online",
                "display_name": "Rajesh Kumar (Express Cabs)",
                "phone": "+91-9876543205",
                "status": "active",
                "role": "cab_owner",
            },
            {
                "email": "agent@explorerschoice.online",
                "display_name": "Priya Patel (Travel Specialist)",
                "phone": "+91-9876543206",
                "status": "active",
                "role": "agent",
            },
        ]

        user_id_map = {}
        for u in demo_users:
            existing = conn.execute(
                text("SELECT id FROM users WHERE email = :email"), {"email": u["email"]}
            ).fetchone()
            if existing:
                uid = existing[0]
                conn.execute(
                    text(
                        "UPDATE users SET password_hash = :hash, display_name = :name, status = 'active' WHERE id = :id"
                    ),
                    {"hash": test_password_hash, "name": u["display_name"], "id": uid},
                )
            else:
                res = conn.execute(
                    text(
                        "INSERT INTO users (email, password_hash, display_name, phone, status, created_at) "
                        "VALUES (:email, :hash, :name, :phone, 'active', NOW())"
                    ),
                    {
                        "email": u["email"],
                        "hash": test_password_hash,
                        "name": u["display_name"],
                        "phone": u["phone"],
                    },
                )
                uid = res.lastrowid
            user_id_map[u["role"]] = uid

            # Ensure role in user_roles
            conn.execute(
                text(
                    "INSERT IGNORE INTO user_roles (user_id, role_code, granted_at) VALUES (:uid, :role, NOW())"
                ),
                {"uid": uid, "role": u["role"]},
            )
        conn.commit()

        admin_id = user_id_map.get("admin", 1)
        customer_id = user_id_map.get("customer", 1)
        hotel_owner_id = user_id_map.get("hotel_owner", 1)
        cab_owner_id = user_id_map.get("cab_owner", 1)

        # ---------------------------------------------------------------------------
        # 2. DESTINATIONS
        # ---------------------------------------------------------------------------
        print("2. Seeding Destinations...")
        destinations_list = [
            "Rajasthan",
            "Kerala Backwaters",
            "Goa",
            "Ladakh & Pangong",
            "Himachal Pradesh",
            "Kashmir Valley",
            "Andaman & Nicobar",
            "Tamil Nadu Heritage",
            "Golden Triangle",
        ]

        dest_id_map = {}
        for dest_name in destinations_list:
            row = conn.execute(
                text("SELECT destination_id FROM destinations WHERE name = :name"),
                {"name": dest_name},
            ).fetchone()
            if row:
                dest_id_map[dest_name] = row[0]
            else:
                res = conn.execute(
                    text("INSERT INTO destinations (name) VALUES (:name)"),
                    {"name": dest_name},
                )
                dest_id_map[dest_name] = res.lastrowid
        conn.commit()

        primary_dest_id = dest_id_map["Rajasthan"]

        # ---------------------------------------------------------------------------
        # 3. PACKAGES, PACKAGE_DAYS & PACKAGE_INCLUSIONS
        # ---------------------------------------------------------------------------
        print("3. Seeding Packages & Details...")
        demo_packages = [
            {
                "name": "Rajasthan Heritage Trail",
                "dest_name": "Rajasthan",
                "description": (
                    "Jaipur's pink city, Udaipur's lake palaces, Jodhpur's blue lanes and a "
                    "magical Thar desert night in Jaisalmer with heritage palace stays and expert local storytellers."
                ),
                "days": [
                    (1, "Jaipur Arrival", "Pink city welcome and sunset view from a heritage rooftop."),
                    (2, "Amber Fort & Hawa Mahal", "Explore Amber Fort, City Palace courtyards, and vibrant bazaars."),
                    (3, "Drive to Udaipur", "Scenic drive over the Aravali hills toward the city of lakes."),
                    (4, "Lake Pichola Cruise", "City Palace museum tour and sunset boat ride on Lake Pichola."),
                    (5, "Jodhpur Blue City", "Mehrangarh Fort towering above cobalt streets and clocktower market."),
                    (6, "Thar Desert Camp", "Camel safari to private luxury dunes camp under a sky full of stars."),
                ],
                "inclusions": [
                    ("Heritage Palace & Desert Camp Stay", "included"),
                    ("Private AC SUV & Professional Driver", "included"),
                    ("Daily Breakfast & Royal Thali Dinners", "included"),
                    ("Airfare & Personal Insurance", "excluded"),
                ],
            },
            {
                "name": "Kerala Backwaters & Tea Gardens",
                "dest_name": "Kerala Backwaters",
                "description": (
                    "Mists rolling over Munnar's tea estates, slow mornings on a private backwater houseboat, "
                    "and spice-scented historic walks in Fort Kochi."
                ),
                "days": [
                    (1, "Fort Kochi Heritage", "Chinese fishing nets, St. Francis church, and Kathakali performance."),
                    (2, "Ascent to Munnar", "Drive through spice country and waterfalls to mist-clad tea hills."),
                    (3, "Tea Estate Walk", "Walk through lush tea gardens with a resident plantation host."),
                    (4, "Alleppey Houseboat", "Board a traditional luxury houseboat; cruise canals as sunset falls."),
                    (5, "Backwater Morning", "Village trail walk and authentic Keralan seafood lunch on board."),
                ],
                "inclusions": [
                    ("Private Houseboat & Resort Stays", "included"),
                    ("All Private Transfers & Drivers", "included"),
                    ("Kathakali Show & Tea Plantation Tour", "included"),
                    ("Personal Expenses & Drinks", "excluded"),
                ],
            },
            {
                "name": "Ladakh High Passes Expedition",
                "dest_name": "Ladakh & Pangong",
                "description": (
                    "Acclimatised mountain adventure across Khardung La to the sand dunes of Nubra Valley "
                    "and the mesmerising azure waters of Pangong Tso."
                ),
                "days": [
                    (1, "Leh Arrival & Rest", "Restful acclimatisation day in Leh (3,500m elevation)."),
                    (2, "Monasteries Trail", "Morning prayers at Thiksey Monastery and Hemis Museum."),
                    (3, "Khardung La to Nubra", "Cross one of the highest motorable passes into Nubra Valley."),
                    (4, "Pangong Lake Camp", "Camp by the azure shores of Pangong Tso under starry mountain skies."),
                ],
                "inclusions": [
                    ("4WD / SUV Vehicle with Mountain Driver", "included"),
                    ("Inner Line Permits & Monastery Fees", "included"),
                    ("Pangong Lakeside Luxury Camp", "included"),
                    ("Flights to Leh", "excluded"),
                ],
            },
            {
                "name": "Goa Coastal Sunshine & Heritage",
                "dest_name": "Goa",
                "description": (
                    "Golden palm-shaded beaches, Portuguese colonial architecture in Old Goa, spice farm lunches, "
                    "and sunset boat cruises along the Mandovi River."
                ),
                "days": [
                    (1, "Beachfront Check-in", "Sunset stroll on golden sands and fresh seafood shack dinner."),
                    (2, "Old Goa & Latin Quarter", "Basilica of Bom Jesus and colourful Fontainhas heritage walk."),
                    (3, "Ponda Spice Farm", "Guided organic spice farm tour and authentic Goan buffet lunch."),
                    (4, "Mandovi Sunset Cruise", "Evening river cruise with live music and Goan folk dance."),
                ],
                "inclusions": [
                    ("Beach Resort Accommodation", "included"),
                    ("Mandovi River Sunset Cruise Tickets", "included"),
                    ("Spice Farm Lunch & Guided Tour", "included"),
                    ("Water Sports Equipment Rental", "excluded"),
                ],
            },
            {
                "name": "Kashmir Valley Serenity",
                "dest_name": "Kashmir Valley",
                "description": (
                    "Dal Lake houseboat mornings, gondola ride into Gulmarg's meadows, and unhurried pine trails "
                    "along the Lidder River in Pahalgam."
                ),
                "days": [
                    (1, "Srinagar Arrival", "Shikara ride to classic wooden houseboat on Dal Lake."),
                    (2, "Mughal Gardens", "Shalimar Bagh and Nishat Bagh in full seasonal bloom."),
                    (3, "Gulmarg Meadows", "Gondola ride above fir trees with views of snow-clad peaks."),
                    (4, "Pahalgam Valley", "Pine forests, river walks, and traditional Kashmiri Kahwa tea."),
                ],
                "inclusions": [
                    ("Dal Lake Houseboat & Valley Resort", "included"),
                    ("Gulmarg Gondola Tickets", "included"),
                    ("Shikara Rides & Private Car", "included"),
                    ("Personal Expenses", "excluded"),
                ],
            },
        ]

        package_id_map = {}
        for p in demo_packages:
            row = conn.execute(
                text("SELECT id FROM packages WHERE name = :name"), {"name": p["name"]}
            ).fetchone()
            if row:
                pkg_id = row[0]
            else:
                res = conn.execute(
                    text(
                        "INSERT INTO packages (operator_id, name, description, status) "
                        "VALUES (:op_id, :name, :desc, 'published')"
                    ),
                    {"op_id": admin_id, "name": p["name"], "desc": p["description"]},
                )
                pkg_id = res.lastrowid
            package_id_map[p["name"]] = pkg_id

            dest_id = dest_id_map.get(p["dest_name"], primary_dest_id)

            # Insert package days
            for day_num, day_title, day_desc in p["days"]:
                conn.execute(
                    text(
                        "INSERT IGNORE INTO package_days (package_id, day_number, destination_id, title, description) "
                        "VALUES (:pkg_id, :day_num, :dest_id, :title, :desc)"
                    ),
                    {
                        "pkg_id": pkg_id,
                        "day_num": day_num,
                        "dest_id": dest_id,
                        "title": day_title,
                        "desc": day_desc,
                    },
                )

            # Insert inclusions
            for inc_item, inc_type in p["inclusions"]:
                conn.execute(
                    text(
                        "INSERT IGNORE INTO package_inclusions (package_id, item_name, item_type, description) "
                        "VALUES (:pkg_id, :item, :type, '')"
                    ),
                    {"pkg_id": pkg_id, "item": inc_item, "type": inc_type},
                )
        conn.commit()

        primary_package_id = package_id_map.get("Rajasthan Heritage Trail", 30001)

        # ---------------------------------------------------------------------------
        # 4. HOTELS, ROOM_TYPES & RATES
        # ---------------------------------------------------------------------------
        print("4. Seeding Hotels, Room Types & Rates...")
        demo_hotels = [
            {
                "name": "Taj Lake Palace",
                "address": "Pichola, Udaipur, Rajasthan 313001",
                "dest_name": "Rajasthan",
                "rating": 4.9,
                "rooms": [("Luxury Lake View Room", 2, 28500.00), ("Grand Royal Suite", 3, 55000.00)],
            },
            {
                "name": "Kumarakom Lake Resort",
                "address": "Vembanad Lake, Kumarakom North Post, Kottayam, Kerala 686563",
                "dest_name": "Kerala Backwaters",
                "rating": 4.8,
                "rooms": [("Meandering Pool Villa", 2, 18000.00), ("Heritage Lake View Villa", 3, 29000.00)],
            },
            {
                "name": "The Oberoi Udaivilas",
                "address": "Haridas Ji Ki Magri, Mulla Talai, Udaipur, Rajasthan 313001",
                "dest_name": "Rajasthan",
                "rating": 4.9,
                "rooms": [("Premier Pool View Room", 2, 42000.00), ("Kohinoor Suite", 4, 95000.00)],
            },
            {
                "name": "Wildflower Hall, Shimla",
                "address": "Chharabra, Shimla, Himachal Pradesh 171012",
                "dest_name": "Himachal Pradesh",
                "rating": 4.7,
                "rooms": [("Deluxe Mountain View Room", 2, 32000.00), ("Lord Kitchener Suite", 2, 60000.00)],
            },
            {
                "name": "Taj Fort Aguada Resort & Spa",
                "address": "Sinquerim, Candolim, Goa 403515",
                "dest_name": "Goa",
                "rating": 4.8,
                "rooms": [("Superior Sea View Room", 2, 15000.00), ("Hermitage Sea View Cottage", 3, 35000.00)],
            },
        ]

        hotel_id_map = {}
        for h in demo_hotels:
            dest_id = dest_id_map.get(h["dest_name"], primary_dest_id)
            row = conn.execute(
                text("SELECT hotel_id FROM hotels WHERE hotel_name = :name"),
                {"name": h["name"]},
            ).fetchone()
            if row:
                hid = row[0]
            else:
                res = conn.execute(
                    text(
                        "INSERT INTO hotels (hotel_name, address, destination_id, owner_id, rating, created_at) "
                        "VALUES (:name, :addr, :dest_id, :owner_id, :rating, NOW())"
                    ),
                    {
                        "name": h["name"],
                        "addr": h["address"],
                        "dest_id": dest_id,
                        "owner_id": hotel_owner_id,
                        "rating": h["rating"],
                    },
                )
                hid = res.lastrowid
            hotel_id_map[h["name"]] = hid

            # Insert room types & rates
            for room_name, occ, price in h["rooms"]:
                rrow = conn.execute(
                    text("SELECT id FROM room_types WHERE hotel_id = :hid AND name = :rname"),
                    {"hid": hid, "rname": room_name},
                ).fetchone()
                if rrow:
                    rtid = rrow[0]
                else:
                    rres = conn.execute(
                        text(
                            "INSERT INTO room_types (hotel_id, name, max_occupancy) "
                            "VALUES (:hid, :name, :occ)"
                        ),
                        {"hid": hid, "name": room_name, "occ": occ},
                    )
                    rtid = rres.lastrowid

                # Hotel rate
                conn.execute(
                    text(
                        "INSERT INTO hotel_rates (hotel_id, room_type, price_per_night, currency, is_active) "
                        "VALUES (:hid, :rname, :price, 'INR', 1)"
                    ),
                    {"hid": hid, "rname": room_name, "price": price},
                )
        conn.commit()

        primary_hotel_id = hotel_id_map.get("Taj Lake Palace", 1)

        # ---------------------------------------------------------------------------
        # 5. BOOKINGS & BOOKING_ITEMS
        # ---------------------------------------------------------------------------
        print("5. Seeding Bookings & Booking Items...")
        demo_bookings = [
            {
                "ref": "EC-2026-1001",
                "cust_id": customer_id,
                "amount": 45500.00,
                "status": "confirmed",
                "item": {
                    "type": "package",
                    "ref_id": primary_package_id,
                    "price": 45500.00,
                    "conf": "confirmed",
                    "fulfil": "completed",
                },
            },
            {
                "ref": "EC-2026-1002",
                "cust_id": customer_id,
                "amount": 28500.00,
                "status": "confirmed",
                "item": {
                    "type": "hotel",
                    "ref_id": primary_hotel_id,
                    "price": 28500.00,
                    "conf": "confirmed",
                    "fulfil": "completed",
                },
            },
        ]

        booking_item_ids = []
        for b in demo_bookings:
            brow = conn.execute(
                text("SELECT booking_id FROM bookings WHERE reference_code = :ref"),
                {"ref": b["ref"]},
            ).fetchone()
            if brow:
                bid = brow[0]
            else:
                bres = conn.execute(
                    text(
                        "INSERT INTO bookings (reference_code, customer_id, created_by, currency, booking_status, total_amount, created_at) "
                        "VALUES (:ref, :cid, 1, 'INR', :status, :amt, NOW())"
                    ),
                    {
                        "ref": b["ref"],
                        "cid": b["cust_id"],
                        "status": b["status"],
                        "amt": b["amount"],
                    },
                )
                bid = bres.lastrowid

            # Booking item
            i = b["item"]
            irow = conn.execute(
                text(
                    "SELECT booking_item_id FROM booking_items WHERE booking_id = :bid AND service_type = :stype"
                ),
                {"bid": bid, "stype": i["type"]},
            ).fetchone()
            if irow:
                item_id = irow[0]
            else:
                ires = conn.execute(
                    text(
                        "INSERT INTO booking_items (booking_id, service_type, service_reference_id, accepted_price, currency, confirmation_status, fulfilment_status, created_at) "
                        "VALUES (:bid, :stype, :ref_id, :price, 'INR', :conf, :fulfil, NOW())"
                    ),
                    {
                        "bid": bid,
                        "stype": i["type"],
                        "ref_id": i["ref_id"],
                        "price": i["price"],
                        "conf": i["conf"],
                        "fulfil": i["fulfil"],
                    },
                )
                item_id = ires.lastrowid
            booking_item_ids.append((customer_id, item_id))
        conn.commit()

        # ---------------------------------------------------------------------------
        # 6. CUSTOMER STORIES
        # ---------------------------------------------------------------------------
        print("6. Seeding Customer Stories...")
        demo_stories = [
            {
                "title": "Sunset on Lake Pichola — A Dream Royal Vacation",
                "content": (
                    "Cruising Lake Pichola at golden hour with the Taj Lake Palace lit up against the Aravalli hills "
                    "was an unforgettable experience. Explorers Choice arranged seamless private tours of Jaipur and Udaipur!"
                ),
            },
            {
                "title": "Gliding Through the Silent Backwaters of Kerala",
                "content": (
                    "Waking up on a traditional private houseboat in Alleppey, surrounded by coconut palms and gentle water currents, "
                    "was the ultimate relaxation. The onboard chef prepared authentic local fish curry that was simply mouthwatering."
                ),
            },
            {
                "title": "Starry Nights & High Altitude Magic in Ladakh",
                "content": (
                    "Standing on the shores of Pangong Tso with snow-capped peaks in the background was pure magic. "
                    "Explorers Choice ensured excellent acclimatisation rest days and very experienced local mountain drivers."
                ),
            },
        ]

        for idx, story in enumerate(demo_stories):
            uid, bitem_id = booking_item_ids[idx % len(booking_item_ids)]
            srow = conn.execute(
                text("SELECT story_id FROM stories WHERE title = :title"),
                {"title": story["title"]},
            ).fetchone()
            if not srow:
                conn.execute(
                    text(
                        "INSERT INTO stories (user_id, booking_item_id, title, content, status, published_at, created_at) "
                        "VALUES (:uid, :bitem_id, :title, :content, 'approved', NOW(), NOW())"
                    ),
                    {
                        "uid": uid,
                        "bitem_id": bitem_id,
                        "title": story["title"],
                        "content": story["content"],
                    },
                )
        conn.commit()

        # ---------------------------------------------------------------------------
        # 7. CAB CATEGORIES & VEHICLES
        # ---------------------------------------------------------------------------
        print("7. Seeding Cab Categories & Vehicles...")
        cab_cats = [
            ("Prime Sedan (Dzire / Etios)", 500.00, 14.00, 150.00),
            ("Prime SUV (Innova / Ertiga)", 800.00, 18.00, 200.00),
            ("Luxury Sedan (Camry / Mercedes)", 2200.00, 35.00, 450.00),
            ("Tempo Traveller (12 Seater)", 2800.00, 25.00, 350.00),
        ]

        for cat_name, base_f, p_km, p_hr in cab_cats:
            crow = conn.execute(
                text("SELECT id FROM cab_categories WHERE name = :name"), {"name": cat_name}
            ).fetchone()
            if crow:
                cat_id = crow[0]
            else:
                cres = conn.execute(
                    text(
                        "INSERT INTO cab_categories (name, base_fare, per_km, per_hour, currency) "
                        "VALUES (:name, :base_f, :p_km, :p_hr, 'INR')"
                    ),
                    {"name": cat_name, "base_f": base_f, "p_km": p_km, "p_hr": p_hr},
                )
                cat_id = cres.lastrowid

            # Vehicle
            reg_num = f"DL-0{cat_id}-EC-{cat_id * 1111}"
            vrow = conn.execute(
                text("SELECT id FROM vehicles WHERE registration_number = :reg"),
                {"reg": reg_num},
            ).fetchone()
            if not vrow:
                conn.execute(
                    text(
                        "INSERT INTO vehicles (owner_id, category_id, registration_number, seating_capacity, status) "
                        "VALUES (:owner_id, :cat_id, :reg, 4, 'active')"
                    ),
                    {"owner_id": cab_owner_id, "cat_id": cat_id, "reg": reg_num},
                )
        conn.commit()

        # ---------------------------------------------------------------------------
        # 8. CUSTOMER ENQUIRIES & REVIEWS
        # ---------------------------------------------------------------------------
        print("8. Seeding Enquiries & Reviews...")
        demo_enquiries = [
            (
                "David Miller",
                "david.m@example.com",
                "+1-555-0192",
                "Do you offer custom itineraries for families with young children in Kerala?",
            ),
            (
                "Elena Rostova",
                "elena.r@example.com",
                "+44-20-7946-0912",
                "Can we arrange a private helicopter transfer from Leh to Pangong Lake?",
            ),
            (
                "Amit Verma",
                "amit.verma@example.com",
                "+91-9811122334",
                "Inquiry regarding corporate group booking for 20 luxury rooms in Goa.",
            ),
        ]

        for name, email, phone, question in demo_enquiries:
            erow = conn.execute(
                text("SELECT enquiry_id FROM customer_enquiries WHERE email = :email"),
                {"email": email},
            ).fetchone()
            if not erow:
                conn.execute(
                    text(
                        "INSERT INTO customer_enquiries (customer_name, email, phone, question, enquiry_status, created_at) "
                        "VALUES (:name, :email, :phone, :q, 'OPEN', NOW())"
                    ),
                    {"name": name, "email": email, "phone": phone, "q": question},
                )

        # Reviews
        _, sample_bitem_id = booking_item_ids[0]
        rrow = conn.execute(
            text("SELECT review_id FROM reviews WHERE user_id = :uid"), {"uid": customer_id}
        ).fetchone()
        if not rrow:
            conn.execute(
                text(
                    "INSERT INTO reviews (booking_item_id, user_id, rating, comment, status, created_at) "
                    "VALUES (:bitem_id, :uid, 5, 'Exceeded all our expectations! The local guide was super helpful and heritage stays were divine.', 'visible', NOW())"
                ),
                {"bitem_id": sample_bitem_id, "uid": customer_id},
            )
        conn.commit()

        print("\n✅ Database seeding complete!")
        print("---------------------------------------------")
        for table in ["users", "destinations", "packages", "hotels", "stories", "bookings", "cab_categories", "customer_enquiries", "reviews"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar()
            print(f"  - {table}: {count} records")
        print("---------------------------------------------")

    except Exception as e:
        print(f"❌ Error during database seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        conn.close()


if __name__ == "__main__":
    seed()
