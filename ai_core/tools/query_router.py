"""
query_router.py

Routes user queries to the correct tools.
This is the single entry point for text-based queries.
"""
from typing import Dict, Any

from ai_core.tools.intent_parser import parse_intent
from ai_core.tools.property_tool import search_properties



# -----------------------------
# Main Router
# -----------------------------

def handle_user_query(user_text: str, limit: int = 5) -> Dict[str, Any]:
    """
    Takes raw user text and returns structured results.
    """

    # Step 1: Parse intent
    filters = parse_intent(user_text)

    # Step 2: Query database via tool
    results = search_properties(
        city=filters.get("city"),
        bhk=filters.get("bhk"),
        min_price=filters.get("min_price"),
        max_price=filters.get("max_price"),
        area_category=filters.get("area_category"),
        tags=filters.get("tags"),
        limit=limit,
    )

    # Step 3: Prepare response payload
    response = {
        "query": user_text,
        "filters_used": filters,
        "result_count": len(results),
        "results": results,
    }

    return response
