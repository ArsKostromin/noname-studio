from pydantic import BaseModel
from typing import List, Literal


# ======================
# Модели для сообщений
# ======================
class AIMessageRequest(BaseModel):
    message: str
    chat_id: str  # UUID чата


class AIMessageResponse(BaseModel):
    message: str


# ======================
# Модели для истории чата
# ======================
class ChatHistoryItem(BaseModel):
    id: str
    chat_id: str
    role: Literal["user", "assistant"]
    text: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    messages: List[ChatHistoryItem]


# ======================
# Модели для чатов
# ======================
class CreateChatRequest(BaseModel):
    title: str


class CreateChatResponse(BaseModel):
    id: str
    title: str
    created_at: str


class ChatItem(BaseModel):
    id: str
    title: str
    created_at: str


class ChatsListResponse(BaseModel):
    chats: list[ChatItem]


class DeleteChatResponse(BaseModel):
    message: str
    deleted_chat_id: str
