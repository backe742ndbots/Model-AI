"""
schemas.py

Defines:
- Property document schema (logical structure)
- Normalization helpers for messy CSV data
"""

from datetime import datetime
import re


# -----------------------------
# Normalization Helpers
# -----------------------------

BHK_MAP = {
    "ONE": 1,
    "TWO": 2,
    "THREE": 3,
    "FOUR": 4,
    "FIVE": 5,
    "SIX": 6,
    "HALL": 1,
    "TW0": 2,  # typo in data
    "TWO&HALF": 3
}


def normalize_bhk(bhk_raw: str | None) -> int | None:
    """
    Converts messy BHK strings into an integer.
    Always preserves original value separately.
    """
    if not bhk_raw or not isinstance(bhk_raw, str):
        return None

    value = bhk_raw.strip().upper()

    # Direct mapping
    if value in BHK_MAP:
        return BHK_MAP[value]

    # Patterns like 2+1, 3+1/2, 1+1+1
    numbers = re.findall(r"\d+", value)
    if numbers:
        return max(int(n) for n in numbers)

    return None


def normalize_price(value: str | float | int | None) -> float | None:
    """
    Normalizes price fields (ASKING / NET PRICE).
    Stored in CRORES.
    """
    if value is None:
        return None

    try:
        return float(str(value).replace("-", "").strip())
    except ValueError:
        return None


def normalize_floor(floor_raw: str | None) -> list[str]:
    """
    Splits floor data into list.
    Example: 'GF+FF' -> ['GF', 'FF']
    """
    if not floor_raw or not isinstance(floor_raw, str):
        return []

    parts = re.split(r"[+/]", floor_raw.upper())
    return [p.strip() for p in parts if p.strip()]


def normalize_phone(phone) -> str | None:
    """
    Ensures phone numbers are stored as strings.
    Removes decimals from CSV float damage.
    """
    if phone is None:
        return None

    phone_str = str(phone).split(".")[0].strip()
    return phone_str if phone_str.isdigit() else None


def normalize_tags(*values) -> list[str]:
    """
    Combines STATUS / STATUS.1 / STATUS.2 into clean tag list.
    """
    tags = set()
    for val in values:
        if isinstance(val, str) and val.strip():
            tags.add(val.strip().upper())
    return list(tags)


def normalize_contact_role(through: str | None) -> str:
    """
    Determines contact role based on THROUGH column.
    """
    if not through:
        return "UNKNOWN"

    value = through.strip().upper()
    if value == "PARTY":
        return "OWNER"

    return value


# -----------------------------
# Property Document Builder
# -----------------------------

def build_property_document(row: dict) -> dict:
    """
    Converts a CSV row (dict) into a MongoDB-ready property document.
    """

    bhk_raw = row.get("BHK")

    document = {
        "meta": {
            "entry_date": datetime.utcnow(),
            "source": "csv_import"
        },

        "location": {
            "city": row.get("CITY"),
            "sector": row.get("SEC") or row.get("SEC.1"),
            "block": row.get("BLOCK") or row.get("BLK"),
            "pocket": row.get("POCKET") or row.get("PKT"),
            "house_number": row.get("NUMBER") or row.get("NUM"),
            "road": row.get("ROAD"),
            "facing": row.get("FACE")
        },

        "property": {
            "category": "COMMERCIAL" if row.get("STATUS") == "COMMERCIAL" else "RESIDENTIAL",
            "area_category": row.get("AREA"),
            "floors": normalize_floor(row.get("FLR")),
            "bhk_raw": bhk_raw,
            "bhk_normalized": normalize_bhk(bhk_raw),
            "roof": row.get("STATUS.2"),
            "area_sqft_raw": row.get("STATUS.2")
        },

        "pricing": {
            "asking_crore": normalize_price(row.get("ASKING")),
            "net_crore": normalize_price(row.get("NET PRICE"))
        },

        "status": {
            "listing": row.get("STATUS"),
            "tags": normalize_tags(
                row.get("STATUS"),
                row.get("STATUS.1"),
                row.get("STATUS.2")
            ),
            "commercial": row.get("STATUS") == "COMMERCIAL",
            "dispute": "DISPUTE" in normalize_tags(row.get("STATUS.1"), row.get("STATUS.2"))
        },

        "contact": {
            "name": row.get("NAME"),
            "role": normalize_contact_role(row.get("THROUGH")),
            "through": row.get("THROUGH"),
            "office_name": row.get("OFFICE NAME"),
            "primary_mobile": normalize_phone(row.get("MOBILE")),
            "secondary_mobile": normalize_phone(row.get("MOBILE.1"))
        },

        "deal": {
            "channel": row.get("THROUGH"),
            "remarks": row.get("COMMENT")
        },

        # Raw preservation (critical)
        "raw_csv": row
    }

    return document
