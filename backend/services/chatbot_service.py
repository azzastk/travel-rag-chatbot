import os
import sys
import re

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
from config import GROQ_API_KEY, LLM_MODEL

from groq import Groq
from services.rag_service import (
    retrieve_context, _detect_city, _detect_category, _is_general_query
)
from services.web_search_service import search_web
from prompts.travel_prompt import SYSTEM_PROMPT

client = Groq(api_key=GROQ_API_KEY)


def _extract_suggested_places(history: list) -> list:
    """Trích xuất tên các địa điểm đã gợi ý để tránh lặp lại."""
    suggested = []
    for msg in history:
        if msg.role == "assistant":
            lines = msg.content.split("\n")
            for line in lines:
                line = line.strip().lstrip("-–•* ")
                match = re.match(r"^([^:,—\-]{5,60}?)[\s]*(?:[:,—]|$)", line)
                if match:
                    name = match.group(1).strip()
                    if name and len(name) > 3:
                        suggested.append(name)
    return list(set(suggested))


def _get_context_from_history(history: list) -> dict:
    """Duyệt toàn bộ history để tìm city và category gần nhất."""
    city     = ""
    category = ""
    for msg in reversed(history):
        if msg.role == "user":
            if not city:
                city = _detect_city(msg.content)
            if not category:
                category = _detect_category(msg.content)
            if city and category:
                break
    return {"city": city, "category": category}


def _build_rag_query(question: str, history: list) -> str:
    """Xây dựng RAG query đầy đủ ngữ cảnh từ history."""
    if not history:
        return question

    current_city     = _detect_city(question)
    current_category = _detect_category(question)
    is_general       = _is_general_query(question)

    # Đã đủ thông tin
    if current_city and current_category:
        return question

    ctx          = _get_context_from_history(history)
    history_city = ctx["city"]
    history_cat  = ctx["category"]

    parts = [question]

    # Ghép city nếu thiếu
    if not current_city and history_city:
        parts.append(f"ở {history_city}")

    # Ghép category chỉ khi câu hỏi KHÔNG phải tổng quát
    if not current_category and history_cat and not is_general:
        parts.append(history_cat)

    return " ".join(parts).strip()


def ask_chatbot(question: str, history: list = []) -> str:
    # 1. Build RAG query
    rag_query = _build_rag_query(question, history)
    print(f"\n[RAG Query] {rag_query}")

    # 2. RAG
    context = retrieve_context(rag_query)

    # 3. Fallback web search
    if not context:
        context = search_web(rag_query)

    # 4. Địa điểm đã gợi ý
    suggested_places = _extract_suggested_places(history)

    # 5. Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-6:]:
        messages.append({"role": msg.role, "content": msg.content})

    if context:
        user_content = f"Context:\n{context}\n\n"
        if suggested_places:
            user_content += (
                f"Places already suggested (DO NOT repeat these):\n"
                f"{', '.join(suggested_places)}\n\n"
            )
        user_content += f"Question:\n{question}"
    else:
        user_content = question

    messages.append({"role": "user", "content": user_content})

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content