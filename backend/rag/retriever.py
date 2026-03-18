import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
from config import RETRIEVER_TOP_K

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

_retriever = None

def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever
    raise RuntimeError("Retriever chưa được khởi tạo. Gọi init_retriever() khi startup trước.")

def init_retriever(documents):
    
    global _retriever

    from chromadb.utils import embedding_functions
    import chromadb

    
    client = chromadb.Client()
    ef = embedding_functions.DefaultEmbeddingFunction()

    collection = client.create_collection(
        name="travel",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    # Thêm documents vào collection
    ids        = [str(i) for i in range(len(documents))]
    texts      = [doc.page_content for doc in documents]
    metadatas  = [doc.metadata for doc in documents]

    collection.add(ids=ids, documents=texts, metadatas=metadatas)

    # Wrap thành retriever đơn giản
    class SimpleRetriever:
        def __init__(self, col, k, threshold):
            self.col = col
            self.k = k
            self.threshold = threshold

        def invoke(self, question: str):
            results = self.col.query(
                query_texts=[question],
                n_results=self.k,
                include=["documents", "metadatas", "distances"]
            )
            docs = []
            print("\n[RAG] Documents retrieved:")
            for i, (text, meta, dist) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                score = dist
                location = meta.get("location", "?")
                city = meta.get("city", "?")
                relevant = score < 0.5  # cosine distance threshold
                print(f"  {'✅' if relevant else '❌'} {location} — {city} (score: {score:.3f})")
                if relevant:
                    from langchain.schema import Document
                    docs.append(Document(page_content=text, metadata=meta))
            return docs

    _retriever = SimpleRetriever(collection, RETRIEVER_TOP_K, 0.5)
    print(f"✅ Retriever đã sẵn sàng — {len(documents)} documents trong memory")
    return _retriever