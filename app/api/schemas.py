from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from app.domain.messages import ChatHistoryMessage


class ChatObject(BaseModel):
    type: str
    id: str
    title: str | None = None
    attributes: dict = {}


class ChatRequest(BaseModel):
    sender_id: str
    message_id: str | None = None
    text: str | None = None
    object: ChatObject | None = None


class ChatBotMessage(BaseModel):
    text: str | None = None
    object: ChatObject | None = None


class ChatResponse(BaseModel):
    sender_id: str
    message_id: str
    messages: list[ChatBotMessage]


class HistoryMessage(BaseModel):
    role: str  # user or bot
    text: str | None = None
    object: ChatObject | None = None


class HistoryResponse(BaseModel):
    sender_id: str
    messages: list[HistoryMessage]

class ChatMessageResponse(BaseModel):
    sender_id: str
    messages: list[ChatHistoryMessage]
