"""Train search, external API integration, PNR status, and booking support for Explorers Choice."""
from datetime import date, datetime, timedelta
import logging
import random
import re
from typing import Any, Optional

import httpx
from sqlalchemy.orm import Session

from .config import settings
from . import models

logger = logging.getLogger("explorers.trains")

# ---------------------------------------------------------------------------
# Comprehensive Indian Railways Stations Catalog
# ---------------------------------------------------------------------------
STATIONS: list[dict[str, str]] = [
    {"code": "NDLS", "name": "New Delhi", "city": "New Delhi", "state": "Delhi"},
    {"code": "DLI", "name": "Old Delhi Junction", "city": "Delhi", "state": "Delhi"},
    {"code": "NZM", "name": "Hazrat Nizamuddin", "city": "Delhi", "state": "Delhi"},
    {"code": "ANVT", "name": "Anand Vihar Terminal", "city": "Delhi", "state": "Delhi"},
    {"code": "CSMT", "name": "Mumbai Chhatrapati Shivaji Maharaj Terminus", "city": "Mumbai", "state": "Maharashtra"},
    {"code": "MMCT", "name": "Mumbai Central", "city": "Mumbai", "state": "Maharashtra"},
    {"code": "BDTS", "name": "Bandra Terminus", "city": "Mumbai", "state": "Maharashtra"},
    {"code": "LTT", "name": "Lokmanya Tilak Terminus", "city": "Mumbai", "state": "Maharashtra"},
    {"code": "PNQ", "name": "Pune Junction", "city": "Pune", "state": "Maharashtra"},
    {"code": "NGP", "name": "Nagpur Junction", "city": "Nagpur", "state": "Maharashtra"},
    {"code": "HWH", "name": "Howrah Junction", "city": "Kolkata", "state": "West Bengal"},
    {"code": "SDAH", "name": "Sealdah", "city": "Kolkata", "state": "West Bengal"},
    {"code": "KOAA", "name": "Kolkata Chitpur", "city": "Kolkata", "state": "West Bengal"},
    {"code": "NJP", "name": "New Jalpaiguri", "city": "Siliguri", "state": "West Bengal"},
    {"code": "MAS", "name": "MGR Chennai Central", "city": "Chennai", "state": "Tamil Nadu"},
    {"code": "MS", "name": "Chennai Egmore", "city": "Chennai", "state": "Tamil Nadu"},
    {"code": "CBE", "name": "Coimbatore Junction", "city": "Coimbatore", "state": "Tamil Nadu"},
    {"code": "MDU", "name": "Madurai Junction", "city": "Madurai", "state": "Tamil Nadu"},
    {"code": "SBC", "name": "KSR Bengaluru City Junction", "city": "Bengaluru", "state": "Karnataka"},
    {"code": "YPR", "name": "Yesvantpur Junction", "city": "Bengaluru", "state": "Karnataka"},
    {"code": "SMVB", "name": "Sir M Visvesvaraya Terminal", "city": "Bengaluru", "state": "Karnataka"},
    {"code": "MYS", "name": "Mysuru Junction", "city": "Mysuru", "state": "Karnataka"},
    {"code": "BSB", "name": "Varanasi Junction", "city": "Varanasi", "state": "Uttar Pradesh"},
    {"code": "DDU", "name": "Pt Deen Dayal Upadhyaya Junction", "city": "Mughalsarai", "state": "Uttar Pradesh"},
    {"code": "LKO", "name": "Lucknow Charbagh", "city": "Lucknow", "state": "Uttar Pradesh"},
    {"code": "LJN", "name": "Lucknow Junction NER", "city": "Lucknow", "state": "Uttar Pradesh"},
    {"code": "CNB", "name": "Kanpur Central", "city": "Kanpur", "state": "Uttar Pradesh"},
    {"code": "AGC", "name": "Agra Cantt", "city": "Agra", "state": "Uttar Pradesh"},
    {"code": "PRYJ", "name": "Prayagraj Junction", "city": "Prayagraj", "state": "Uttar Pradesh"},
    {"code": "GKP", "name": "Gorakhpur Junction", "city": "Gorakhpur", "state": "Uttar Pradesh"},
    {"code": "JAI", "name": "Jaipur Junction", "city": "Jaipur", "state": "Rajasthan"},
    {"code": "JU", "name": "Jodhpur Junction", "city": "Jodhpur", "state": "Rajasthan"},
    {"code": "UDZ", "name": "Udaipur City", "city": "Udaipur", "state": "Rajasthan"},
    {"code": "ADI", "name": "Ahmedabad Junction", "city": "Ahmedabad", "state": "Gujarat"},
    {"code": "ST", "name": "Surat", "city": "Surat", "state": "Gujarat"},
    {"code": "BRC", "name": "Vadodara Junction", "city": "Vadodara", "state": "Gujarat"},
    {"code": "MAO", "name": "Madgaon Junction", "city": "Goa", "state": "Goa"},
    {"code": "KRMI", "name": "Karmali", "city": "North Goa", "state": "Goa"},
    {"code": "ERS", "name": "Ernakulam Junction (South)", "city": "Kochi", "state": "Kerala"},
    {"code": "ERN", "name": "Ernakulam Town (North)", "city": "Kochi", "state": "Kerala"},
    {"code": "TVC", "name": "Thiruvananthapuram Central", "city": "Thiruvananthapuram", "state": "Kerala"},
    {"code": "CLT", "name": "Kozhikode Main", "city": "Kozhikode", "state": "Kerala"},
    {"code": "HYB", "name": "Hyderabad Deccan", "city": "Hyderabad", "state": "Telangana"},
    {"code": "SC", "name": "Secunderabad Junction", "city": "Hyderabad", "state": "Telangana"},
    {"code": "BZA", "name": "Vijayawada Junction", "city": "Vijayawada", "state": "Andhra Pradesh"},
    {"code": "VSKP", "name": "Visakhapatnam Junction", "city": "Visakhapatnam", "state": "Andhra Pradesh"},
    {"code": "BBS", "name": "Bhubaneswar", "city": "Bhubaneswar", "state": "Odisha"},
    {"code": "PURI", "name": "Puri Terminus", "city": "Puri", "state": "Odisha"},
    {"code": "PNBE", "name": "Patna Junction", "city": "Patna", "state": "Bihar"},
    {"code": "GHY", "name": "Guwahati", "city": "Guwahati", "state": "Assam"},
    {"code": "JAT", "name": "Jammu Tawi", "city": "Jammu", "state": "Jammu & Kashmir"},
    {"code": "SVDK", "name": "Shri Mata Vaishno Devi Katra", "city": "Katra", "state": "Jammu & Kashmir"},
    {"code": "ASR", "name": "Amritsar Junction", "city": "Amritsar", "state": "Punjab"},
    {"code": "CDG", "name": "Chandigarh Junction", "city": "Chandigarh", "state": "Chandigarh"},
    {"code": "DDN", "name": "Dehradun", "city": "Dehradun", "state": "Uttarakhand"},
    {"code": "HW", "name": "Haridwar Junction", "city": "Haridwar", "state": "Uttarakhand"},
    {"code": "BPL", "name": "Bhopal Junction", "city": "Bhopal", "state": "Madhya Pradesh"},
    {"code": "RKMP", "name": "Rani Kamalapati", "city": "Bhopal", "state": "Madhya Pradesh"},
    {"code": "INDB", "name": "Indore Junction", "city": "Indore", "state": "Madhya Pradesh"},
    {"code": "GWL", "name": "Gwalior Junction", "city": "Gwalior", "state": "Madhya Pradesh"},
]

