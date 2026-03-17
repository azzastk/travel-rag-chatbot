import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
from config import RETRIEVER_TOP_K

from rag.retriever import get_retriever


SIMILARITY_THRESHOLD = 0.8


def retrieve_context(question: str) -> str:
    try:
        retriever = get_retriever()

        # Dùng similarity_search_with_score thay vì invoke
        # để lấy được score và filter document không liên quan
        vector_db = retriever.vectorstore
        results = vector_db.similarity_search_with_score(
            question,
            k=RETRIEVER_TOP_K
        )

        if not results:
            return ""

        # Filter — chỉ giữ document có score dưới ngưỡng (càng nhỏ càng liên quan)
        relevant_docs = []
        print("\n[RAG] Documents retrieved:")
        for doc, score in results:
            location = doc.metadata.get("location", "?")
            city     = doc.metadata.get("city", "?")
            print(f"  {'✅' if score < SIMILARITY_THRESHOLD else '❌'} "
                  f"{location} — {city} (score: {score:.3f})")
            if score < SIMILARITY_THRESHOLD:
                relevant_docs.append(doc)

        if not relevant_docs:
            print("[RAG] Không có document nào đủ liên quan → fallback web search")
            return ""

        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        return context

    except RuntimeError as e:
        print(f"[RAG] Warning: {e}")
        return ""