from pydantic import BaseModel


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
    user_message: str
    ai_response: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    messages: list[ChatHistoryItem]


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
