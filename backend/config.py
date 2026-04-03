import os
from dotenv import load_dotenv

load_dotenv()

# === Paths ===
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR  = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(ROOT_DIR, "data", "travel_dataset.json")

# === LLM ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL    = "llama-3.1-8b-instant"

# === Embedding — multilingual, hỗ trợ tiếng Việt lẫn tiếng Anh ===
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# === RAG ===
# Top K cao hơn vì sau khi filter city/category thì ít kết quả hơn
RETRIEVER_TOP_K = 8