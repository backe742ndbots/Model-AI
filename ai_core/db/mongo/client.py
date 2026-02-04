"""
client.py

Single MongoDB connection handler.
ALL database access must go through this file.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv



# -----------------------------
# Load environment variables
# -----------------------------

load_dotenv()  # loads .env from project root

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "property_ai")

if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI not found. Check your .env file. "
        "Do NOT hardcode MongoDB credentials."
    )

# -----------------------------
# Client Initialization
# -----------------------------

_client: MongoClient | None = None
_db = None


def get_client() -> MongoClient:
    global _client

    if _client is None:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )

        # Test connection immediately
        try:
            _client.admin.command("ping")
        except ConnectionFailure as exc:
            raise RuntimeError(
                "Failed to connect to MongoDB Atlas"
            ) from exc

    return _client


def get_db():
    global _db

    if _db is None:
        client = get_client()
        _db = client[DB_NAME]

    return _db


def get_properties_collection():
    db = get_db()
    return db["properties"]
