"""
seed.py

Seeds MongoDB with property data from CSV.
Uses schemas.py for normalization.
"""

import sys
from pathlib import Path

import pandas as pd
from pymongo.errors import BulkWriteError

from db.mongo.client import get_properties_collection
from db.mongo.schemas import build_property_document


# -----------------------------
# Configuration
# -----------------------------

# Change this to your actual CSV file path
CSV_PATH = Path(r"D:\ML\property-ai\ai-core\db\mongo\FloorDataOrg.csv")

BATCH_SIZE = 100  # insert in chunks


# -----------------------------
# Helpers
# -----------------------------

def clean_row(row: dict) -> dict:
    """
    Convert pandas NaN to None and strip strings.
    """
    cleaned = {}
    for k, v in row.items():
        if pd.isna(v):
            cleaned[k] = None
        elif isinstance(v, str):
            cleaned[k] = v.strip()
        else:
            cleaned[k] = v
    return cleaned


# -----------------------------
# Main Seeder
# -----------------------------

def run_seed():
    if not CSV_PATH.exists():
        print(f"❌ CSV file not found: {CSV_PATH}")
        sys.exit(1)

    print("📂 Reading CSV...")
    df = pd.read_csv(CSV_PATH)

    print(f"📊 Total rows found: {len(df)}")

    collection = get_properties_collection()

    documents = []
    inserted = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            raw_row = clean_row(row.to_dict())
            doc = build_property_document(raw_row)
            documents.append(doc)

            if len(documents) >= BATCH_SIZE:
                result = collection.insert_many(documents, ordered=False)
                inserted += len(result.inserted_ids)
                documents.clear()

        except Exception as exc:
            skipped += 1
            print(f"⚠️ Skipped row {idx}: {exc}")

    # Insert remaining docs
    if documents:
        try:
            result = collection.insert_many(documents, ordered=False)
            inserted += len(result.inserted_ids)
        except BulkWriteError as exc:
            print("⚠️ Bulk write warning:", exc.details)

    print("✅ Seeding complete")
    print(f"✔ Inserted: {inserted}")
    print(f"⚠ Skipped: {skipped}")


if __name__ == "__main__":
    run_seed()
