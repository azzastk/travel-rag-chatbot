import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
from config import GROQ_API_KEY, LLM_MODEL

from groq import Groq
from services.rag_service import retrieve_context
from services.web_search_service import search_web
from prompts.travel_prompt import SYSTEM_PROMPT

client = Groq(api_key=GROQ_API_KEY)


def ask_chatbot(question: str) -> str:
    # 1. Thử RAG trước
    context = retrieve_context(question)

    # 2. Fallback web search nếu RAG không có kết quả
    if not context:
        context = search_web(question)

    prompt = f"""{SYSTEM_PROMPT}

Context:
{context if context else "No context available."}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content