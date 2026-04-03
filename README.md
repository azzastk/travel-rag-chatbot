---
title: VietTravel AI
emoji: 🌏
colorFrom: green
colorTo: yellow
sdk: docker
pinned: true
---

# 🌏 VietTravel AI — Smart Travel Assistant Chatbot

> Trợ lý du lịch thông minh cho Việt Nam · Bilingual travel assistant for Vietnam

[![Live Demo](https://img.shields.io/badge/🤗%20Live%20Demo-HuggingFace%20Spaces-FFD21E?style=for-the-badge)](https://huggingface.co/spaces/Azza1610/viettravel-ai)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-llama--3.1-F55036?style=for-the-badge)](https://groq.com)

---

## Giới thiệu / Overview

**VI:** VietTravel AI là chatbot du lịch thông minh sử dụng kiến trúc **RAG (Retrieval-Augmented Generation)** kết hợp với **multilingual embedding** để hiểu câu hỏi bằng cả tiếng Việt lẫn tiếng Anh. Chatbot có thể gợi ý địa điểm tham quan, quán cà phê, nhà hàng và khách sạn tại 17 tỉnh thành Việt Nam.

**EN:** VietTravel AI is an intelligent travel chatbot using **RAG** architecture with **multilingual embedding** to understand queries in both Vietnamese and English. It recommends destinations, cafes, restaurants, and hotels across 17 cities in Vietnam.

---

## Tính năng / Features

- 🔍 **RAG + Metadata Filter** — tìm kiếm ngữ nghĩa kết hợp filter city + category → kết quả chính xác đúng thành phố, đúng loại hình
- 🧠 **Multilingual Embedding** — model `paraphrase-multilingual-MiniLM-L12-v2` hiểu cả tiếng Việt lẫn tiếng Anh
- 💬 **Chat History** — nhớ ngữ cảnh hội thoại, không lặp lại gợi ý cũ, hiểu câu hỏi tiếp theo
- 🌐 **Web Search Fallback** — tự động tìm DuckDuckGo khi không có dữ liệu trong vector DB
- 🗺️ **17 thành phố** — TPHCM, Hà Nội, Đà Nẵng, Hội An, Nha Trang, Đà Lạt, Huế, Cần Thơ, Phú Quốc, Vũng Tàu, Hạ Long, Sa Pa, Mũi Né, Phan Thiết, Phong Nha, Kon Tum, Buôn Ma Thuột
- 🎨 **Bilingual UI** — giao diện chat song ngữ Anh/Việt với travel theme

---

## Kiến trúc / Architecture

```
User Question
     │
     ▼
Detect city + category từ câu hỏi + history
     │
     ▼
ChromaDB metadata filter (city + category)
     │
     ├── Có kết quả → RAG context
     └── Không có → DuckDuckGo web search
                          │
                          ▼
              Groq API (llama-3.1-8b-instant)
              + Chat history (6 tin nhắn gần nhất)
              + Danh sách đã gợi ý (tránh lặp)
                          │
                          ▼
                    Câu trả lời
```

---

## Tech Stack

| Layer         | Technology                            |
| ------------- | ------------------------------------- |
| **LLM**       | Groq API — llama-3.1-8b-instant       |
| **Embedding** | paraphrase-multilingual-MiniLM-L12-v2 |
| **Vector DB** | ChromaDB in-memory                    |
| **Backend**   | FastAPI + Python 3.11                 |
| **Frontend**  | HTML / CSS / Vanilla JS               |
| **Deploy**    | Hugging Face Spaces (Docker)          |

---

## Cấu trúc dự án / Project Structure

```
travel-rag-chatbot/
├── Dockerfile
├── requirements.txt
├── data/
│   └── travel_dataset.json       # 56 điểm đến du lịch
├── frontend/
│   └── index.html                # Giao diện chat
└── backend/
    ├── main.py
    ├── config.py
    ├── schemas/chat_schema.py
    ├── prompts/travel_prompt.py
    ├── rag/
    │   ├── ingest_data.py
    │   └── retriever.py
    └── services/
        ├── chatbot_service.py
        ├── rag_service.py
        └── web_search_service.py
```

---

## Chạy local / Run Locally

```bash
# 1. Clone
git clone https://github.com/azzastk/travel-rag-chatbot.git
cd travel-rag-chatbot

# 2. Môi trường ảo
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Tạo .env
cp .env.example .env
# Điền GROQ_API_KEY vào .env

# 5. Khởi động
cd backend
uvicorn main:app --reload
```

Mở **http://localhost:8000**

---

## API

| Method | Endpoint  | Mô tả          |
| ------ | --------- | -------------- |
| GET    | `/`       | Giao diện chat |
| GET    | `/health` | Health check   |
| POST   | `/chat`   | Gửi câu hỏi    |

```json
// Request
{ "message": "Gợi ý quán cà phê ở Đà Nẵng", "history": [] }

// Response
{ "answer": "Ở Đà Nẵng mình hay dẫn khách đến Nắng Café..." }
```

---

## Deploy on Hugging Face Spaces

```bash
git remote add space https://huggingface.co/spaces/Azza1610/viettravel-ai
git push space main
```

Thêm secret `GROQ_API_KEY` tại **Settings → Variables and secrets**.
