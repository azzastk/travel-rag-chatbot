import json
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR    = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)
from config import DATA_PATH

from langchain.schema import Document

# File 2 — places dataset (cà phê, nhà hàng, khách sạn)
PLACES_PATH = os.path.join(ROOT_DIR, "data", "places_dataset.json")


def load_documents() -> list:
    """Load cả 2 dataset và trả về list Document."""
    documents = []

    # === Dataset 1: travel_dataset.json (56 điểm đến) ===
    docs1, skip1 = _load_travel_dataset(DATA_PATH)
    documents.extend(docs1)
    print(f"📂 travel_dataset.json  : {len(docs1)} docs ({skip1} skipped)")

    # === Dataset 2: places_dataset.json (cà phê, nhà hàng, khách sạn) ===
    if os.path.exists(PLACES_PATH):
        docs2, skip2 = _load_places_dataset(PLACES_PATH)
        documents.extend(docs2)
        print(f"📂 places_dataset.json  : {len(docs2)} docs ({skip2} skipped)")
    else:
        print(f"⚠️  places_dataset.json không tìm thấy tại: {PLACES_PATH}")
        print(f"   Chạy scrape_foursquare_v2.py để tạo file này.")

    print(f"📝 Tổng documents       : {len(documents)}")
    return documents


def _load_travel_dataset(path: str):
    """Load travel_dataset.json — các điểm đến du lịch."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    skipped = 0
    for item in data:
        try:
            page_content = item.get("text") or _build_travel_text(item)
            metadata = {
                "source":    "travel_dataset",
                "id":        item.get("id", ""),
                "location":  item.get("location", ""),
                "city":      item.get("city", ""),
                "type":      item.get("type", ""),
                "region":    item.get("region", ""),
                "price":     item.get("price", ""),
                "best_time": item.get("best_time", ""),
                "transport": item.get("transport", ""),
                "activities": ", ".join(item.get("activities", [])),
                "category":  "destination",
            }
            docs.append(Document(page_content=page_content, metadata=metadata))
        except Exception as e:
            skipped += 1
            print(f"  ⚠️  Skip travel item id={item.get('id', '?')}: {e}")

    return docs, skipped


def _load_places_dataset(path: str):
    """Load places_dataset.json — cà phê, nhà hàng, khách sạn."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    skipped = 0
    for item in data:
        try:
            page_content = item.get("text") or _build_place_text(item)
            metadata = {
                "source":      "places_dataset",
                "id":          item.get("id", ""),
                "name":        item.get("name", ""),
                "city":        item.get("city", ""),
                "category":    item.get("category", ""),
                "type":        item.get("type", ""),
                "address":     item.get("address", ""),
                "rating":      str(item.get("rating", "")),
                "hours":       item.get("hours", ""),
                "price":       item.get("price", ""),
                "description": item.get("description", ""),
            }
            docs.append(Document(page_content=page_content, metadata=metadata))
        except Exception as e:
            skipped += 1
            print(f"  ⚠️  Skip place item id={item.get('id', '?')}: {e}")

    return docs, skipped


def _build_travel_text(item: dict) -> str:
    """Fallback text cho travel_dataset nếu thiếu field 'text'."""
    activities = ", ".join(item.get("activities", []))
    return (
        f"{item.get('location', '')} in {item.get('city', '')} "
        f"is a {item.get('type', '')} destination. "
        f"{item.get('description', '')} "
        f"Best time to visit: {item.get('best_time', '')}. "
        f"Activities: {activities}. "
        f"Region: {item.get('region', '')}. "
        f"Price range: {item.get('price', '')}. "
        f"Transport: {item.get('transport', '')}."
    )


def _build_place_text(item: dict) -> str:
    """Fallback text cho places_dataset nếu thiếu field 'text'."""
    parts = [f"{item.get('name', '')} is a {item.get('category', '')} in {item.get('city', '')}, Vietnam."]
    if item.get("address"):
        parts.append(f"Address: {item['address']}.")
    if item.get("rating"):
        parts.append(f"Rating: {item['rating']}/10.")
    if item.get("hours"):
        parts.append(f"Hours: {item['hours']}.")
    if item.get("price"):
        parts.append(f"Price: {item['price']}.")
    if item.get("description"):
        parts.append(item["description"])
    return " ".join(parts)