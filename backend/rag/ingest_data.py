import json
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
from config import DATA_PATH

from langchain.schema import Document


def load_documents() -> list:
    
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Không tìm thấy: {DATA_PATH}")

    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    skipped = 0

    for item in data:
        try:
            page_content = item.get("text") or _build_text_fallback(item)
            metadata = {
                "id":        item.get("id", ""),
                "location":  item.get("location", ""),
                "city":      item.get("city", ""),
                "type":      item.get("type", ""),
                "region":    item.get("region", ""),
                "price":     item.get("price", ""),
                "best_time": item.get("best_time", ""),
                "transport": item.get("transport", ""),
                "activities": ", ".join(item.get("activities", [])),
            }
            documents.append(Document(page_content=page_content, metadata=metadata))
        except Exception as e:
            skipped += 1
            print(f"Bỏ qua item id={item.get('id', '?')}: {e}")

    print(f"Loaded {len(documents)} documents ({skipped} skipped)")
    return documents


def _build_text_fallback(item: dict) -> str:
    activities = ", ".join(item.get("activities", []))
    return (
        f"{item.get('location', '')} in {item.get('city', '')} "
        f"is a {item.get('type', '')} destination. "
        f"{item.get('description', '')} "
        f"Best time to visit is {item.get('best_time', '')}. "
        f"Activities include {activities}. "
        f"Region: {item.get('region', '')}. "
        f"Price range: {item.get('price', '')}. "
        f"Transport: {item.get('transport', '')}."
    )