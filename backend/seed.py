"""Seed the database with realistic demo destinations, packages and itineraries.

Demo content only — replace or extend with real product data via the admin API.
Safe to re-run: it skips items whose slug already exists.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.models import Destination, Hotel, Package, ItineraryDay, PackageFaq, User

# ---------------------------------------------------------------------------
# Demo destinations
# ---------------------------------------------------------------------------
DESTINATIONS = [
    {
        "name": "Rajasthan",
        "slug": "rajasthan",
        "country": "India",
        "region": "North India",
        "short_description": "Palaces, forts and the colours of the Thar desert",
        "description": (
            "The land of kings: rose-pink Jaipur, lake-strewn Udaipur, the blue city of "
            "Jodhpur and the golden ramparts of Jaisalmer. Explorers Choice pairs you with "
            "local guides who know the quieter courtyards, the best thali houses and the "
            "desert camps that sit beyond the tourist trail."
        ),
        "hero_image": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=80",
        ],
        "best_time": "October – March",
        "recommended_duration": "6–10 days",
        "highlights": ["Jaipur City Palace", "Udaipur lakes", "Jodhpur fort", "Jaisalmer dunes"],
        "things_to_do": [
            "Watch the sun rise over Hawa Mahal from a roof café",
            "Sail the evening on Lake Pichola",
            "Walk the lanes of Jodhpur's blue old city",
            "Camp in the Thar beneath a sky full of stars",
        ],
        "travel_information": [
            "Currency: Indian rupee (INR)",
            "Language: Hindi, Rajasthani & English",
            "Visa: e-Tourist visa available online for most nationalities",
        ],
        "is_featured": True,
    },
    {
        "name": "Kerala",
        "slug": "kerala",
        "country": "India",
        "region": "South India",
        "short_description": "Backwaters, tea hills and God's Own Country",
        "description": (
            "Slow mornings at a houseboat, mists rolling over Munnar's tea estates, and "
            "the old spice lanes of Kochi. Kerala rewards the traveller who lingers — "
            "we build in unhurried boat days, homely seafood and a pace that lets the "
            "backwaters do their quiet work."
        ),
        "hero_image": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
        ],
        "best_time": "September – March",
        "recommended_duration": "6–9 days",
        "highlights": ["Alleppey houseboat", "Munnar tea estates", "Kochi forts", "Kathakali evening"],
        "things_to_do": [
            "Sleep aboard a private backwater houseboat",
            "Walk sunrise through a Munnar tea plantation",
            "Watch a Kathakali performance in Kochi",
            "Taste toddy-shop seafood on a village trail",
        ],
        "travel_information": [
            "Currency: Indian rupee (INR)",
            "Language: Malayalam, English & Hindi",
            "Visa: e-Tourist visa available online for most nationalities",
        ],
        "is_featured": True,
    },
    {
        "name": "Ladakh",
        "slug": "ladakh",
        "country": "India",
        "region": "North India",
        "short_description": "High passes, monasteries and the moonscape of Pangong",
        "description": (
            "A land of high-altitude deserts where prayer flags snap in thin air, white "
            "monasteries cling to raw cliffs and Pangong Lake shifts through a dozen blues. "
            "We travel slowly, with acclimatisation built in and a local guide who opens "
            "the mountain homes others drive past."
        ),
        "hero_image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80",
        ],
        "best_time": "May – September",
        "recommended_duration": "8–12 days",
        "highlights": ["Pangong Lake", "Thiksey monastery", "Nubra sand dunes", "Khardung La"],
        "things_to_do": [
            "Camp beside Pangong Lake at golden hour",
            "Join morning prayers at Thiksey monastery",
            "Ride a double-humped camel in Nubra",
            "Cross Khardung La on a clear morning",
        ],
        "travel_information": [
            "Currency: Indian rupee (INR)",
            "Language: Ladakhi, Hindi & English",
            "Altitude: Leh sits at 3,500m — acclimatisation days are included",
        ],
        "is_featured": True,
    },
    {
        "name": "Goa",
        "slug": "goa",
        "country": "India",
        "region": "West India",
        "short_description": "Golden beaches, Portuguese lanes and easy living",
        "description": (
            "Sun-warmed beaches, palm-shaded villages and whitewashed churches from its "
            "Portuguese past. We mix laid-back beach days with spice-farm lunches, old "
            "city walks and a sunset that never gets old."
        ),
        "hero_image": "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=80",
        ],
        "best_time": "November – February",
        "recommended_duration": "5–8 days",
        "highlights": ["North Goa beaches", "Old Goa churches", "Spice farms", "Sunset cruises"],
        "things_to_do": [
            "Linger over a beach-shack breakfast",
            "Walk the Basilica of Bom Jesus in Old Goa",
            "Lunch on a spice farm in Ponda",
            "Sail the Mandovi at sunset",
        ],
        "travel_information": [
            "Currency: Indian rupee (INR)",
            "Language: Konkani, Hindi & English",
            "Visa: e-Tourist visa available online for most nationalities",
        ],
        "is_featured": True,
    },
    {
        "name": "Kashmir",
        "slug": "kashmir",
        "country": "India",
        "region": "North India",
        "short_description": "Dal Lake, meadow valleys and the Himalayas",
        "description": (
            "Shikaras gliding past lotus blooms on Dal Lake, the meadow valleys of Pahalgam "
            "and Gulmarg's fir-clad slopes. A journey that feels suspended in time, taken "
            "at a gentle pace with a host who makes you feel like family."
        ),
        "hero_image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1530908295418-12c326d45a24?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1503256207526-0d5d80fa2f47?auto=format&fit=crop&w=1200&q=80",
        ],
        "best_time": "April – October",
        "recommended_duration": "6–9 days",
        "highlights": ["Dal Lake houseboat", "Gulmarg meadows", "Pahalgam valley", "Mughal gardens"],
        "things_to_do": [
            "Wake on a Dal Lake houseboat",
            "Ride a gondola above Gulmarg",
            "Walk the pine trails of Pahalgam",
            "Wander the Shalimar and Nishat gardens",
        ],
        "travel_information": [
            "Currency: Indian rupee (INR)",
            "Language: Kashmiri, Hindi, Urdu & English",
            "Visa: e-Tourist visa available online for most nationalities",
        ],
        "is_featured": False,
    },
    {
        "name": "Andaman & Nicobar",
        "slug": "andaman",
        "country": "India",
        "region": "Islands",
        "short_description": "Turquoise seas, coral gardens and island days",
        "description": (
            "White-sand coves, coral gardens and waters clear enough to read the reef by. "
            "From the historic cells of Port Blair to the beaches of Swaraj Dweep, the "
            "Andamans are India's slowest, bluest escape."
        ),
        "hero_image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1540202404-a2f29016b523?auto=format&fit=crop&w=1200&q=80",
        ],
        "best_time": "November – April",
        "recommended_duration": "5–8 days",
        "highlights": ["Swaraj Dweep beaches", "Snorkelling trips", "Cellular Jail", "Radhanagar Beach"],
        "things_to_do": [
            "Snorkel the coral flats of Bharatpur",
            "Watch the sunset on Radhanagar Beach",
            "Attend the light-and-sound show at Cellular Jail",
            "Take a seaplane island hop between isles",
        ],
        "travel_information": [
            "Currency: Indian rupee (INR)",
            "Language: Hindi, Bengali, Tamil & English",
            "Permits: Indian citizens need none; foreign visitors apply on arrival",
        ],
        "is_featured": False,
    },
    {
        "name": "Himachal Pradesh",
        "slug": "himachal",
        "country": "India",
        "region": "North India",
        "short_description": "Shimla, Manali and the mountain trails of the north",
        "description": (
            "Colonial Shimla, the pine forests of Kullu and the high meadows of Solang. "
            "Himachal is where the plains turn to peaks — a journey of ropeways, "
            "apple orchards and tea rooms that feel a century old."
        ),
        "hero_image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1503775034369-8705d18e3a4a?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1530189627142-5bec1b282b47?auto=format&fit=crop&w=1200&q=80",
        ],
        "best_time": "March – June / Sep – Dec",
        "recommended_duration": "6–9 days",
        "highlights": ["Shimla Mall Road", "Manali old town", "Solang valley", "Rohtang Pass"],
        "things_to_do": [
            "Ride the Kalka–Shimla toy train",
            "Walk the Mall Road at dusk",
            "Paraglide in Solang valley",
            "Sip kahwa above Manali's apple orchards",
        ],
        "travel_information": [
            "Currency: Indian rupee (INR)",
            "Language: Hindi, Pahari & English",
            "Visa: e-Tourist visa available online for most nationalities",
        ],
        "is_featured": False,
    },
    {
        "name": "Tamil Nadu",
        "slug": "tamil-nadu",
        "country": "India",
        "region": "South India",
        "short_description": "Temple towers, Chettinad mansions and coastal Kanyakumari",
        "description": (
            "A sacred and storied south: the gopurams of Madurai, the sea temples of "
            "Rameswaram and the land's-end sunrise at Kanyakumari. Home ground for "
            "Explorers Choice — expect local hosts, temple food and timeless craft."
        ),
        "hero_image": "https://images.unsplash.com/photo-1692173248120-59547c3d4653?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1692173248120-59547c3d4653?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1788448351519-2734da0d1c8f?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1759134334610-488eb3937c82?auto=format&fit=crop&w=1200&q=80",
        ],
        "best_time": "November – March",
        "recommended_duration": "5–8 days",
        "highlights": ["Meenakshi temple", "Chettinad heritage", "Rameswaram shores", "Kanyakumari sunrise"],
        "things_to_do": [
            "Watch the Meenakshi temple at dusk",
            "Sleep in a restored Chettinad mansion",
            "Walk Rameswaram's longest sea corridor",
            "See the sunrise where three seas meet",
        ],
        "travel_information": [
            "Currency: Indian rupee (INR)",
            "Language: Tamil, English & Hindi",
            "Visa: e-Tourist visa available online for most nationalities",
        ],
        "is_featured": False,
    },
]

# ---------------------------------------------------------------------------
# Demo packages
# ---------------------------------------------------------------------------
PACKAGES = [
    {
        "name": "Rajasthan Heritage Trail",
        "slug": "rajasthan-heritage-trail",
        "destination_slug": "rajasthan",
        "short_description": "Jaipur, Udaipur, Jodhpur and Jaisalmer in one royal loop.",
        "description": (
            "A full royal loop — Jaipur's pink city, Udaipur's lake palaces, Jodhpur's "
            "blue lanes and a desert night at Jaisalmer — with heritage stays and "
            "local storytellers at every fort."
        ),
        "duration_days": 8,
        "duration_nights": 7,
        "starting_price": 68500.00,
        "currency": "INR",
        "hero_image": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
        ],
        "highlights": ["Amber Fort", "Lake Pichola", "Mehrangarh Fort", "Thar desert camp"],
        "included": [
            "7 nights heritage hotels & one desert camp",
            "Private air-conditioned transport",
            "Experienced local guides in each city",
            "Daily breakfast + 5 dinners",
            "Jaisalmer camel safari & desert dinner",
        ],
        "excluded": ["International/domestic flights", "Travel insurance", "Lunches & drinks"],
        "accommodation_summary": "Heritage havelis and palace hotels, plus a night in the Thar under canvas.",
        "transportation_summary": "Private AC SUV with a professional local driver throughout.",
        "meal_summary": "Daily breakfast, five dinners including a royal thali and a desert barbecue.",
        "cancellation_policy": (
            "Free cancellation up to 45 days before departure. 25% charge within 45–21 days, "
            "50% within 20–7 days, 100% within 6 days."
        ),
        "important_information": [
            "Summer heat is intense — pack light cottons and sun protection",
            "Minimum age: 6 years",
            "Temple visits require modest dress",
        ],
        "is_featured": True,
        "itinerary": [
            {"day_number": 1, "title": "Jaipur arrival", "description": "Pink city welcome and a rooftop first evening.", "activities": ["Arrival", "Rooftop dinner"], "meals": "Dinner", "accommodation": "Jaipur heritage hotel", "transportation": "Private transfer"},
            {"day_number": 2, "title": "Amber Fort & City Palace", "description": "Old Jaipur's forts, courtyards and bazaars.", "activities": ["Amber Fort", "City Palace", "Hawa Mahal"], "meals": "Breakfast, dinner", "accommodation": "Jaipur heritage hotel", "transportation": "Private AC SUV"},
            {"day_number": 3, "title": "Drive to Udaipur", "description": "Over the Aravali hills toward the lakes.", "activities": ["Scenic drive", "Evening lake walk"], "meals": "Breakfast, dinner", "accommodation": "Udaipur lake-side hotel", "transportation": "Private AC SUV"},
            {"day_number": 4, "title": "Lake city", "description": "City Palace, a boat on Lake Pichola and sunset ghats.", "activities": ["City Palace", "Lake Pichola boat"], "meals": "Breakfast, dinner", "accommodation": "Udaipur lake-side hotel", "transportation": "Boat & walking"},
            {"day_number": 5, "title": "Jodhpur blue city", "description": "Mehrangarh Fort above cobalt lanes.", "activities": ["Mehrangarh Fort", "Old city walk"], "meals": "Breakfast, dinner", "accommodation": "Jodhpur heritage hotel", "transportation": "Private AC SUV"},
            {"day_number": 6, "title": "To Jaisalmer", "description": "Desert roads, villages and the golden fort.", "activities": ["Jaisalmer Fort", "Haveli walk"], "meals": "Breakfast, dinner", "accommodation": "Jaisalmer heritage hotel", "transportation": "Private AC SUV"},
            {"day_number": 7, "title": "Thar desert night", "description": "Camel safari to a dune camp beneath the stars.", "activities": ["Camel safari", "Dune sunset", "Desert dinner"], "meals": "Breakfast, dinner", "accommodation": "Thar desert camp", "transportation": "Private AC SUV + camel"},
            {"day_number": 8, "title": "Departure", "description": "Return to Jaisalmer and onward connections.", "activities": ["Return drive", "Airport/station transfer"], "meals": "Breakfast", "accommodation": "—", "transportation": "Private transfer"},
        ],
        "faqs": [
            {"question": "Is the desert camp comfortable?", "answer": "Yes — proper beds in sturdy tents with a shared wash facility.", "sort_order": 1},
            {"question": "How far do we travel each day?", "answer": "The longest driving day is about six hours; most are three to four.", "sort_order": 2},
        ],
    },
    {
        "name": "Kerala Backwaters & Munnar",
        "slug": "kerala-backwaters-munnar",
        "destination_slug": "kerala",
        "short_description": "Tea hills, a houseboat night and Kochi's old port.",
        "description": (
            "Mists over Munnar's tea estates, a private night afloat on the backwaters "
            "and the spice-scented streets of Kochi — a gentle south-India classic."
        ),
        "duration_days": 7,
        "duration_nights": 6,
        "starting_price": 45500.00,
        "currency": "INR",
        "hero_image": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80",
        ],
        "highlights": ["Munnar tea estates", "Alleppey houseboat", "Kathakali evening", "Kochi fort"],
        "included": [
            "6 nights including a private houseboat",
            "All private transport & drivers",
            "Tea estate walk with a plantation host",
            "Daily breakfast + 4 dinners",
            "Kathakali performance & backwater cruise",
        ],
        "excluded": ["Flights to Kochi", "Travel insurance", "Lunches & drinks"],
        "accommodation_summary": "A mountain lodge in Munnar, backwater homestay and one night aboard a houseboat.",
        "transportation_summary": "Private tourist taxi with an experienced local driver.",
        "meal_summary": "Daily breakfast, four dinners including Kerala seafood and an in-houseboat meal.",
        "cancellation_policy": (
            "Free cancellation up to 30 days before departure. 25% charge within 30–15 days, "
            "50% within 14–7 days, 100% within 6 days."
        ),
        "important_information": [
            "Monsoon timber—pack light rain layers",
            "Minimum age: 5 years",
            "Houseboat cabin availability is limited — book early",
        ],
        "booking_mode": "INSTANT_BOOKING",
        "is_featured": True,
        "itinerary": [
            {"day_number": 1, "title": "Kochi arrival", "description": "Fort Kochi's colonial lanes and evening breeze.", "activities": ["Arrival", "Fort Kochi walk"], "meals": "Dinner", "accommodation": "Fort Kochi hotel", "transportation": "Private transfer"},
            {"day_number": 2, "title": "Kochi heritage", "description": "Chinese nets, Dutch houses and a Kathakali night.", "activities": ["Chinese fishing nets", "St Francis Church", "Kathakali evening"], "meals": "Breakfast, dinner", "accommodation": "Fort Kochi hotel", "transportation": "Walking & local ferry"},
            {"day_number": 3, "title": "To Munnar", "description": "Rise through spice country to the tea hills.", "activities": ["Scenic drive", "Tea garden arrival"], "meals": "Breakfast, dinner", "accommodation": "Munnar mountain lodge", "transportation": "Private taxi"},
            {"day_number": 4, "title": "Tea estates", "description": "A plantation walk and a waterfall trail.", "activities": ["Tea estate walk", "Eravikulam viewpoint"], "meals": "Breakfast, dinner", "accommodation": "Munnar mountain lodge", "transportation": "Private taxi"},
            {"day_number": 5, "title": "To Alleppey", "description": "Backwaters unwind beside paddy fields.", "activities": ["Backwater drive", "Village trail"], "meals": "Breakfast, dinner", "accommodation": "Alleppey backwater homestay", "transportation": "Private taxi"},
            {"day_number": 6, "title": "Houseboat night", "description": "A private boat, canals and a dinner prepared on board.", "activities": ["Houseboat cruise", "Sunset canal"], "meals": "Breakfast, lunch, dinner", "accommodation": "Private houseboat", "transportation": "Houseboat"},
            {"day_number": 7, "title": "Departure", "description": "Return to Kochi for onward connections.", "activities": ["Return to Kochi", "Transfer"], "meals": "Breakfast", "accommodation": "—", "transportation": "Private transfer"},
        ],
        "faqs": [
            {"question": "When is the best season?", "answer": "September to March is ideal; November–February is peak.", "sort_order": 1},
        ],
    },
    {
        "name": "Ladakh Expedition",
        "slug": "ladakh-expedition",
        "destination_slug": "ladakh",
        "short_description": "Monasteries, high passes and a night by Pangong Lake.",
        "description": (
            "An acclimatised high-altitude adventure — Leh's old town, Thiksey and Hemis "
            "monasteries, the Nubra dunes and a lakeside camp at Pangong."
        ),
        "duration_days": 8,
        "duration_nights": 7,
        "starting_price": 58000.00,
        "currency": "INR",
        "hero_image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80",
        ],
        "highlights": ["Pangong camp", "Thiksey monastery", "Nubra dunes", "Khardung La"],
        "included": [
            "7 nights including a Pangong lakeside camp",
            "All 4WD transport with local drivers",
            "Internal Ladakh permits & monastery entries",
            "Daily breakfast + 6 dinners",
            "Local high-altitude guide throughout",
        ],
        "excluded": ["Flights to Leh", "Travel insurance", "Lunches & drinks"],
        "accommodation_summary": "Guesthouses in Leh and Nubra plus a premium lakeside camp at Pangong.",
        "transportation_summary": "Tempo-traveller and 4WDs with experienced Ladakhi drivers.",
        "meal_summary": "Daily breakfast, six dinners with homely Ladakhi cooking.",
        "cancellation_policy": (
            "Free cancellation up to 45 days before departure. 30% charge within 45–21 days, "
            "100% within 20 days."
        ),
        "important_information": [
            "Leh is at 3,500m — we include full acclimatisation days",
            "Minimum age: 10 years",
            "Carry a warm layer even in summer",
        ],
        "is_featured": True,
        "itinerary": [
            {"day_number": 1, "title": "Leh arrival", "description": "Land, rest and let the altitude settle.", "activities": ["Arrival", "Rest day"], "meals": "Dinner", "accommodation": "Leh guesthouse", "transportation": "Airport transfer"},
            {"day_number": 2, "title": "Leh acclimatise", "description": "Old town lanes and the palace viewpoint.", "activities": ["Leh Palace", "Old town walk"], "meals": "Breakfast, dinner", "accommodation": "Leh guesthouse", "transportation": "Walking"},
            {"day_number": 3, "title": "Monasteries", "description": "Thiksey and Hemis at morning prayer time.", "activities": ["Thiksey monastery", "Hemis monastery"], "meals": "Breakfast, dinner", "accommodation": "Leh guesthouse", "transportation": "Private 4WD"},
            {"day_number": 4, "title": "Khardung La & Nubra", "description": "Across the pass to the dune fields of Nubra.", "activities": ["Khardung La", "Nubra dunes"], "meals": "Breakfast, dinner", "accommodation": "Nubra guesthouse", "transportation": "Private 4WD"},
            {"day_number": 5, "title": "Nubra valleys", "description": "Camel ride and the peaceful Diskit monastery.", "activities": ["Desert camel ride", "Diskit monastery"], "meals": "Breakfast, dinner", "accommodation": "Nubra guesthouse", "transportation": "Private 4WD"},
            {"day_number": 6, "title": "To Pangong", "description": "Climb Chang La and arrive at the blue lake.", "activities": ["Chang La pass", "Pangong sunset"], "meals": "Breakfast, dinner", "accommodation": "Pangong lakeside camp", "transportation": "Private 4WD"},
            {"day_number": 7, "title": "Pangong morning", "description": "Sunrise over the lake, then back to Leh.", "activities": ["Lake sunrise", "Return drive"], "meals": "Breakfast, dinner", "accommodation": "Leh guesthouse", "transportation": "Private 4WD"},
            {"day_number": 8, "title": "Departure", "description": "Fly out from Leh.", "activities": ["Airport transfer"], "meals": "Breakfast", "accommodation": "—", "transportation": "Private transfer"},
        ],
        "faqs": [
            {"question": "Do I need an acclimatisation day?", "answer": "Yes — day two is built for rest to keep everyone safe at altitude.", "sort_order": 1},
        ],
    },
    {
        "name": "Goa Sunset Escape",
        "slug": "goa-sunset-escape",
        "destination_slug": "goa",
        "short_description": "Beach days, Old Goa and a spice-farm lunch.",
        "description": (
            "A laid-back stretch of golden beaches and colonial charm — North Goa's sands, "
            "Old Goa's churches, palm-shaded spice farms and a Mandovi sunset cruise."
        ),
        "duration_days": 6,
        "duration_nights": 5,
        "starting_price": 32500.00,
        "currency": "INR",
        "hero_image": "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        ],
        "highlights": ["North Goa beaches", "Old Goa churches", "Spice farms", "Sunset cruise"],
        "included": [
            "5 nights beachfront hotels",
            "Private transfers & local driver",
            "Old Goa & Panaji city tour",
            "Daily breakfast + 3 dinners",
            "Mandovi river sunset cruise",
        ],
        "excluded": ["Flights to Goa", "Travel insurance", "Lunches & drinks"],
        "accommodation_summary": "Beachfront resorts and boutique shacks favourite in North Goa.",
        "transportation_summary": "Private AC car with a local driver for excursions.",
        "meal_summary": "Daily breakfast, three dinners including a beach barbecue.",
        "cancellation_policy": (
            "Free cancellation up to 30 days before departure. 25% charge within 30–15 days, "
            "100% within 14 days."
        ),
        "important_information": [
            "Goa is scorching in May — the Nov–Feb season is best",
            "Minimum age: 4 years",
        ],
        "booking_mode": "INSTANT_BOOKING",
        "is_featured": False,
        "itinerary": [
            {"day_number": 1, "title": "Goa arrival", "description": "Beach check-in and a golden first sunset.", "activities": ["Arrival", "Beach sunset"], "meals": "Dinner", "accommodation": "North Goa beach hotel", "transportation": "Private transfer"},
            {"day_number": 2, "title": "Old Goa", "description": "Whitewashed churches and Panaji's Latin quarter.", "activities": ["Basilica of Bom Jesus", "Panaji Latin quarter"], "meals": "Breakfast, dinner", "accommodation": "North Goa beach hotel", "transportation": "Private AC car"},
            {"day_number": 3, "title": "Spice farm", "description": "Ponda's plantations and a slow local lunch.", "activities": ["Spice farm tour", "Local lunch"], "meals": "Breakfast, lunch", "accommodation": "North Goa beach hotel", "transportation": "Private AC car"},
            {"day_number": 4, "title": "Beach day", "description": "Seashell hunts, beach shacks and nothing on the clock.", "activities": ["Free beach day"], "meals": "Breakfast", "accommodation": "North Goa beach hotel", "transportation": "—"},
            {"day_number": 5, "title": "Sunset cruise", "description": "The Mandovi at golden hour with dinner aboard.", "activities": ["Mandovi cruise", "Farewell dinner"], "meals": "Breakfast, dinner", "accommodation": "North Goa beach hotel", "transportation": "Cruise boat"},
            {"day_number": 6, "title": "Departure", "description": "Transfer to the airport.", "activities": ["Airport transfer"], "meals": "Breakfast", "accommodation": "—", "transportation": "Private transfer"},
        ],
        "faqs": [
            {"question": "Which beach do we stay near?", "answer": "North Goa's quieter stretches, close to Palolem-style calm yet reachable to all sights.", "sort_order": 1},
        ],
    },
    {
        "name": "Kashmir Valley Serenity",
        "slug": "kashmir-valley-serenity",
        "destination_slug": "kashmir",
        "short_description": "Dal Lake, Gulmarg meadows and Pahalgam's pine valleys.",
        "description": (
            "Houseboat mornings on Dal Lake, a gondola ride above Gulmarg and the slow "
            "pine trails of Pahalgam — Kashmir at its most restful, with a host who "
            "welcomes you like family."
        ),
        "duration_days": 7,
        "duration_nights": 6,
        "starting_price": 46000.00,
        "currency": "INR",
        "hero_image": "https://images.unsplash.com/photo-1503256207526-0d5d80fa2f47?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1503256207526-0d5d80fa2f47?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1530908295418-12c326d45a24?auto=format&fit=crop&w=1200&q=80",
        ],
        "highlights": ["Dal Lake houseboat", "Gulmarg gondola", "Pahalgam trails", "Mughal gardens"],
        "included": [
            "6 nights houseboat & valley hotels",
            "All private transport with experienced drivers",
            "Gulmarg gondola tickets",
            "Daily breakfast + 5 dinners",
            "Shikara ride & garden visits",
        ],
        "excluded": ["Flights to Srinagar", "Travel insurance", "Lunches & drinks"],
        "accommodation_summary": "A classic Dal Lake houseboat plus lakeside and valley hotels.",
        "transportation_summary": "Private AC cars throughout with vetted local drivers.",
        "meal_summary": "Daily breakfast, five dinners including a Wazwan-style feast night.",
        "cancellation_policy": (
            "Free cancellation up to 45 days before departure. 30% charge within 45–21 days, "
            "100% within 20 days."
        ),
        "important_information": [
            "Valley temperatures drop sharply at night — pack warm layers",
            "Minimum age: 6 years",
        ],
        "is_featured": False,
        "itinerary": [
            {"day_number": 1, "title": "Srinagar arrival", "description": "Settle onto a Dal Lake houseboat.", "activities": ["Arrival", "Houseboat check-in"], "meals": "Dinner", "accommodation": "Dal Lake houseboat", "transportation": "Private transfer"},
            {"day_number": 2, "title": "Lake morning", "description": "A shikara glide through the floating gardens.", "activities": ["Shikara ride", "Floating gardens"], "meals": "Breakfast, dinner", "accommodation": "Dal Lake houseboat", "transportation": "Shikara"},
            {"day_number": 3, "title": "Mughal gardens", "description": "Shalimar, Nishat and Chashme Shahi in blossom.", "activities": ["Shalimar Bagh", "Nishat Bagh"], "meals": "Breakfast, dinner", "accommodation": "Srinagar lake-view hotel", "transportation": "Private AC car"},
            {"day_number": 4, "title": "Gulmarg", "description": "Ride the gondola into meadows of green and white.", "activities": ["Gulmarg gondola", "Meadow walks"], "meals": "Breakfast, dinner", "accommodation": "Srinagar lake-view hotel", "transportation": "Private AC car"},
            {"day_number": 5, "title": "Pahalgam", "description": "Pine forests, the Lidder River and village tea.", "activities": ["Pahalgam valley", "Lidder walk"], "meals": "Breakfast, dinner", "accommodation": "Pahalgam resort", "transportation": "Private AC car"},
            {"day_number": 6, "title": "Valley trails", "description": "An unhurried morning before returning to Srinagar.", "activities": ["Trail walk", "Return to Srinagar"], "meals": "Breakfast, dinner", "accommodation": "Srinagar lake-view hotel", "transportation": "Private AC car"},
            {"day_number": 7, "title": "Departure", "description": "Transfer to Srinagar airport.", "activities": ["Airport transfer"], "meals": "Breakfast", "accommodation": "—", "transportation": "Private transfer"},
        ],
        "faqs": [
            {"question": "Is the valley safe to travel?", "answer": "The tourist circuits are open and well-run; we travel with vetted local hosts.", "sort_order": 1},
        ],
    },
    {
        "name": "Andaman Island Escape",
        "slug": "andaman-island-escape",
        "destination_slug": "andaman",
        "short_description": "Snorkelling, seaplane hops and island-lagoon days.",
        "description": (
            "Turquoise shallows, coral gardens and slow ferry hops between Port Blair and "
            "Swaraj Dweep — India's most dreamlike coastline, taken at island pace."
        ),
        "duration_days": 6,
        "duration_nights": 5,
        "starting_price": 52000.00,
        "currency": "INR",
        "hero_image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        ],
        "highlights": ["Swaraj Dweep beaches", "Snorkelling trips", "Cellular Jail", "Radhanagar Beach"],
        "included": [
            "5 nights island resorts",
            "Ferry transfers between islands",
            "Snorkelling gear & boat trips",
            "Daily breakfast + 4 dinners",
            "Cellular Jail light-and-sound show",
        ],
        "excluded": ["Flights to Port Blair", "Travel insurance", "Lunches & drinks"],
        "accommodation_summary": "Beachfront resorts on Port Blair and Swaraj Dweep.",
        "transportation_summary": "Private ferry / speedboat hops plus airport transfers.",
        "meal_summary": "Daily breakfast, four dinners with fresh catch by the sea.",
        "cancellation_policy": (
            "Free cancellation up to 30 days before departure. 30% charge within 30–15 days, "
            "100% within 14 days."
        ),
        "important_information": [
            "Ferry schedules vary — we hold flexible plans",
            "Minimum age: 6 years",
            "Coral-friendly sunscreen is encouraged",
        ],
        "is_featured": False,
        "itinerary": [
            {"day_number": 1, "title": "Port Blair arrival", "description": "Settle in near the harbour.", "activities": ["Arrival", "Harbour walk"], "meals": "Dinner", "accommodation": "Port Blair resort", "transportation": "Airport transfer"},
            {"day_number": 2, "title": "Cellular Jail", "description": "History and the night sound-and-light show.", "activities": ["Cellular Jail", "Light-and-sound show"], "meals": "Breakfast, dinner", "accommodation": "Port Blair resort", "transportation": "Private car"},
            {"day_number": 3, "title": "To Swaraj Dweep", "description": "Ferry across to the island of golden beaches.", "activities": ["Ferry crossing", "Radhanagar sunset"], "meals": "Breakfast, dinner", "accommodation": "Swaraj Dweep resort", "transportation": "Ferry"},
            {"day_number": 4, "title": "Snorkelling day", "description": "Coral flats and clear-water snorkelling.", "activities": ["Snorkelling trip", "Beach afternoon"], "meals": "Breakfast, dinner", "accommodation": "Swaraj Dweep resort", "transportation": "Speedboat"},
            {"day_number": 5, "title": "Island mornings", "description": "Slow breakfasts and a final swim before return.", "activities": ["Free morning", "Return ferry"], "meals": "Breakfast, dinner", "accommodation": "Port Blair resort", "transportation": "Ferry"},
            {"day_number": 6, "title": "Departure", "description": "Transfer to the airport.", "activities": ["Airport transfer"], "meals": "Breakfast", "accommodation": "—", "transportation": "Private transfer"},
        ],
        "faqs": [
            {"question": "Can non-swimmers snorkel?", "answer": "Yes — life jackets, guides and very shallow coral flats make it accessible.", "sort_order": 1},
        ],
    },
    {
        "name": "Himachal Mountain Trails",
        "slug": "himachal-mountain-trails",
        "destination_slug": "himachal",
        "short_description": "Shimla's toy train, Manali's valleys and Solang skies.",
        "description": (
            "From the Kalka–Shimla toy train to Manali's apple orchards and a paragliding "
            "morning in Solang — the classic north-India hill holiday."
        ),
        "duration_days": 7,
        "duration_nights": 6,
        "starting_price": 38000.00,
        "currency": "INR",
        "hero_image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1530189627142-5bec1b282b47?auto=format&fit=crop&w=1200&q=80",
        ],
        "highlights": ["Kalka–Shimla toy train", "Manali old town", "Solang valley", "Temple trails"],
        "included": [
            "6 nights mountain hotels",
            "Toy-train tickets & all transfers",
            "Solang valley activities",
            "Daily breakfast + 4 dinners",
            "Local mountain guide on trail days",
        ],
        "excluded": ["Flights/rail to Chandigarh", "Travel insurance", "Lunches & drinks"],
        "accommodation_summary": "Cosy colonial and mountain-view hotels in Shimla and Manali.",
        "transportation_summary": "Private AC car plus the scenic toy train to Shimla.",
        "meal_summary": "Daily breakfast, four dinners with Himachali specialities.",
        "cancellation_policy": (
            "Free cancellation up to 30 days before departure. 25% charge within 30–15 days, "
            "100% within 14 days."
        ),
        "important_information": [
            "Roads can be slow in the hills — we build in buffer time",
            "Minimum age: 5 years",
        ],
        "is_featured": False,
        "itinerary": [
            {"day_number": 1, "title": "Chandigarh start", "description": "Arrive and enjoy Chandigarh's lake gardens.", "activities": ["Arrival", "Lake garden evening"], "meals": "Dinner", "accommodation": "Chandigarh hotel", "transportation": "Arrival transfer"},
            {"day_number": 2, "title": "Toy train to Shimla", "description": "The little red train up the Kalka–Shimla line.", "activities": ["Toy train ride", "Mall Road walk"], "meals": "Breakfast, dinner", "accommodation": "Shimla colonial hotel", "transportation": "Toy train"},
            {"day_number": 3, "title": "Shimla old town", "description": "Christ Church, Ridge walks and cafés.", "activities": ["The Ridge", "Christ Church", "Old bazaar"], "meals": "Breakfast, dinner", "accommodation": "Shimla colonial hotel", "transportation": "Walking"},
            {"day_number": 4, "title": "To Manali", "description": "Kullu valley drives and riverside stops.", "activities": ["Scenic drive", "Kullu valley"], "meals": "Breakfast, dinner", "accommodation": "Manali mountain hotel", "transportation": "Private AC car"},
            {"day_number": 5, "title": "Manali old town", "description": "Hadimba temple and apple-orchard walks.", "activities": ["Hadimba temple", "Orchard walk"], "meals": "Breakfast, dinner", "accommodation": "Manali mountain hotel", "transportation": "Private AC car"},
            {"day_number": 6, "title": "Solang valley", "description": "Paragliding and meadow time above Manali.", "activities": ["Solang valley", "Paragliding"], "meals": "Breakfast, dinner", "accommodation": "Manali mountain hotel", "transportation": "Private AC car"},
            {"day_number": 7, "title": "Departure", "description": "Return to Chandigarh for onward connections.", "activities": ["Return drive", "Transfer"], "meals": "Breakfast", "accommodation": "—", "transportation": "Private transfer"},
        ],
        "faqs": [
            {"question": "Is the toy train journey worth it?", "answer": "Absolutely — the Kalka–Shimla line is a UNESCO heritage route.", "sort_order": 1},
        ],
    },
    {
        "name": "Tamil Nadu Temple Trail",
        "slug": "tamil-nadu-temple-trail",
        "destination_slug": "tamil-nadu",
        "short_description": "Madurai's towers, Chettinad mansions and Kanyakumari's seas.",
        "description": (
            "South India's sacred high roads — Meenakshi's dusk lamps, Rameswaram's long "
            "corridor and the windswept meeting of three seas at Kanyakumari, on the "
            "agency's own home ground."
        ),
        "duration_days": 6,
        "duration_nights": 5,
        "starting_price": 36500.00,
        "currency": "INR",
        "hero_image": "https://images.unsplash.com/photo-1692173248120-59547c3d4653?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1692173248120-59547c3d4653?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1788448351519-2734da0d1c8f?auto=format&fit=crop&w=1200&q=80",
        ],
        "highlights": ["Meenakshi temple", "Chettinad mansions", "Rameswaram shore", "Kanyakumari sunrise"],
        "included": [
            "5 nights heritage & temple-town hotels",
            "All private transport with local drivers",
            "Temple entry & guided visits",
            "Daily breakfast + 4 dinners",
            "Chettinad mansion stay",
        ],
        "excluded": ["Flights/train to Madurai", "Travel insurance", "Lunches & drinks"],
        "accommodation_summary": "A restored Chettinad mansion plus comfortable temple-town stays.",
        "transportation_summary": "Private AC car throughout with knowledgeable local drivers.",
        "meal_summary": "Daily breakfast, four dinners with pure South Indian fare.",
        "cancellation_policy": (
            "Free cancellation up to 30 days before departure. 25% charge within 30–15 days, "
            "100% within 14 days."
        ),
        "important_information": [
            "Temples require modest dress and footwear removal",
            "Minimum age: 5 years",
            "Kanyakumari sunset is a must — we time it well",
        ],
        "is_featured": False,
        "itinerary": [
            {"day_number": 1, "title": "Madurai arrival", "description": "Arrive and watch Meenakshi at evening lamps.", "activities": ["Arrival", "Temple dusk"], "meals": "Dinner", "accommodation": "Madurai hotel", "transportation": "Private transfer"},
            {"day_number": 2, "title": "Madurai temples", "description": "The tower city, its market and its famous temple food.", "activities": ["Meenakshi temple", "Local market"], "meals": "Breakfast, dinner", "accommodation": "Madurai hotel", "transportation": "Walking & auto"},
            {"day_number": 3, "title": "Chettinad", "description": "Palatial mansions, handloom and fiery Chettinad curry.", "activities": ["Mansion tours", "Handloom visit"], "meals": "Breakfast, dinner", "accommodation": "Chettinad heritage mansion", "transportation": "Private AC car"},
            {"day_number": 4, "title": "Rameswaram", "description": "The southern rails of the Ramanathaswamy temple.", "activities": ["Sea corridor", "Shore temples"], "meals": "Breakfast, dinner", "accommodation": "Rameswaram hotel", "transportation": "Private AC car"},
            {"day_number": 5, "title": "Kanyakumari", "description": "India's land's-end — sunrise, three seas and sunset rocks.", "activities": ["Vivekananda Rock", "Three-seas viewpoint"], "meals": "Breakfast, dinner", "accommodation": "Kanyakumari hotel", "transportation": "Private AC car"},
            {"day_number": 6, "title": "Departure", "description": "Return to Kanyakumari/Trivandrum railhead for onward travel.", "activities": ["Return drive", "Transfer"], "meals": "Breakfast", "accommodation": "—", "transportation": "Private transfer"},
        ],
        "faqs": [
            {"question": "Is this a religious-only trip?", "answer": "It's a heritage and culture journey — the food and architecture are highlights too.", "sort_order": 1},
        ],
    },
]


# ---------------------------------------------------------------------------
# Demo hotels (mirrors the frontend's /src/data/hotels.ts demo catalogue)
# ---------------------------------------------------------------------------
HOTELS = [
    {
        "slug": "taj-lake-palace-udaipur",
        "name": "Taj Lake Palace",
        "location": "Udaipur, Rajasthan",
        "destination": "Rajasthan",
        "tagline": "A floating marble palace on Lake Pichola",
        "description": "Set on a 4-acre island in Lake Pichola, the Taj Lake Palace is a breathtaking 18th-century marble palace. With intricate carved jharokhas, lush courtyards and panoramic lake views, it offers an unforgettable royal experience.",
        "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1600&q=80",
        "price_per_night": 28500,
        "currency": "INR",
        "amenities": ["Lake-view rooms", "Spa & wellness", "Fine dining", "Heritage walks", "Boat transfers"],
        "highlights": ["Floating island location", "Royal Rajasthani decor", "Sunset boat rides", "Jiva Spa"],
        "is_published": True,
    },
    {
        "slug": "kumarakom-lake-resort-kerala",
        "name": "Kumarakom Lake Resort",
        "location": "Kumarakom, Kerala",
        "destination": "Kerala",
        "tagline": "Kerala backwater luxury amid coconut groves",
        "description": "Nestled on the banks of Lake Vembanad, this resort blends traditional Kerala architecture with modern luxury. Wake to the sound of kingfishers, cruise the backwaters on a private houseboat and indulge in authentic Ayurvedic therapies.",
        "image": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=1600&q=80",
        "price_per_night": 18000,
        "currency": "INR",
        "amenities": ["Backwater views", "Ayurvedic spa", "Infinity pool", "Houseboat cruise", "Yoga sessions"],
        "highlights": ["Private backwater access", "Traditional Kerala architecture", "Authentic Ayurveda", "Bird-watching tours"],
        "is_published": True,
    },
    {
        "slug": "oberoi-udaivilas-udaipur",
        "name": "The Oberoi Udaivilas",
        "location": "Udaipur, Rajasthan",
        "destination": "Rajasthan",
        "tagline": "Where Mughal grandeur meets modern opulence",
        "description": "Spread across 50 acres on the banks of Lake Pichola, The Oberoi Udaivilas features domed pavilions, sweeping courtyards and sunlit corridors. Every room offers stunning views of the Aravalli hills or the lake.",
        "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=1600&q=80",
        "price_per_night": 42000,
        "currency": "INR",
        "amenities": ["Lake-facing suites", "Temperature-controlled pool", "Oberoi Spa", "Cultural performances", "Private dining"],
        "highlights": ["Architectural masterpiece", "Personal Oberoi concierge", "Sunset cocktails by the lake", "Rajasthani folk evenings"],
        "is_published": True,
    },
    {
        "slug": "wildflower-hall-manali",
        "name": "Wildflower Hall",
        "location": "Manali, Himachal Pradesh",
        "destination": "Himachal Pradesh",
        "tagline": "A Himalayan retreat above the clouds",
        "description": "Perched at 8,250 ft amid cedar forests and snow-capped peaks, Wildflower Hall offers an enchanting escape. With panoramic mountain views, an award-winning spa and adventure activities, it's the ultimate Himalayan luxury resort.",
        "image": "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=1600&q=80",
        "price_per_night": 32000,
        "currency": "INR",
        "amenities": ["Mountain-view rooms", "Heated indoor pool", "Spa & fitness", "Mountain biking", "Nature walks"],
        "highlights": ["8,250 ft altitude", "Cedar forest setting", "Adventure activities", "Star-gazing evenings"],
        "is_published": True,
    },
    {
        "slug": "taj-fort-aguada-goa",
        "name": "Taj Fort Aguada",
        "location": "Sinquerim, Goa",
        "destination": "Goa",
        "tagline": "A Portuguese-era fort turned beachside luxury resort",
        "description": "Built within the ramparts of a 16th-century Portuguese fortress overlooking the Arabian Sea, Taj Fort Aguada combines colonial heritage with beachside luxury. Lush gardens, private beach access and world-class dining await.",
        "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1600&q=80",
        "price_per_night": 15000,
        "currency": "INR",
        "amenities": ["Beachfront", "Heritage wings", "Jiva Spa", "Water sports", "Multiple restaurants"],
        "highlights": ["16th-century fort setting", "Private beach access", "Portuguese architecture", "Sunset bar by the sea"],
        "is_published": True,
    },
    {
        "slug": "zostel-manali",
        "name": "The Hosteller Manali",
        "location": "Old Manali, Himachal Pradesh",
        "destination": "Himachal Pradesh",
        "tagline": "Budget-friendly mountain stays with stunning valley views",
        "description": "Nestled in the heart of Old Manali with breathtaking views of the Beas River valley, this charming boutique stay offers cozy rooms, a rooftop cafe, and easy access to trails and cafes. Perfect for solo travellers and couples.",
        "image": "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?auto=format&fit=crop&w=1600&q=80",
        "price_per_night": 3500,
        "currency": "INR",
        "amenities": ["Valley-view rooms", "Rooftop cafe", "Free Wi-Fi", "Lounge area", "Trekking helpdesk"],
        "highlights": ["Old Manali location", "Budget luxury", "River valley views", "Walking distance to cafes"],
        "is_published": True,
    },
    {
        "slug": "coconut-lagoon-kerala",
        "name": "Coconut Lagoon",
        "location": "Kumarakom, Kerala",
        "destination": "Kerala",
        "tagline": "A heritage retreat accessible only by boat",
        "description": "Tucked away on a peaceful island in the Vembanad backwaters, Coconut Lagoon is reachable only by country boat. With traditional Kerala tharavads, a butterfly garden and Ayurvedic centre, it's an eco-paradise.",
        "image": "https://images.unsplash.com/photo-1596178065887-1198b6148b2b?auto=format&fit=crop&w=1600&q=80",
        "price_per_night": 12000,
        "currency": "INR",
        "amenities": ["Backwater access", "Ayurvedic centre", "Butterfly garden", "Country boat transfers", "Organic kitchen"],
        "highlights": ["Island-only access", "Heritage Kerala tharavads", "Eco-friendly resort", "Kayaking & canoeing"],
        "is_published": True,
    },
    {
        "slug": "rambagh-palace-jaipur",
        "name": "Rambagh Palace",
        "location": "Jaipur, Rajasthan",
        "destination": "Rajasthan",
        "tagline": "The former residence of the Maharaja of Jaipur",
        "description": "Once the home of the Maharaja of Jaipur, Rambagh Palace is a living heritage property set in 47 acres of manicured gardens. With peacocks roaming the grounds and exquisite Art Deco interiors, it epitomises royal Rajasthani hospitality.",
        "image": "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?auto=format&fit=crop&w=1600&q=80",
        "price_per_night": 35000,
        "currency": "INR",
        "amenities": ["Palace suites", "Heritage walks", "Spa & salon", "Golf course", "Royal dining"],
        "highlights": ["Former royal residence", "47-acre gardens", "Peacock-spotting", "Art Deco interiors"],
        "is_published": True,
    },
]


BROKEN_IMAGE_MARKERS = (
    "photo-1583430788308-9fe346a8e869",
    "photo-1506461883276-59f2ebe600eb",
    "photo-1600100598826-6b4f6ffe5d32",
)


def _is_broken_image(url: str) -> bool:
    return any(marker in url for marker in BROKEN_IMAGE_MARKERS)


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Upsert destinations
        slug_to_destination: dict[str, Destination] = {}
        for d in DESTINATIONS:
            existing = db.scalars(select(Destination).where(Destination.slug == d["slug"])).first()
            if existing:
                if existing.hero_image and _is_broken_image(existing.hero_image):
                    existing.hero_image = d["hero_image"]
                if existing.gallery:
                    existing.gallery = [
                        d["gallery"][0] if _is_broken_image(image) else image
                        for image in existing.gallery
                    ]
                slug_to_destination[d["slug"]] = existing
                continue
            destination = Destination(**d)
            db.add(destination)
            db.flush()
            slug_to_destination[d["slug"]] = destination

        # Upsert packages + itinerary
        for package_data in PACKAGES:
            existing_pkg = db.scalars(
                select(Package).where(Package.slug == package_data["slug"])
            ).first()
            if existing_pkg:
                if existing_pkg.hero_image and _is_broken_image(existing_pkg.hero_image):
                    existing_pkg.hero_image = package_data["hero_image"]
                if existing_pkg.gallery:
                    existing_pkg.gallery = [
                        package_data["gallery"][0] if _is_broken_image(image) else image
                        for image in existing_pkg.gallery
                    ]
                continue

            data = package_data.copy()
            destination = slug_to_destination[data.pop("destination_slug")]
            itinerary = data.pop("itinerary")
            faqs = data.pop("faqs")
            package = Package(destination_id=destination.id, **data)
            package.itinerary = [ItineraryDay(**day) for day in itinerary]
            package.faqs = [PackageFaq(**faq) for faq in faqs]
            db.add(package)

        # Upsert demo hotels (assigned to a staff account acting as the listing owner)
        owner = db.scalars(
            select(User).where(User.role.in_(["ADMIN", "MANAGER"])).limit(1)
        ).first()
        if owner is None:
            owner = db.scalars(select(User).limit(1)).first()
        if owner is None:
            owner = User(email="demo@explorerschoice.in", full_name="Explorers Choice", role="CUSTOMER")
            db.add(owner)
            db.flush()
        for hotel_data in HOTELS:
            existing_hotel = db.scalars(
                select(Hotel).where(Hotel.slug == hotel_data["slug"])
            ).first()
            if existing_hotel:
                continue
            db.add(Hotel(owner_id=owner.id, **hotel_data))

        db.commit()
        print("Seed complete")
        print(f"   Destinations: {db.query(Destination).count()}")
        print(f"   Packages:     {db.query(Package).count()}")
        print(f"   Itinerary:    {db.query(ItineraryDay).count()}")
        print(f"   Package FAQs: {db.query(PackageFaq).count()}")
        print(f"   Hotels:       {db.query(Hotel).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()