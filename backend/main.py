import sys
import os

# Thêm backend/ vào sys.path để import các module nội bộ
# Cần thiết khi chạy từ thư mục gốc: uvicorn backend.main:app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from schemas.chat_schema import ChatRequest
from services.chatbot_service import ask_chatbot
from rag.ingest_data import load_documents
from rag.retriever import init_retriever


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Loading travel data into memory...")
    documents = load_documents()
    init_retriever(documents)
    yield


app = FastAPI(title="VietTravel AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


@app.get("/")
def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "VietTravel AI is running. Frontend not found."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        answer = ask_chatbot(req.message)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")