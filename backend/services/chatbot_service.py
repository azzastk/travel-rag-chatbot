"""
Chatbot service — giờ chỉ là wrapper gọi LangChain Agent.
"""
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from agents.travel_agent import run_agent


def ask_chatbot(question: str, history: list = []) -> str:
    """
    Gọi LangChain Agent để trả lời câu hỏi.
    Agent tự quyết định dùng tool nào phù hợp.
    """
    print(f"\n[Agent] Question: {question}")
    return run_agent(question, history)