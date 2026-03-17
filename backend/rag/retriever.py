import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
from config import EMBEDDING_MODEL, RETRIEVER_TOP_K

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Singleton — khởi tạo một lần, dùng lại cho mọi request
_retriever = None

def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    raise RuntimeError(
        "Retriever chưa được khởi tạo. "
        "Gọi init_retriever() khi startup trước."
    )

def init_retriever(documents):
    global _retriever

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="travel",
    )

    _retriever = vector_db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": RETRIEVER_TOP_K,
            "score_threshold": 0.3,
        }
    )

    print(f"✅ Retriever đã sẵn sàng — {len(documents)} documents trong memory")
    return _retriever