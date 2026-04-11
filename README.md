---
title: VietTravel AI
emoji: 🌏
colorFrom: green
colorTo: yellow
sdk: docker
pinned: true
---

# 🌏 VietTravel AI — Smart Travel Assistant Chatbot

> Trợ lý du lịch thông minh cho Việt Nam · Bilingual AI travel assistant powered by LangChain Agent + RAG

[![Live Demo](https://img.shields.io/badge/🤗%20Live%20Demo-HuggingFace-FFD21E?style=for-the-badge)](https://huggingface.co/spaces/Azza1610/viettravel-ai)
[![GitHub](https://img.shields.io/badge/GitHub-azzastk-181717?style=for-the-badge&logo=github)](https://github.com/azzastk/travel-rag-chatbot)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=for-the-badge)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3-F55036?style=for-the-badge)](https://groq.com)

---

## 📌 Giới thiệu / Overview

**VI:** VietTravel AI là chatbot du lịch thông minh kết hợp **LangChain Agent** và **RAG (Retrieval-Augmented Generation)** để tìm kiếm chính xác thông tin về địa điểm tham quan, nhà hàng, quán cà phê và khách sạn tại 17 tỉnh thành Việt Nam. Agent tự động lựa chọn tool phù hợp với từng câu hỏi, hỗ trợ lập lịch trình du lịch phức tạp nhiều ngày.

**EN:** VietTravel AI is an intelligent travel chatbot combining **LangChain Agent** and **RAG** to accurately find information about destinations, restaurants, cafes and hotels across 17 cities in Vietnam. The agent automatically selects the right tool for each query and supports complex multi-day itinerary planning.

---

## ✨ Tính năng / Features

- 🤖 **LangChain Agent** — tự động chọn tool phù hợp, multi-step reasoning cho lịch trình phức tạp
- 🔍 **RAG + Metadata Filter** — ChromaDB filter theo city + category → kết quả chính xác đúng thành phố
- 🧠 **Multilingual Embedding** — `paraphrase-multilingual-MiniLM-L12-v2` hiểu tiếng Việt lẫn tiếng Anh
- 💬 **Chat History** — nhớ ngữ cảnh, không lặp gợi ý cũ, hiểu câu hỏi tiếp theo
- 🌐 **Web Search Fallback** — DuckDuckGo khi không có dữ liệu trong vector DB
- 🗺️ **17 thành phố** — TPHCM, Hà Nội, Đà Nẵng, Hội An, Nha Trang, Đà Lạt, Huế, Cần Thơ, Phú Quốc, Vũng Tàu, Hạ Long, Sa Pa, Mũi Né, Phan Thiết, Phong Nha, Kon Tum, Buôn Ma Thuột
- 🎨 **Bilingual UI** — giao diện chat song ngữ Anh/Việt với travel theme

---

## 🏗️ Kiến trúc / Architecture

```
User Question
      │
      ▼
LangChain Agent (llama-3.3-70b via Groq)
      │
      ├── search_destinations  → ChromaDB (city filter, exclude hotel/cafe)
      ├── search_restaurants   → ChromaDB (city + category=restaurant)
      ├── search_cafes         → ChromaDB (city + category=coffee)
      ├── search_hotels        → ChromaDB (city + category=hotel)
      └── web_search           → DuckDuckGo HTML scraping
                │
                ▼
    Agent tổng hợp → Câu trả lời / Lịch trình
```

**Ví dụ itinerary flow:**

```
"Lập lịch 3 ngày Đà Nẵng, budget 5 triệu"
  → search_destinations → search_restaurants
  → search_cafes → search_hotels
  → Lịch trình 3 ngày chi tiết theo ngày
```

---

## 🛠️ Tech Stack

| Layer         | Technology                                  |
| ------------- | ------------------------------------------- |
| **Agent**     | LangChain 0.3 + `create_tool_calling_agent` |
| **LLM**       | Groq API — llama-3.3-70b-versatile          |
| **Embedding** | paraphrase-multilingual-MiniLM-L12-v2       |
| **Vector DB** | ChromaDB in-memory                          |
| **Backend**   | FastAPI 0.115 + Python 3.12                 |
| **Frontend**  | HTML / CSS / Vanilla JS                     |
| **Deploy**    | Hugging Face Spaces (Docker)                |

---

## 📁 Cấu trúc dự án / Project Structure

```
travel-rag-chatbot/
├── Dockerfile
├── requirements.txt
├── .env.example
├── data/
│   ├── travel_dataset.json      # 56 điểm đến du lịch
│   └── places_dataset.json      # ~3000 cà phê, nhà hàng, khách sạn
├── frontend/
│   └── index.html
└── backend/
    ├── main.py
    ├── config.py
    ├── schemas/chat_schema.py
    ├── prompts/travel_prompt.py
    ├── rag/
    │   ├── ingest_data.py
    │   └── retriever.py
    ├── agents/
    │   ├── travel_agent.py      # LangChain Agent
    │   └── tools/
    │       └── rag_tools.py     # 5 tools: destinations, restaurants,
    │                            #          cafes, hotels, web_search
    └── services/
        └── chatbot_service.py
```

---

## ⚙️ Chạy local / Run Locally

### Yêu cầu

- Python 3.12+
- Groq API key miễn phí tại [console.groq.com](https://console.groq.com)

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

# 5. Tạo __init__.py
type nul > backend\__init__.py
type nul > backend\schemas\__init__.py
type nul > backend\prompts\__init__.py
type nul > backend\rag\__init__.py
type nul > backend\agents\__init__.py
type nul > backend\agents\tools\__init__.py
type nul > backend\services\__init__.py

# 6. Khởi động
cd backend
uvicorn main:app --reload
```

Mở **http://localhost:8000**

---

## 📝 API

| Method | Endpoint  | Mô tả          |
| ------ | --------- | -------------- |
| GET    | `/`       | Giao diện chat |
| GET    | `/health` | Health check   |
| POST   | `/chat`   | Gửi câu hỏi    |

```json
// Request
{ "message": "Lập lịch 3 ngày ở Đà Nẵng", "history": [] }

// Response
{ "answer": "Đây là lịch trình 3 ngày Đà Nẵng cho bạn!..." }
```

---

## 📊 Dataset

| File                  | Nội dung                    | Records |
| --------------------- | --------------------------- | ------- |
| `travel_dataset.json` | Địa danh, điểm tham quan    | 56      |
| `places_dataset.json` | Cà phê, nhà hàng, khách sạn | ~3000   |

---

## 🚀 Deploy on Hugging Face Spaces

```bash
git remote add space https://huggingface.co/spaces/Azza1610/viettravel-ai
git push space main
```

Thêm secret `GROQ_API_KEY` tại **Settings → Variables and secrets**.
