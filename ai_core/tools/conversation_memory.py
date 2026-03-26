"""
conversation_memory.py

Simple in-memory conversation state.
"""

from typing import Dict, Any

# Single-user memory for now (MVP)
SESSION_MEMORY: Dict[str, Any] = {
    "last_intent": None,
    "last_results": None,
    "last_filters": None,
}


def update_memory(intent=None, results=None, filters=None):
    if intent is not None:
        SESSION_MEMORY["last_intent"] = intent
    if results is not None:
        SESSION_MEMORY["last_results"] = results
    if filters is not None:
        SESSION_MEMORY["last_filters"] = filters


def get_memory():
    return SESSION_MEMORY
