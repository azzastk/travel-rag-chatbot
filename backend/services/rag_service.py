import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from rag.retriever import get_retriever

SIMILARITY_THRESHOLD = 0.5  # cosine distance (0=giống hệt, 1=hoàn toàn khác)


def retrieve_context(question: str) -> str:
    try:
        retriever = get_retriever()
        docs = retriever.invoke(question)

        if not docs:
            print("[RAG] Không có document nào đủ liên quan → fallback web search")
            return ""

        context = "\n\n".join([doc.page_content for doc in docs])
        return context

    except RuntimeError as e:
        print(f"[RAG] Warning: {e}")
        return ""