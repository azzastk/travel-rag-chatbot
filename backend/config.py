import os
from dotenv import load_dotenv

load_dotenv()

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(ROOT_DIR, "data", "travel_dataset.json")

# === LLM ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = "llama-3.1-8b-instant"

# === Embedding ===
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# === RAG ===
RETRIEVER_TOP_K = 3
SIMILARITY_THRESHOLD = 1.2