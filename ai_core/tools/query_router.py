"""
query_router.py

Routes user queries to the correct tools.
This is the single entry point for text-based queries.
"""

from typing import Dict, Any

from ai_core.tools.intent_parser import parse_intent
from ai_core.tools.property_tool import search_properties
from ai_core.tools.ollama_client import ask_ollama


# -----------------------------
# LLM Intent Classifier (llama3)
# -----------------------------
def classify_intent_with_llm(user_text: str) -> str:
    prompt = f"""
You are a strict intent classifier.

You MUST respond with ONLY ONE WORD.
No explanation. No punctuation. No formatting.

Choose exactly one from:
greeting
property_search
help
unknown

User text:
{user_text}

Answer:
"""
    response = ask_ollama(prompt)

    # Safety normalization
    return response.strip().lower().split()[0]




def decide_action_with_llm(user_text: str) -> str:
    """
    Decide whether to chat or search properties.
    """
    prompt = f"""
You are a conversational real estate assistant.

Decide the action for this user message.

Choose ONLY ONE:
chat
property_search
ask_clarification

User message:
{user_text}

Answer:
"""
    response = ask_ollama(prompt)
    return response.strip().lower().split()[0]


def chat_with_llm(user_text: str) -> str:
    """
    Free-form conversational response.
    """
    prompt = f"""
You are a helpful, friendly real estate AI assistant.

You can:
- chat naturally
- answer general questions
- explain real estate concepts
- give advice (no legal guarantees)

User:
{user_text}

Assistant:
"""
    return ask_ollama(prompt)






def is_followup_query(text: str) -> bool:
    followups = {
        "what are those",
        "tell me",
        "tell me more",
        "show them",
        "elaborate",
        "explain",
        "those properties",
        "can you elaborate",
        "details",
    }
    return any(phrase in text.lower() for phrase in followups)



# -----------------------------
# Main Router
# -----------------------------
from ai_core.tools.conversation_memory import update_memory, get_memory


def explain_properties_with_llm(properties):
    """
    Uses llama3 to explain a list of properties conversationally.
    """
    # Keep prompt small & safe (no full raw dump)
    summary_lines = []
    for i, p in enumerate(properties, start=1):
        summary_lines.append(
            f"{i}. Location: {p.get('city', '')} Block {p.get('block', '')} "
            f"Pocket {p.get('pocket', '')}, "
            f"BHK: {p.get('bhk', 'N/A')}, "
            f"Price: {p.get('price', 'Price on request')}"
        )

    summary_text = "\n".join(summary_lines)

    prompt = f"""
You are a professional real estate advisor.

The following properties were found for the user:

{summary_text}

Explain these properties clearly and concisely.
Highlight:
- location differences
- who each property may be suitable for
- any useful insights

Keep the tone friendly and helpful.
Do NOT invent details not present.
"""
    return ask_ollama(prompt)




def handle_user_query(user_text: str, limit: int = 5):
    clean_text = user_text.strip()

    memory = get_memory()

    # -----------------------------
    # 1. Handle follow-up questions
    # -----------------------------
    if is_followup_query(clean_text):
        if memory["last_intent"] == "property_search" and memory["last_results"]:

            explanation = explain_properties_with_llm(memory["last_results"])

            return {
                "reply_text": explanation,
                "intent": "property_followup",
                "results": memory["last_results"],
            }


    # -----------------------------
    # 2. Let llama3 decide action
    # -----------------------------
    action = decide_action_with_llm(clean_text)

    # -----------------------------
    # 3. Normal chat
    # -----------------------------
    if action == "chat":
        update_memory(intent="chat")
        return {
            "reply_text": chat_with_llm(clean_text),
            "intent": "chat"
        }

    # -----------------------------
    # 4. Clarification
    # -----------------------------
    if action == "ask_clarification":
        update_memory(intent="clarification")
        return {
            "reply_text": "Could you share more details like location, budget, or BHK?",
            "intent": "clarification"
        }

    # -----------------------------
    # 5. Property search
    # -----------------------------
    filters = parse_intent(clean_text)

    results = search_properties(
        city=filters.get("city"),
        bhk=filters.get("bhk"),
        min_price=filters.get("min_price"),
        max_price=filters.get("max_price"),
        area_category=filters.get("area_category"),
        tags=filters.get("tags"),
        limit=limit,
    )

    update_memory(
        intent="property_search",
        results=results,
        filters=filters
    )

    return {
        "reply_text": f"I found {len(results)} properties that may match your requirement.",
        "intent": "property_search",
        "results": results,
    }