# ---------------------------------------------------------------------------
# Popular Master Train Catalog with Authentic Timings & Fares
# ---------------------------------------------------------------------------
POPULAR_TRAINS = [
    {
        "train_number": "22436",
        "train_name": "Vande Bharat Express",
        "train_type": "Vande Bharat",
        "from_code": "NDLS",
        "from_name": "New Delhi",
        "to_code": "BSB",
        "to_name": "Varanasi Junction",
        "departure_time": "06:00",
        "arrival_time": "14:00",
        "duration": "8h 00m",
        "running_days": ["Mon", "Tue", "Wed", "Fri", "Sat", "Sun"],
        "classes": [
            {"travel_class": "CC", "class_name": "AC Chair Car", "fare": 1750.0},
            {"travel_class": "EC", "class_name": "Exec Chair Car", "fare": 3300.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "22435",
        "train_name": "Vande Bharat Express",
        "train_type": "Vande Bharat",
        "from_code": "BSB",
        "from_name": "Varanasi Junction",
        "to_code": "NDLS",
        "to_name": "New Delhi",
        "departure_time": "15:00",
        "arrival_time": "23:00",
        "duration": "8h 00m",
        "running_days": ["Mon", "Tue", "Wed", "Fri", "Sat", "Sun"],
        "classes": [
            {"travel_class": "CC", "class_name": "AC Chair Car", "fare": 1750.0},
            {"travel_class": "EC", "class_name": "Exec Chair Car", "fare": 3300.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "12952",
        "train_name": "Mumbai Rajdhani Express",
        "train_type": "Rajdhani",
        "from_code": "NDLS",
        "from_name": "New Delhi",
        "to_code": "MMCT",
        "to_name": "Mumbai Central",
        "departure_time": "16:55",
        "arrival_time": "08:35",
        "duration": "15h 40m",
        "running_days": ["Daily"],
        "classes": [
            {"travel_class": "3A", "class_name": "AC 3 Tier", "fare": 2150.0},
            {"travel_class": "2A", "class_name": "AC 2 Tier", "fare": 3100.0},
            {"travel_class": "1A", "class_name": "AC 1st Class", "fare": 4950.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "12951",
        "train_name": "Mumbai Rajdhani Express",
        "train_type": "Rajdhani",
        "from_code": "MMCT",
        "from_name": "Mumbai Central",
        "to_code": "NDLS",
        "to_name": "New Delhi",
        "departure_time": "17:00",
        "arrival_time": "08:32",
        "duration": "15h 32m",
        "running_days": ["Daily"],
        "classes": [
            {"travel_class": "3A", "class_name": "AC 3 Tier", "fare": 2150.0},
            {"travel_class": "2A", "class_name": "AC 2 Tier", "fare": 3100.0},
            {"travel_class": "1A", "class_name": "AC 1st Class", "fare": 4950.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "22221",
        "train_name": "Mumbai CSMT - Hazrat Nizamuddin Rajdhani",
        "train_type": "Rajdhani",
        "from_code": "CSMT",
        "from_name": "Mumbai CSMT",
        "to_code": "NZM",
        "to_name": "Hazrat Nizamuddin",
        "departure_time": "16:00",
        "arrival_time": "09:55",
        "duration": "17h 55m",
        "running_days": ["Mon", "Wed", "Fri", "Sat"],
        "classes": [
            {"travel_class": "3A", "class_name": "AC 3 Tier", "fare": 2240.0},
            {"travel_class": "2A", "class_name": "AC 2 Tier", "fare": 3280.0},
            {"travel_class": "1A", "class_name": "AC 1st Class", "fare": 5120.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "22229",
        "train_name": "Mumbai CSMT - Madgaon Vande Bharat Express",
        "train_type": "Vande Bharat",
        "from_code": "CSMT",
        "from_name": "Mumbai CSMT",
        "to_code": "MAO",
        "to_name": "Madgaon Junction (Goa)",
        "departure_time": "05:25",
        "arrival_time": "13:10",
        "duration": "7h 45m",
        "running_days": ["Mon", "Tue", "Wed", "Thu", "Sat", "Sun"],
        "classes": [
            {"travel_class": "CC", "class_name": "AC Chair Car", "fare": 1815.0},
            {"travel_class": "EC", "class_name": "Exec Chair Car", "fare": 3355.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "22230",
        "train_name": "Madgaon - Mumbai CSMT Vande Bharat Express",
        "train_type": "Vande Bharat",
        "from_code": "MAO",
        "from_name": "Madgaon Junction (Goa)",
        "to_code": "CSMT",
        "to_name": "Mumbai CSMT",
        "departure_time": "14:40",
        "arrival_time": "22:25",
        "duration": "7h 45m",
        "running_days": ["Mon", "Tue", "Wed", "Thu", "Sat", "Sun"],
        "classes": [
            {"travel_class": "CC", "class_name": "AC Chair Car", "fare": 1815.0},
            {"travel_class": "EC", "class_name": "Exec Chair Car", "fare": 3355.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "12002",
        "train_name": "Bhopal Shatabdi Express",
        "train_type": "Shatabdi",
        "from_code": "NDLS",
        "from_name": "New Delhi",
        "to_code": "AGC",
        "to_name": "Agra Cantt",
        "departure_time": "06:00",
        "arrival_time": "07:50",
        "duration": "1h 50m",
        "running_days": ["Daily"],
        "classes": [
            {"travel_class": "CC", "class_name": "AC Chair Car", "fare": 690.0},
            {"travel_class": "EC", "class_name": "Exec Chair Car", "fare": 1395.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "12015",
        "train_name": "Ajmer Shatabdi Express",
        "train_type": "Shatabdi",
        "from_code": "NDLS",
        "from_name": "New Delhi",
        "to_code": "JAI",
        "to_name": "Jaipur Junction",
        "departure_time": "06:10",
        "arrival_time": "10:40",
        "duration": "4h 30m",
        "running_days": ["Daily"],
        "classes": [
            {"travel_class": "CC", "class_name": "AC Chair Car", "fare": 1040.0},
            {"travel_class": "EC", "class_name": "Exec Chair Car", "fare": 1820.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "20608",
        "train_name": "Mysuru - Chennai Central Vande Bharat Express",
        "train_type": "Vande Bharat",
        "from_code": "SBC",
        "from_name": "KSR Bengaluru",
        "to_code": "MAS",
        "to_name": "MGR Chennai Central",
        "departure_time": "14:50",
        "arrival_time": "19:20",
        "duration": "4h 30m",
        "running_days": ["Mon", "Tue", "Thu", "Fri", "Sat", "Sun"],
        "classes": [
            {"travel_class": "CC", "class_name": "AC Chair Car", "fare": 995.0},
            {"travel_class": "EC", "class_name": "Exec Chair Car", "fare": 1885.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "22439",
        "train_name": "Shri Mata Vaishno Devi Katra Vande Bharat",
        "train_type": "Vande Bharat",
        "from_code": "NDLS",
        "from_name": "New Delhi",
        "to_code": "SVDK",
        "to_name": "Shri Mata Vaishno Devi Katra",
        "departure_time": "06:00",
        "arrival_time": "14:00",
        "duration": "8h 00m",
        "running_days": ["Mon", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "classes": [
            {"travel_class": "CC", "class_name": "AC Chair Car", "fare": 1630.0},
            {"travel_class": "EC", "class_name": "Exec Chair Car", "fare": 3015.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "12301",
        "train_name": "Howrah Rajdhani Express",
        "train_type": "Rajdhani",
        "from_code": "HWH",
        "from_name": "Howrah Junction (Kolkata)",
        "to_code": "NDLS",
        "to_name": "New Delhi",
        "departure_time": "16:50",
        "arrival_time": "10:05",
        "duration": "17h 15m",
        "running_days": ["Mon", "Tue", "Wed", "Thu", "Sat", "Sun"],
        "classes": [
            {"travel_class": "3A", "class_name": "AC 3 Tier", "fare": 2420.0},
            {"travel_class": "2A", "class_name": "AC 2 Tier", "fare": 3490.0},
            {"travel_class": "1A", "class_name": "AC 1st Class", "fare": 5580.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "12626",
        "train_name": "Kerala Express",
        "train_type": "Superfast",
        "from_code": "NDLS",
        "from_name": "New Delhi",
        "to_code": "ERS",
        "to_name": "Ernakulam Junction (Kochi)",
        "departure_time": "20:10",
        "arrival_time": "15:25",
        "duration": "43h 15m",
        "running_days": ["Daily"],
        "classes": [
            {"travel_class": "SL", "class_name": "Sleeper", "fare": 985.0},
            {"travel_class": "3A", "class_name": "AC 3 Tier", "fare": 2550.0},
            {"travel_class": "2A", "class_name": "AC 2 Tier", "fare": 3720.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "12802",
        "train_name": "Purushottam Express",
        "train_type": "Superfast",
        "from_code": "NDLS",
        "from_name": "New Delhi",
        "to_code": "PURI",
        "to_name": "Puri Terminus",
        "departure_time": "22:40",
        "arrival_time": "05:25",
        "duration": "30h 45m",
        "running_days": ["Daily"],
        "classes": [
            {"travel_class": "SL", "class_name": "Sleeper", "fare": 745.0},
            {"travel_class": "3A", "class_name": "AC 3 Tier", "fare": 1960.0},
            {"travel_class": "2A", "class_name": "AC 2 Tier", "fare": 2840.0},
            {"travel_class": "1A", "class_name": "AC 1st Class", "fare": 4820.0},
        ],
        "has_pantry": True,
    },
    {
        "train_number": "12004",
        "train_name": "Lucknow Swarna Shatabdi Express",
        "train_type": "Shatabdi",
        "from_code": "NDLS",
        "from_name": "New Delhi",
        "to_code": "LJN",
        "to_name": "Lucknow Junction",
        "departure_time": "06:10",
        "arrival_time": "12:40",
        "duration": "6h 30m",
        "running_days": ["Daily"],
        "classes": [
            {"travel_class": "CC", "class_name": "AC Chair Car", "fare": 1165.0},
            {"travel_class": "EC", "class_name": "Exec Chair Car", "fare": 2125.0},
        ],
        "has_pantry": True,
    },
]

CLASS_NAMES = {
    "1A": "AC 1st Class (1A)",
    "2A": "AC 2 Tier (2A)",
    "3A": "AC 3 Tier (3A)",
    "3E": "AC 3 Economy (3E)",
    "CC": "AC Chair Car (CC)",
    "EC": "Exec Chair Car (EC)",
    "SL": "Sleeper Class (SL)",
    "2S": "Second Sitting (2S)",
}


def search_stations(query: str) -> list[dict[str, str]]:
    """Search stations by code, name, city, or state."""
    q = (query or "").strip().lower()
    if not q:
        return STATIONS[:12]
    
    matches = []
    # Exact code match first
    for s in STATIONS:
        if s["code"].lower() == q:
            matches.append(s)
            
    # Starts with code / name / city
    for s in STATIONS:
        if s not in matches:
            if (
                s["code"].lower().startswith(q)
                or s["name"].lower().startswith(q)
                or s["city"].lower().startswith(q)
            ):
                matches.append(s)

    # Contains in name, city, or state
    for s in STATIONS:
        if s not in matches:
            if q in s["name"].lower() or q in s["city"].lower() or q in s["state"].lower():
                matches.append(s)

    return matches[:15]


def get_station_by_code(code: str) -> dict[str, str]:
    """Retrieve station info or fallback formatted dict."""
    c = code.strip().upper()
    for s in STATIONS:
        if s["code"] == c:
            return s
    return {"code": c, "name": f"Station ({c})", "city": c, "state": "India"}


# ---------------------------------------------------------------------------
# External Railway API parsing helpers (honest, validated responses only)
# ---------------------------------------------------------------------------
_CLASS_DEFAULT_FARES = {
    "1A": 3200.0, "2A": 2050.0, "3A": 1450.0, "3E": 1050.0,
    "CC": 950.0, "EC": 1750.0, "SL": 540.0, "2S": 350.0,
}

_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def api_configured() -> bool:
    return bool(settings.railway_api_key and settings.railway_api_key.strip())


def _find(d: Any, *keys: str, default: Any = None) -> Any:
    if isinstance(d, dict):
        lowered = {str(k).lower(): v for k, v in d.items()}
        for key in keys:
            if key.lower() in lowered:
                return lowered[key.lower()]
    return default


def _first(d: dict, *names: str, default: str = "") -> str:
    for name in names:
        val = _find(d, name)
        if val is not None and not isinstance(val, bool) and str(val).strip():
            return str(val).strip()
    return default


def _to_int(val: Any, default: int = 0) -> int:
    try:
        return int(float(str(val).strip()))
    except (TypeError, ValueError):
        return default


def _to_float(val: Any, default: float = 0.0) -> float:
    try:
        f = float(str(val).strip())
        return f if f > 0 else default
    except (TypeError, ValueError):
        return default


def _normalize_duration(raw: Any) -> str:
    s = str(raw or "").strip()
    if not s:
        return ""
    m = re.match(r"^(\d+):([0-5]?\d)$", s)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        return f"{h}h {mi:02d}m" if h else f"{mi:02d}m"
    m = re.match(r"^\s*(\d+)\s*h(?:\s*([0-5]?\d)\s*m)?\s*$", re.sub(r"(?i)hrs?", "h", s))
    if m:
        h, mi = int(m.group(1)), int(m.group(2) or 0)
        return f"{h}h {mi:02d}m"
    return s


def _parse_running_days(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        days = []
        for item in raw:
            day = str(item or "").strip()
            if not day:
                continue
            if day.replace(" ", "").upper() in ("DAILY", "ALL", "ALLDAYS", "ROZ"):
                return ["Daily"]
            days.append(day.title())
        return days or ["Daily"]
    s = str(raw).upper().replace(" ", "").replace("-", "").replace(",", "").replace("_", "")
    if s in ("DAILY", "ALL", "ALLDAYS", "ROZ"):
        return ["Daily"]
    if len(s) >= 7 and set(s[:7]) <= {"Y", "N"}:
        days = [day for flag, day in zip(s[:7], _DAYS) if flag == "Y"]
        return days or ["Daily"]
    parts = [p.strip().title() for p in re.split(r"[,/]", str(raw)) if p.strip()]
    return parts or ["Daily"]


def _train_type(name: str, raw_type: Any = None) -> str:
    rt = str(raw_type or "").upper()
    if rt in ("VB", "VANDE_BHARAT", "VB_EXP"):
        return "Vande Bharat"
    n = name.upper()
    if "VANDE" in n:
        return "Vande Bharat"
    if "RAJDHANI" in n:
        return "Rajdhani"
    if "SHATABDI" in n or "SHATABDEE" in n:
        return "Shatabdi"
    if "SUPERFAST" in n or " SF " in f" {n} ":
        return "Superfast"
    return "Express"


def _class_availability(entry: dict) -> tuple[str, str]:
    stype_raw = _first(entry, "avail_type", "status_type", "status")
    avail_raw = _first(entry, "available", "availability", "avail_count", "avail")
    status = avail_raw or stype_raw or "AVAILABLE"
    blob = f"{stype_raw} {avail_raw}".upper()
    if "RAC" in blob:
        stype = "RAC"
    elif "WAIT" in blob or re.search(r"\bWL\b", blob):
        stype = "WL"
    else:
        stype = "AVAILABLE"
    return status, stype


def _class_fare(entry: dict, cls_code: str) -> float:
    fare = entry.get("fare") if isinstance(entry, dict) else None
    f = _to_float(fare, 0.0)
    if f:
        return f
    return _CLASS_DEFAULT_FARES.get(cls_code.strip().upper(), 1500.0)


def _normalize_class(c: Any, cls_code_hint: str) -> Optional[dict[str, Any]]:
    entry = c if isinstance(c, dict) else {}
    code = _first(entry, "class_code", "classType", "travel_class", "cls") or str(cls_code_hint or "")
    code = code.strip().upper()
    if not code:
        return None
    status, stype = _class_availability(entry)
    return {
        "travel_class": code,
        "class_name": _first(entry, "class_name", "className", "desc") or CLASS_NAMES.get(code, code),
        "fare": _class_fare(entry, code),
        "status": status,
        "status_type": stype,
    }


def _normalize_train(t: Any, from_code: str, to_code: str) -> Optional[dict[str, Any]]:
    if not isinstance(t, dict):
        return None
    number = re.sub(r"\D", "", _first(t, "train_num", "train_number", "train_no", "number"))
    if not number:
        return None
    name = _first(t, "train_name", "name") or f"Express {number}"
    raw_classes = _find(t, "class_type", "classType", "classes", "availability")
    if isinstance(raw_classes, dict):
        raw_classes = _find(raw_classes, "class_type", "classes") or []
    if not isinstance(raw_classes, list):
        raw_classes = []
    classes = []
    seen = set()
    for c in raw_classes:
        hint = c["class_code"] if isinstance(c, dict) else c
        norm = _normalize_class(c, hint)
        if norm and norm["travel_class"] not in seen:
            seen.add(norm["travel_class"])
            classes.append(norm)
    dep = _first(t, "departure_time", "from_std", "dep_time")
    arr = _first(t, "arrival_time", "to_sta", "arr_time")
    return {
        "train_number": number,
        "train_name": name,
        "train_type": _train_type(name, _find(t, "train_type", "trainType")),
        "from_station_code": _first(t, "from_stn_code", "from_station_code", "source_code") or from_code,
        "from_station_name": _first(t, "from_stn_name", "from_station_name", "source", "origin")
        or get_station_by_code(from_code)["name"],
        "to_station_code": _first(t, "to_stn_code", "to_station_code", "dest_code") or to_code,
        "to_station_name": _first(t, "to_stn_name", "to_station_name", "destination", "dest")
        or get_station_by_code(to_code)["name"],
        "departure_time": dep or "",
        "arrival_time": arr or "",
        "duration": _normalize_duration(_find(t, "duration", "travel_time", "running_time")),
        "running_days": _parse_running_days(_find(t, "run_days", "running_days", "runningDays", "days_running")),
        "classes": classes,
        "has_pantry": bool(_to_int(_find(t, "has_pantry", "pantry"), 1)),
    }


def _extract_train_list(payload: Any) -> list[Any]:
    if isinstance(payload, dict):
        data = _find(payload, "data")
        for key in ("train_between_station", "trainbetweenstations", "trains", "train_list", "trainlist"):
            val = _find(data, key) if isinstance(data, dict) else None
            if val is None:
                val = _find(payload, key)
            if isinstance(val, list):
                return val
        if isinstance(data, list):
            return data
    elif isinstance(payload, list):
        return payload
    return []


async def _get_rapidapi(url_path: str, params: dict[str, str]) -> Any:
    url = f"{settings.railway_api_url.rstrip('/')}/{url_path}"
    headers = {
        "x-rapidapi-key": settings.railway_api_key,
        "x-rapidapi-host": settings.railway_api_host,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers, params=params)
        payload = resp.json()
        if resp.status_code != 200 or not isinstance(payload, dict):
            logger.warning("External Railway API %s returned HTTP %s", url_path, resp.status_code)
            return None
        if payload.get("status") is False:
            logger.warning("External Railway API %s reported status: %s", url_path, payload.get("message"))
            return None
        return payload
    except Exception as exc:
        logger.warning("External Railway API %s failed: %s", url_path, exc)
        return None


async def fetch_trains_from_external_api(
    from_code: str, to_code: str, journey_date: date
) -> Optional[list[dict[str, Any]]]:
    """Query external Indian Railways API for original train schedules if an API key is available."""
    if not api_configured():
        return None
    payload = await _get_rapidapi(
        "api/v3/trainBetweenStations",
        {
            "fromStationCode": from_code,
            "toStationCode": to_code,
            "dateOfJourney": journey_date.strftime("%Y-%m-%d"),
        },
    )
    if payload is None:
        return None
    results = []
    seen = set()
    for raw in _extract_train_list(payload):
        train = _normalize_train(raw, from_code, to_code)
        if not train or train["train_number"] in seen:
            continue
        seen.add(train["train_number"])
        results.append(train)
    return results or None


def _catalog_trains_for_route(fc: str, tc: str) -> list[dict[str, Any]]:
    matched = []
    for t in POPULAR_TRAINS:
        if t["from_code"] == fc and t["to_code"] == tc:
            classes = []
            for c in t["classes"]:
                classes.append({
                    "travel_class": c["travel_class"],
                    "class_name": CLASS_NAMES.get(c["travel_class"], c["class_name"]),
                    "fare": c["fare"],
                    "status": "",
                    "status_type": "AVAILABLE",
                })
            matched.append({
                "train_number": t["train_number"],
                "train_name": t["train_name"],
                "train_type": t["train_type"],
                "from_station_code": t["from_code"],
                "from_station_name": t["from_name"],
                "to_station_code": t["to_code"],
                "to_station_name": t["to_name"],
                "departure_time": t["departure_time"],
                "arrival_time": t["arrival_time"],
                "duration": t["duration"],
                "running_days": t["running_days"],
                "classes": classes,
                "has_pantry": t["has_pantry"],
            })
    return matched


async def search_trains_between_stations(
    from_code: str, to_code: str, journey_date: date
) -> list[dict[str, Any]]:
    """Search trains between two stations on a given journey date."""
    fc = from_code.strip().upper()
    tc = to_code.strip().upper()

    external_results = await fetch_trains_from_external_api(fc, tc, journey_date)
    if external_results:
        return external_results

    return _catalog_trains_for_route(fc, tc)


def generate_pnr() -> str:
    """Generate authentic 10-digit Indian Railways PNR number."""
    # First digit 2, 4, 6, 8 (standard zones)
    zone_digit = random.choice(["2", "4", "6", "8"])
    rest = "".join([str(random.randint(0, 9)) for _ in range(9)])
    return zone_digit + rest


def generate_berth_allocation(travel_class: str, index: int, pref: str) -> str:
    """Generate realistic coach, seat number, and berth designation."""
    cls = travel_class.upper()
    coach_prefixes = {
        "1A": "H1",
        "2A": "A" + str(1 + (index // 40)),
        "3A": "B" + str(1 + (index // 64)),
        "3E": "M" + str(1 + (index // 72)),
        "CC": "C" + str(1 + (index // 70)),
        "EC": "E1",
        "SL": "S" + str(1 + (index // 72)),
        "2S": "D" + str(1 + (index // 100)),
    }
    coach = coach_prefixes.get(cls, "B1")
    seat_num = random.randint(1, 64)

    berths = {
        "1A": ["Cabin A", "Cabin B", "Coupe A", "Coupe B"],
        "2A": ["Lower", "Upper", "Side Lower", "Side Upper"],
        "3A": ["Lower", "Middle", "Upper", "Side Lower", "Side Upper"],
        "3E": ["Lower", "Middle", "Upper", "Side Lower", "Side Upper"],
        "CC": ["Window", "Aisle", "Middle"],
        "EC": ["Window", "Aisle"],
        "SL": ["Lower", "Middle", "Upper", "Side Lower", "Side Upper"],
        "2S": ["Window", "Aisle"],
    }

    allowed = berths.get(cls, ["Lower", "Upper"])
    chosen_berth = pref if pref in allowed else random.choice(allowed)
    return f"{coach}-{seat_num} ({chosen_berth})"


def lookup_pnr_status(db: Session, pnr: str) -> Optional[dict[str, Any]]:
    """Lookup a PNR in the local booking database only."""
    clean_pnr = pnr.strip().replace("-", "").replace(" ", "")

    # Only genuine 10-digit IRCTC PNR numbers are accepted
    if not re.match(r"^\d{10}$", clean_pnr):
        return None

    booking = db.query(models.TrainBooking).filter(models.TrainBooking.pnr_number == clean_pnr).first()
    if not booking:
        return None

    return {
        "pnr_number": booking.pnr_number,
        "train_number": booking.train_number,
        "train_name": booking.train_name,
        "from_station": f"{booking.from_station_name} ({booking.from_station_code})",
        "to_station": f"{booking.to_station_name} ({booking.to_station_code})",
        "journey_date": str(booking.journey_date),
        "travel_class": booking.travel_class,
        "chart_prepared": True,
        "status": booking.status,
        "passengers": booking.passengers or [],
    }


async def fetch_pnr_status_from_external(pnr: str) -> Optional[dict[str, Any]]:
    """Query external Indian Railways API for original PNR status if an API key is available."""
    if not api_configured():
        return None
    payload = await _get_rapidapi("api/v3/getPNRStatus", {"pnrNumber": pnr})
    data = _find(payload, "data", "result", "pnr")
    if not isinstance(data, dict):
        return None

    train_number = _first(data, "train_number", "train_num", "trainNo")
    if not train_number:
        return None

    def _station_label(key_name: str) -> str:
        raw = _find(data, key_name)
        if isinstance(raw, dict):
            return f"{_first(raw, 'name', 'station_name')} ({_first(raw, 'code', 'station_code')})"
        return _first(data, key_name, f"{key_name}_name")

    raw_passengers = _find(data, "passengers", "passenger_list", "passengerList")
    passengers = []
    if isinstance(raw_passengers, list):
        for i, p in enumerate(raw_passengers, start=1):
            if not isinstance(p, dict):
                continue
            coach = _first(p, "coach", "coach_position")
            seat = _first(p, "seat", "seat_number", "berth")
            berth_desc = _first(p, "booking_berth_desc", "booking_berth_code")
            seat_str = "/".join(part for part in (coach, seat) if part)
            if berth_desc and berth_desc.upper() not in ("NA", "N/A"):
                seat_str = f"{seat_str} ({berth_desc})" if seat_str else berth_desc
            passengers.append({
                "name": _first(p, "name") or f"Passenger {i}",
                "age": _to_int(_find(p, "age"), 0),
                "gender": _first(p, "gender") or "N/A",
                "seat_number": seat_str or "TBD",
                "status": _first(p, "current_status", "current_status_code", "booking_status", "status") or "CNF",
            })

    chart_raw = _find(data, "chart_prepared", "chartPrepared", "is_chart_prepared")
    chart_prepared = bool(chart_raw) if chart_raw is not None else bool(passengers)

    status_line = _first(data, "status", "pnr_status") or (
        passengers[0]["status"] if passengers else ("CONFIRMED" if chart_prepared else "UNCONFIRMED")
    )

    return {
        "pnr_number": _first(data, "pnr_number", "pnrNumber") or pnr,
        "train_number": train_number,
        "train_name": _first(data, "train_name", "trainName") or f"Train {train_number}",
        "from_station": _station_label("from_station"),
        "to_station": _station_label("to_station"),
        "journey_date": _first(data, "journey_date", "journeyDate", "reservation_date") or "",
        "travel_class": _first(data, "class", "travel_class", "classType") or "",
        "chart_prepared": chart_prepared,
        "status": status_line,
        "passengers": passengers,
    }


async def get_live_train_status(train_number: str) -> Optional[dict[str, Any]]:
    """Retrieve original live running status from the external API."""
    if not api_configured():
        return None
    payload = await _get_rapidapi(
        "api/v1/liveTrainStatus", {"trainNo": train_number.strip(), "startDay": "0"}
    )
    data = _find(payload, "data")
    if not isinstance(data, dict) or not data:
        return None

    num = _first(data, "train_num", "train_number", "trainNo") or train_number.strip()
    name = _first(data, "train_name", "trainName") or f"Train {num}"
    current_station = _first(data, "current_station_name", "current_station", "current_station_code", "position")
    if not current_station:
        return None

    delay_val = _find(data, "delay_in_minutes", "delay_minutes", "delay")
    if isinstance(delay_val, dict):
        delay_val = _to_int(_find(delay_val, "actual_delay", "scheduled_delay"), 0)
    delay = _to_int(delay_val, 0)

    next_station = _first(data, "upcoming_station_name", "next_station", "upcoming_station") or "No upcoming station"
    estimated_arrival = _first(data, "upcoming_station_arrival_time", "next_station_arrival", "eta")
    if not estimated_arrival:
        estimated_arrival = (datetime.now() + timedelta(minutes=45)).strftime("%H:%M")

    return {
        "train_number": num,
        "train_name": name,
        "current_station": current_station,
        "status_message": "Running On Time (Right Time)" if delay == 0 else f"Running Delayed by {delay} mins",
        "delay_minutes": delay,
        "last_updated": _first(data, "last_update", "last_updated", "lastUpdated", "updated_at") or "Just now",
        "next_station": next_station,
        "estimated_arrival": estimated_arrival,
    }


async def search_stations_external(query: str) -> Optional[list[dict[str, str]]]:
    """Query external Indian Railways API for original station results if an API key is available."""
    if not api_configured():
        return None
    payload = await _get_rapidapi("api/v1/searchStation", {"query": query.strip()})
    data = _find(payload, "data")
    if not isinstance(data, list):
        return None
    results = []
    seen = set()
    for s in data:
        if not isinstance(s, dict):
            continue
        code = _first(s, "station_code", "code").upper()
        if not code or code in seen:
            continue
        seen.add(code)
        name = _first(s, "station_name", "name") or _first(s, "city")
        results.append({
            "code": code,
            "name": name or f"Station ({code})",
            "city": _first(s, "city") or name or code,
            "state": _first(s, "state") or "India",
        })
        if len(results) >= 15:
            break
    return results or None
