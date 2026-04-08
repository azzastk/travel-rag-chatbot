import os
from dotenv import load_dotenv

load_dotenv()

# === Paths ===
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR  = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(ROOT_DIR, "data", "travel_dataset.json")

# === LLM — Google Gemini ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL      = "gemini-2.0-flash"

# === Embedding — multilingual ===
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# === RAG ===
RETRIEVER_TOP_K = 8