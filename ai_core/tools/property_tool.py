"""
property_tool.py

Core property search tool.
This is the ONLY way AI is allowed to read property data.
"""

from typing import Optional, List, Dict, Any

from ai_core.db.mongo.client import get_properties_collection


# -----------------------------
# Query Builder
# -----------------------------

def build_query(
    city: Optional[str] = None,
    bhk: Optional[int] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    area_category: Optional[str] = None,
    floor: Optional[str] = None,
    contact_role: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build a MongoDB query dict based on provided filters.
    """

    query: Dict[str, Any] = {}

    if city:
        query["location.city"] = city.upper()

    if bhk is not None:
        query["property.bhk_normalized"] = bhk

    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        query["pricing.asking_crore"] = price_filter

    if area_category:
        query["property.area_category"] = area_category.upper()

    if floor:
        query["property.floors"] = floor.upper()

    if contact_role:
        query["contact.role"] = contact_role.upper()

    if tags:
        query["status.tags"] = {
            "$all": [t.upper() for t in tags]
        }

    return query


# -----------------------------
# Public Search API
# -----------------------------

def search_properties(
    city: Optional[str] = None,
    bhk: Optional[int] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    area_category: Optional[str] = None,
    floor: Optional[str] = None,
    contact_role: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Search properties based on structured filters.
    Returns AI-friendly results only.
    """

    collection = get_properties_collection()

    query = build_query(
        city=city,
        bhk=bhk,
        max_price=max_price,
        min_price=min_price,
        area_category=area_category,
        floor=floor,
        contact_role=contact_role,
        tags=tags,
    )

    cursor = (
        collection
        .find(query)
        .limit(limit)
    )

    results = []

    for doc in cursor:
        results.append({
            "id": str(doc["_id"]),
            "city": doc["location"].get("city"),
            "sector": doc["location"].get("sector"),
            "block": doc["location"].get("block"),
            "pocket": doc["location"].get("pocket"),
            "house_number": doc["location"].get("house_number"),

            "bhk": doc["property"].get("bhk_normalized"),
            "area_category": doc["property"].get("area_category"),
            "floors": doc["property"].get("floors"),

            "asking_price_crore": doc["pricing"].get("asking_crore"),

            "contact_name": doc["contact"].get("name"),
            "contact_role": doc["contact"].get("role"),
            "contact_mobile": doc["contact"].get("primary_mobile"),

            "tags": doc["status"].get("tags", []),
        })

    return results
