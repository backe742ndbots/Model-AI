"""
intent_parser.py

Rule-based intent parser for property queries.
Fast, cheap, deterministic.
"""

import re
from typing import Dict, Any, List


# -----------------------------
# Keyword Dictionaries
# -----------------------------

CITY_KEYWORDS = [
    "rohini", "dwarka", "pitam pura", "rani bagh", "noida", "gurgaon"
]

AREA_KEYWORDS = ["MIG", "LIG", "HIG", "JANTA"]

TAG_KEYWORDS = {
    "park": "PARK",
    "corner": "CORNER",
    "furnished": "FULLY FURNISHED",
    "duplex": "DUPLEX",
    "commercial": "COMMERCIAL"
}


# -----------------------------
# Extractors
# -----------------------------

def extract_bhk(text: str) -> int | None:
    match = re.search(r"(\d)\s*bhk", text)
    if match:
        return int(match.group(1))
    return None


def extract_price(text: str) -> float | None:
    match = re.search(r"under\s*([\d\.]+)", text)
    if match:
        return float(match.group(1))
    return None


def extract_city(text: str) -> str | None:
    for city in CITY_KEYWORDS:
        if city in text:
            return city.upper()
    return None


def extract_area_category(text: str) -> str | None:
    for area in AREA_KEYWORDS:
        if area.lower() in text:
            return area
    return None


def extract_tags(text: str) -> List[str]:
    tags = []
    for key, tag in TAG_KEYWORDS.items():
        if key in text:
            tags.append(tag)
    return tags


# -----------------------------
# Main Parser
# -----------------------------

def parse_intent(user_text: str) -> Dict[str, Any]:
    """
    Convert user text into structured filters.
    """

    text = user_text.lower()

    filters: Dict[str, Any] = {}

    bhk = extract_bhk(text)
    if bhk:
        filters["bhk"] = bhk

    price = extract_price(text)
    if price:
        filters["max_price"] = price

    city = extract_city(text)
    if city:
        filters["city"] = city

    area = extract_area_category(text)
    if area:
        filters["area_category"] = area

    tags = extract_tags(text)
    if tags:
        filters["tags"] = tags

    return filters
