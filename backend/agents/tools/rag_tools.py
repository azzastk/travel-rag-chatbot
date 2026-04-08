"""
RAG Tools cho LangChain Agent.
Dùng @tool decorator của LangChain — dễ thêm tool mới sau này.
"""
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from langchain_core.tools import tool
from rag.retriever import get_retriever

SIMILARITY_THRESHOLD = 0.65

CITY_MAPPING = {
    "tphcm": "Ho Chi Minh City", "tp.hcm": "Ho Chi Minh City",
    "tp hcm": "Ho Chi Minh City", "hồ chí minh": "Ho Chi Minh City",
    "ho chi minh": "Ho Chi Minh City", "sài gòn": "Ho Chi Minh City",
    "saigon": "Ho Chi Minh City", "hà nội": "Hanoi", "ha noi": "Hanoi",
    "hanoi": "Hanoi", "đà nẵng": "Da Nang", "da nang": "Da Nang",
    "hội an": "Hoi An", "hoi an": "Hoi An", "nha trang": "Nha Trang",
    "đà lạt": "Da Lat", "da lat": "Da Lat", "dalat": "Da Lat",
    "huế": "Hue", "hue": "Hue", "cần thơ": "Can Tho", "can tho": "Can Tho",
    "phú quốc": "Phu Quoc", "phu quoc": "Phu Quoc",
    "vũng tàu": "Vung Tau", "vung tau": "Vung Tau",
    "hạ long": "Ha Long", "ha long": "Ha Long",
    "sa pa": "Sa Pa", "sapa": "Sa Pa",
    "mũi né": "Mui Ne", "mui ne": "Mui Ne",
    "phan thiết": "Phan Thiet", "phan thiet": "Phan Thiet",
    "phong nha": "Phong Nha", "quảng bình": "Phong Nha",
    "kon tum": "Kon Tum",
    "buôn ma thuột": "Buon Ma Thuot", "buon ma thuot": "Buon Ma Thuot",
}


def _detect_city(text: str) -> str:
    t = text.lower()
    for kw, city in CITY_MAPPING.items():
        if kw in t:
            return city
    return ""


def _query_collection(query: str, where: dict, k: int = 5) -> str:
    """Query ChromaDB với filter và trả về context string."""
    try:
        retriever  = get_retriever()
        collection = retriever.col
        params = {
            "query_texts": [query],
            "n_results":   k,
            "include":     ["documents", "metadatas", "distances"],
        }
        if where:
            params["where"] = where

        results = collection.query(**params)
        if not results["documents"][0]:
            return ""

        docs = []
        for text, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            if dist < SIMILARITY_THRESHOLD:
                docs.append(text)

        if not docs and results["documents"][0]:
            docs = [results["documents"][0][0]]

        return "\n\n".join(docs)

    except Exception as e:
        return f"Error: {e}"


@tool
def search_destinations(query: str) -> str:
    """
    Tìm kiếm địa điểm tham quan, danh lam thắng cảnh tại Việt Nam.
    Dùng khi user hỏi về nơi đi chơi, tham quan, địa danh nổi tiếng.
    Input: câu hỏi về địa điểm, ví dụ 'điểm tham quan ở Đà Lạt'
    """
    city = _detect_city(query)
    where = (
        {
            "$and": [
                {"city":     {"$eq": city}},
                {"category": {"$nin": ["hotel", "coffee", "restaurant"]}},
            ]
        }
        if city else
        {"category": {"$nin": ["hotel", "coffee", "restaurant"]}}
    )
    result = _query_collection(query, where, k=6)
    return result or "Không tìm thấy địa điểm phù hợp."


@tool
def search_restaurants(query: str) -> str:
    """
    Tìm kiếm nhà hàng, quán ăn tại Việt Nam.
    Dùng khi user hỏi về ăn uống, nhà hàng, quán ăn ngon.
    Input: câu hỏi về nhà hàng, ví dụ 'nhà hàng ngon ở Hội An'
    """
    city  = _detect_city(query)
    where = (
        {
            "$and": [
                {"city":     {"$eq": city}},
                {"category": {"$eq": "restaurant"}},
            ]
        }
        if city else
        {"category": {"$eq": "restaurant"}}
    )
    result = _query_collection(query, where, k=5)
    return result or "Không tìm thấy nhà hàng phù hợp."


@tool
def search_cafes(query: str) -> str:
    """
    Tìm kiếm quán cà phê tại Việt Nam.
    Dùng khi user hỏi về cà phê, cafe, chỗ ngồi uống cà phê.
    Input: câu hỏi về cà phê, ví dụ 'quán cà phê đẹp ở Đà Nẵng'
    """
    city  = _detect_city(query)
    where = (
        {
            "$and": [
                {"city":     {"$eq": city}},
                {"category": {"$eq": "coffee"}},
            ]
        }
        if city else
        {"category": {"$eq": "coffee"}}
    )
    result = _query_collection(query, where, k=5)
    return result or "Không tìm thấy quán cà phê phù hợp."


@tool
def search_hotels(query: str) -> str:
    """
    Tìm kiếm khách sạn, homestay, nơi lưu trú tại Việt Nam.
    Dùng khi user hỏi về chỗ ở, khách sạn, homestay.
    Input: câu hỏi về khách sạn, ví dụ 'khách sạn giá rẻ ở Nha Trang'
    """
    city  = _detect_city(query)
    where = (
        {
            "$and": [
                {"city":     {"$eq": city}},
                {"category": {"$eq": "hotel"}},
            ]
        }
        if city else
        {"category": {"$eq": "hotel"}}
    )
    result = _query_collection(query, where, k=5)
    return result or "Không tìm thấy khách sạn phù hợp."


@tool
def web_search(query: str) -> str:
    """
    Tìm kiếm thông tin du lịch trên internet khi không có trong database.
    Dùng khi cần thông tin về thời tiết, vé, phương tiện di chuyển, sự kiện.
    Input: câu hỏi cần tìm kiếm, ví dụ 'thời tiết Đà Lạt tháng 12'
    """
    try:
        import re
        import requests
        from urllib.parse import quote_plus

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        url      = f"https://html.duckduckgo.com/html/?q={quote_plus(query + ' Vietnam travel')}"
        res      = requests.get(url, headers=headers, timeout=8)
        pattern  = r'class="result__snippet"[^>]*>(.*?)</a>'
        matches  = re.findall(pattern, res.text, re.DOTALL)
        snippets = []
        for m in matches[:3]:
            clean = re.sub(r'<[^>]+>', '', m).strip()
            clean = ' '.join(clean.split())
            if clean and len(clean) > 30:
                snippets.append(clean)
        return "\n".join(snippets) if snippets else "Không tìm thấy thông tin."
    except Exception as e:
        return f"Lỗi tìm kiếm: {e}"


# Export danh sách tools để dùng trong agent
ALL_TOOLS = [
    search_destinations,
    search_restaurants,
    search_cafes,
    search_hotels,
    web_search,
]