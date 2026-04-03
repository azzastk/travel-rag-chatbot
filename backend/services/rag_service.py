import os
import sys
import re

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from rag.retriever import get_retriever

SIMILARITY_THRESHOLD = 0.65

CITY_MAPPING = {
    "tphcm":           "Ho Chi Minh City",
    "tp.hcm":          "Ho Chi Minh City",
    "tp hcm":          "Ho Chi Minh City",
    "hồ chí minh":     "Ho Chi Minh City",
    "ho chi minh":     "Ho Chi Minh City",
    "sài gòn":         "Ho Chi Minh City",
    "saigon":          "Ho Chi Minh City",
    "hà nội":          "Hanoi",
    "ha noi":          "Hanoi",
    "hanoi":           "Hanoi",
    "đà nẵng":         "Da Nang",
    "da nang":         "Da Nang",
    "hội an":          "Hoi An",
    "hoi an":          "Hoi An",
    "nha trang":       "Nha Trang",
    "đà lạt":          "Da Lat",
    "da lat":          "Da Lat",
    "dalat":           "Da Lat",
    "huế":             "Hue",
    "hue":             "Hue",
    "cần thơ":         "Can Tho",
    "can tho":         "Can Tho",
    "phú quốc":        "Phu Quoc",
    "phu quoc":        "Phu Quoc",
    "vũng tàu":        "Vung Tau",
    "vung tau":        "Vung Tau",
    "hạ long":         "Ha Long",
    "ha long":         "Ha Long",
    "vịnh hạ long":    "Ha Long",
    "sa pa":           "Sa Pa",
    "sapa":            "Sa Pa",
    "mũi né":          "Mui Ne",
    "mui ne":          "Mui Ne",
    "phan thiết":      "Phan Thiet",
    "phan thiet":      "Phan Thiet",
    "phong nha":       "Phong Nha",
    "quảng bình":      "Phong Nha",
    "kon tum":         "Kon Tum",
    "buôn ma thuột":   "Buon Ma Thuot",
    "buon ma thuot":   "Buon Ma Thuot",
    "đắk lắk":         "Buon Ma Thuot",
}

CATEGORY_MAPPING = {
    "cà phê":    "coffee",
    "cafe":      "coffee",
    "coffee":    "coffee",
    "nhà hàng":  "restaurant",
    "quán ăn":   "restaurant",
    "ăn uống":   "restaurant",
    "restaurant": "restaurant",
    "khách sạn": "hotel",
    "homestay":  "hotel",
    "hotel":     "hotel",
    "lưu trú":   "hotel",
}

# Từ khóa chỉ câu hỏi tổng quát — không filter category
GENERAL_KEYWORDS = [
    "lập kế hoạch", "kế hoạch", "itinerary", "plan",
    "đi chơi", "du lịch", "tham quan", "khám phá",
    "nên đi đâu", "gợi ý địa điểm", "địa điểm nổi tiếng",
    "điểm đến", "nên làm gì", "what to do", "where to go",
    "things to do", "places to visit", "travel guide",
    "lịch trình", "hành trình",
]


def _detect_city(question: str) -> str:
    q = question.lower()
    for keyword, city in CITY_MAPPING.items():
        if keyword in q:
            return city
    return ""


def _detect_category(question: str) -> str:
    q = question.lower()
    for keyword, cat in CATEGORY_MAPPING.items():
        if keyword in q:
            return cat
    return ""


def _is_general_query(question: str) -> bool:
    """Kiểm tra câu hỏi có phải loại tổng quát không — không nên filter category."""
    q = question.lower()
    return any(kw in q for kw in GENERAL_KEYWORDS)


def retrieve_context(question: str) -> str:
    try:
        retriever  = get_retriever()
        collection = retriever.col

        detected_city     = _detect_city(question)
        detected_category = _detect_category(question)
        is_general        = _is_general_query(question)

        # Nếu là câu hỏi tổng quát (lịch trình, đi chơi...) → chỉ filter city
        if is_general:
            detected_category = ""
            print(f"[RAG] General query detected → skip category filter")

        # Build where filter
        where_filter = None
        if detected_city and detected_category:
            where_filter = {
                "$and": [
                    {"city":     {"$eq": detected_city}},
                    {"category": {"$eq": detected_category}},
                ]
            }
            print(f"[RAG] Filter: city={detected_city}, category={detected_category}")
        elif detected_city:
            where_filter = {"city": {"$eq": detected_city}}
            print(f"[RAG] Filter: city={detected_city}")
        elif detected_category:
            where_filter = {"category": {"$eq": detected_category}}
            print(f"[RAG] Filter: category={detected_category}")
        else:
            print(f"[RAG] Filter: none")

        query_params = {
            "query_texts": [question],
            "n_results":   retriever.k,
            "include":     ["documents", "metadatas", "distances"],
        }
        if where_filter:
            query_params["where"] = where_filter

        results = collection.query(**query_params)

        if not results["documents"][0]:
            print("[RAG] Không có kết quả → fallback web search")
            return ""

        from langchain.schema import Document
        docs = []
        print("\n[RAG] Documents retrieved:")
        for text, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            name     = meta.get("name") or meta.get("location", "?")
            city     = meta.get("city", "?")
            relevant = dist < SIMILARITY_THRESHOLD
            print(f"  {'✅' if relevant else '❌'} {name} — {city} (score: {dist:.3f})")
            if relevant:
                docs.append(Document(page_content=text, metadata=meta))

        if not docs:
            # Nới lỏng — lấy top kết quả tốt nhất
            best_text = results["documents"][0][0]
            best_meta = results["metadatas"][0][0]
            docs.append(Document(page_content=best_text, metadata=best_meta))

        return "\n\n".join([doc.page_content for doc in docs])

    except RuntimeError as e:
        print(f"[RAG] Warning: {e}")
        return ""