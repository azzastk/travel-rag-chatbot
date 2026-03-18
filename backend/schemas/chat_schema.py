from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    role: str      # "user" hoặc "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []


class ChatResponse(BaseModel):
    answer: str