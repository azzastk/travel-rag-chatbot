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


def ask_chatbot(question: str, history: list = []) -> str:
    context = retrieve_context(question)

    if not context:
        context = search_web(question)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    
    for msg in history[-6:]:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    if context:
        user_content = f"Context:\n{context}\n\nQuestion:\n{question}"
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