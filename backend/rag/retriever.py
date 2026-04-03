import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
from config import RETRIEVER_TOP_K, EMBEDDING_MODEL

_retriever = None

def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever
    raise RuntimeError("Retriever chưa được khởi tạo. Gọi init_retriever() khi startup trước.")

def init_retriever(documents):
    """
    Khởi tạo ChromaDB in-memory với multilingual embedding model.
    Hỗ trợ query tiếng Việt match với data tiếng Anh.
    """
    global _retriever

    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    # Dùng multilingual model thay vì all-MiniLM-L6-v2
    ef = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

    client     = chromadb.Client()
    collection = client.create_collection(
        name="travel",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    # Chia batch 100 để tránh lỗi "exceeds maximum batch size"
    BATCH_SIZE = 100
    total      = len(documents)

    for i in range(0, total, BATCH_SIZE):
        batch     = documents[i:i + BATCH_SIZE]
        ids       = [str(i + j) for j in range(len(batch))]
        texts     = [doc.page_content for doc in batch]
        metadatas = [doc.metadata for doc in batch]
        collection.add(ids=ids, documents=texts, metadatas=metadatas)
        print(f"  📦 Batch {i // BATCH_SIZE + 1}: {i + len(batch)}/{total} docs")

    class SimpleRetriever:
        def __init__(self, col, k):
            self.col = col
            self.k   = k

        def invoke(self, question: str, threshold: float = 0.6):
            results = self.col.query(
                query_texts=[question],
                n_results=self.k,
                include=["documents", "metadatas", "distances"]
            )

            docs = []
            print("\n[RAG] Documents retrieved:")
            for text, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                name     = meta.get("name") or meta.get("location", "?")
                city     = meta.get("city", "?")
                relevant = dist < threshold
                print(f"  {'✅' if relevant else '❌'} {name} — {city} (score: {dist:.3f})")
                if relevant:
                    from langchain.schema import Document
                    docs.append(Document(page_content=text, metadata=meta))
            return docs

    _retriever = SimpleRetriever(collection, RETRIEVER_TOP_K)
    print(f"✅ Retriever sẵn sàng — {total} documents | model: {EMBEDDING_MODEL}")
    return _retriever