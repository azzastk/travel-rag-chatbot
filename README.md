# 🌏 VietTravel AI — Smart Travel Assistant Chatbot

> **Trợ lý du lịch thông minh** giúp du khách khám phá các điểm đến tại Việt Nam thông qua giao diện chat tự nhiên, song ngữ Anh - Việt.
>
> An **intelligent travel assistant** helping tourists discover destinations across Vietnam through a natural bilingual (EN/VI) chat interface.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=for-the-badge&logo=render)](https://viettravel-ai.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

---

## 📌 Giới thiệu / Overview

**VI:** VietTravel AI là chatbot du lịch được xây dựng theo kiến trúc **RAG (Retrieval-Augmented Generation)** — kết hợp tìm kiếm ngữ nghĩa trong cơ sở dữ liệu vector với mô hình ngôn ngữ lớn để đưa ra câu trả lời chính xác, có ngữ cảnh về các điểm đến du lịch tại Việt Nam.

**EN:** VietTravel AI is a travel chatbot built on **RAG (Retrieval-Augmented Generation)** architecture — combining semantic search over a vector database with a large language model to deliver accurate, context-aware answers about travel destinations in Vietnam.

**Tính năng nổi bật / Key Features:**

- 🔍 RAG pipeline với similarity threshold — chỉ trả context thực sự liên quan
- 🌐 Web search fallback — tự động tìm DuckDuckGo khi không có dữ liệu
- ⚡ ChromaDB in-memory — không cần persist, tự load khi server khởi động
- 🎨 Giao diện chat song ngữ Anh/Việt với travel theme
- 🚀 Deploy sẵn trên Render free tier

---

## 🏗️ Kiến trúc hệ thống / System Architecture

```
User (Browser)
     │
     ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌─────────────────────────────┐   │
│  │      /chat endpoint          │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │     Chatbot Service          │   │
│  │  1. RAG → retrieve context   │   │
│  │  2. Fallback → Web Search    │   │
│  │  3. LLM → generate answer    │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│    ┌────────┴────────┐             │
│    ▼                 ▼             │
│ ┌──────────┐  ┌────────────────┐  │
│ │ChromaDB  │  │ DuckDuckGo API │  │
│ │(in-memory│  │  (web search   │  │
│ │ vectors) │  │   fallback)    │  │
│ └──────────┘  └────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │        Groq API              │  │
│  │   llama-3.1-8b-instant       │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Luồng xử lý / Request Flow:**

1. User gửi câu hỏi → FastAPI nhận request
2. `chatbot_service` gọi RAG tìm context trong ChromaDB
3. Lọc document theo **cosine distance threshold (≤ 0.5)** — loại bỏ kết quả không liên quan
4. Nếu không có context → fallback DuckDuckGo web search
5. Context + prompt → Groq API (llama-3.1-8b-instant) sinh câu trả lời
6. Trả kết quả về người dùng

---

## 🛠️ Tech Stack

| Layer         | Technology                                    | Lý do chọn / Reason                                 |
| ------------- | --------------------------------------------- | --------------------------------------------------- |
| **LLM**       | Groq API (llama-3.1-8b-instant)               | Miễn phí, ~500 tokens/s, không cần GPU              |
| **Embedding** | ChromaDB built-in (all-MiniLM-L6-v2 via ONNX) | Không cần PyTorch, ~150MB RAM, fit Render free tier |
| **Vector DB** | ChromaDB in-memory                            | Không lo mất data khi Render restart                |
| **Backend**   | FastAPI + Python 3.10                         | Async, auto Swagger docs, production-ready          |
| **Frontend**  | Vanilla HTML/CSS/JS                           | Không cần build step, deploy đơn giản               |
| **Deploy**    | Render free tier                              | CI/CD tự động từ GitHub                             |

---

## 📁 Cấu trúc thư mục / Project Structure

```
travel-rag-chatbot/
├── .env.example              # Template cấu hình môi trường
├── .gitignore
├── render.yaml               # Cấu hình deploy Render
├── requirements.txt
├── README.md
│
├── data/
│   └── travel_dataset.json   # 56 điểm đến du lịch Việt Nam
│
├── frontend/
│   └── index.html            # Giao diện chat song ngữ
│
└── backend/
    ├── main.py               # FastAPI app, serve frontend, startup events
    ├── config.py             # Cấu hình tập trung
    ├── schemas/
    │   └── chat_schema.py    # Pydantic models
    ├── prompts/
    │   └── travel_prompt.py  # System prompt cho LLM
    ├── rag/
    │   ├── ingest_data.py    # Load JSON → Document objects
    │   └── retriever.py      # ChromaDB in-memory, lazy init
    └── services/
        ├── chatbot_service.py     # Orchestrator chính
        ├── rag_service.py         # RAG + similarity filtering
        └── web_search_service.py  # DuckDuckGo fallback
```

---

## ⚙️ Chạy local / Run Locally

### Yêu cầu / Requirements

- Python 3.10+
- Groq API key miễn phí tại [console.groq.com](https://console.groq.com)

### Các bước / Steps

```bash
# 1. Clone repo
git clone https://github.com/azzastk/travel-rag-chatbot.git
cd travel-rag-chatbot

# 2. Tạo môi trường ảo
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Tạo file .env
cp .env.example .env
# Mở .env và điền GROQ_API_KEY của bạn

# 5. Tạo __init__.py (Windows)
type nul > backend\__init__.py
type nul > backend\schemas\__init__.py
type nul > backend\prompts\__init__.py
type nul > backend\rag\__init__.py
type nul > backend\services\__init__.py

# 6. Khởi động server
cd backend
uvicorn main:app --reload
```

Mở trình duyệt tại **http://localhost:8000**

---

## 📊 Dataset

`data/travel_dataset.json` gồm **56 điểm đến** trên khắp Việt Nam:

| Trường / Field | Mô tả / Description                   |
| -------------- | ------------------------------------- |
| `location`     | Tên địa điểm                          |
| `city`         | Thành phố / tỉnh                      |
| `type`         | Loại hình (nature, beach, culture...) |
| `region`       | Miền (north, central, south)          |
| `price`        | Mức giá (budget, medium, high)        |
| `activities`   | Hoạt động có thể làm                  |
| `best_time`    | Thời điểm tốt nhất để ghé thăm        |
| `text`         | Nội dung được dùng để tạo embeddings  |

---

## 📝 API Documentation

Swagger UI tự động tại: `{BASE_URL}/docs`

| Method | Endpoint  | Mô tả                         |
| ------ | --------- | ----------------------------- |
| `GET`  | `/`       | Serve giao diện chat          |
| `GET`  | `/health` | Health check                  |
| `POST` | `/chat`   | Gửi câu hỏi, nhận câu trả lời |

**Request:**

```json
{ "message": "What are the best beaches in Vietnam?" }
```

**Response:**

```json
{ "answer": "Vietnam has stunning beaches! I recommend..." }
```
