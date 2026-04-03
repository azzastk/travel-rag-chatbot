import json
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR    = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)
from config import DATA_PATH

from langchain.schema import Document

PLACES_PATH = os.path.join(ROOT_DIR, "data", "places_dataset.json")

# Map tỉnh/thành → tên thành phố chuẩn dùng trong metadata filter
# Đảm bảo khớp với CITY_MAPPING trong rag_service.py
PROVINCE_TO_CITY = {
    "Lam Dong":       "Da Lat",
    "Khanh Hoa":      "Nha Trang",
    "Thua Thien Hue": "Hue",
    "Quang Nam":      "Hoi An",
    "Quang Ninh":     "Ha Long",
    "Kien Giang":     "Phu Quoc",
    "Ba Ria":         "Vung Tau",
    "Vung Tau":       "Vung Tau",
    "Lao Cai":        "Sa Pa",
    "Binh Thuan":     "Mui Ne",
    "Quang Binh":     "Phong Nha",
    "Kon Tum":        "Kon Tum",
    "Dak Lak":        "Buon Ma Thuot",
    "Can Tho":        "Can Tho",
    "Da Nang":        "Da Nang",
    "Hanoi":          "Hanoi",
    "Ha Noi":         "Hanoi",
    "Ho Chi Minh":    "Ho Chi Minh City",
}

# Map location → city chuẩn (cho các địa danh cụ thể)
LOCATION_TO_CITY = {
    "Da Lat":             "Da Lat",
    "Xuan Huong Lake":    "Da Lat",
    "Langbiang Mountain": "Da Lat",
    "Valley of Love":     "Da Lat",
    "Da Nang":            "Da Nang",
    "Ba Na Hills":        "Da Nang",
    "Dragon Bridge":      "Da Nang",
    "My Khe Beach":       "Da Nang",
    "Marble Mountains":   "Da Nang",
    "Ha Long Bay":        "Ha Long",
    "Bai Tu Long Bay":    "Ha Long",
    "Hoi An":             "Hoi An",
    "Nha Trang":          "Nha Trang",
    "Hue":                "Hue",
    "Phu Quoc":           "Phu Quoc",
    "Sa Pa":              "Sa Pa",
    "Mui Ne":             "Mui Ne",
    "Phong Nha":          "Phong Nha",
}


def _normalize_city(item: dict) -> str:
    """Chuẩn hóa tên thành phố để khớp với CITY_MAPPING trong rag_service."""
    location = item.get("location", "")
    city     = item.get("city", "")

    # Ưu tiên map theo location cụ thể
    if location in LOCATION_TO_CITY:
        return LOCATION_TO_CITY[location]

    # Fallback map theo tỉnh
    for province, std_city in PROVINCE_TO_CITY.items():
        if province.lower() in city.lower():
            return std_city

    return city


def load_documents() -> list:
    documents = []

    docs1, skip1 = _load_travel_dataset(DATA_PATH)
    documents.extend(docs1)
    print(f"📂 travel_dataset.json  : {len(docs1)} docs ({skip1} skipped)")

    if os.path.exists(PLACES_PATH):
        docs2, skip2 = _load_places_dataset(PLACES_PATH)
        documents.extend(docs2)
        print(f"📂 places_dataset.json  : {len(docs2)} docs ({skip2} skipped)")
    else:
        print(f"⚠️  places_dataset.json không tìm thấy")

    print(f"📝 Tổng documents       : {len(documents)}")
    return documents


def _load_travel_dataset(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Không tìm thấy: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    docs    = []
    skipped = 0
    for item in data:
        try:
            # Chuẩn hóa city để khớp với filter
            std_city     = _normalize_city(item)
            page_content = item.get("text") or _build_travel_text(item, std_city)

            metadata = {
                "source":    "travel_dataset",
                "id":        item.get("id", ""),
                "location":  item.get("location", ""),
                "city":      std_city,  # ✅ dùng city đã chuẩn hóa
                "type":      item.get("type", ""),
                "region":    item.get("region", ""),
                "price":     item.get("price", ""),
                "best_time": item.get("best_time", ""),
                "transport": item.get("transport", ""),
                "activities": ", ".join(item.get("activities", [])),
                "category":  "destination",  # để phân biệt với coffee/restaurant/hotel
            }
            docs.append(Document(page_content=page_content, metadata=metadata))
        except Exception as e:
            skipped += 1
            print(f"  ⚠️  Skip id={item.get('id','?')}: {e}")

    return docs, skipped


def _load_places_dataset(path: str):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    docs    = []
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
            print(f"  ⚠️  Skip id={item.get('id','?')}: {e}")

    return docs, skipped


def _build_travel_text(item: dict, std_city: str) -> str:
    activities = ", ".join(item.get("activities", []))
    location   = item.get("location", "")
    return (
        f"{location} in {std_city} is a {item.get('type','')} destination. "
        f"{item.get('description','')} "
        f"Best time to visit: {item.get('best_time','')}. "
        f"Activities: {activities}. "
        f"Region: {item.get('region','')}. "
        f"Price: {item.get('price','')}."
    )


def _build_place_text(item: dict) -> str:
    parts = [f"{item.get('name','')} is a {item.get('category','')} in {item.get('city','')}, Vietnam."]
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