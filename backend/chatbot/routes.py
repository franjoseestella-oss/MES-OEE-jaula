"""Endpoints del chatbot en FastAPI."""

import markdown
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from chatbot.agent import run_chat

router = APIRouter(prefix="/api/v1/chat")


class ChatMessage(BaseModel):
    role: str        # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    machine_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    reply_html: str


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    msgs = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = run_chat(msgs, machine_id_hint=req.machine_id)
    reply_html = markdown.markdown(reply, extensions=["tables", "fenced_code"])
    return ChatResponse(reply=reply, reply_html=reply_html)
