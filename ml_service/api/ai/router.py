# ml_service/api/ai/router.py
import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from services.hf_gpt import HFClient
from services.features import collect_student_features
from services.ml_model import predict_topic_needs
from db.session import AsyncSessionLocal
from db.models.chat_message import ChatMessage
from db.models.chat import Chat
from config import settings
from api.ai.schemas import (
    AIMessageRequest,
    AIMessageResponse,
    ChatHistoryItem,
    ChatHistoryResponse,
    CreateChatRequest,
    CreateChatResponse,
    ChatItem,
    ChatsListResponse,
    DeleteChatResponse,
)

router = APIRouter(prefix="/api/ai")
hf_client = HFClient()
security = HTTPBearer()  # "Authorization: Bearer <token>"


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def get_user_id_from_token(access_token: str) -> uuid.UUID:
    """Извлекает user_id из JWT токена"""
    try:
        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        # В Django SimpleJWT используется 'user_id' в payload
        user_id = payload.get("user_id") or payload.get("sub")
        if user_id is None:
            raise ValueError("User ID not found in token")
        return uuid.UUID(str(user_id))
    except (JWTError, ValueError, TypeError) as e:
        raise ValueError(f"Invalid token: {e}")


# ======================
# helpers
# ======================
def build_student_context(features: dict, ml_results: dict) -> str:
    parts = []

    for topic, data in features.items():
        avg = data.get("avg_score")
        fails = data.get("fails")
        days = data.get("days_until_event")
        is_test = data.get("is_test")
        is_exam = data.get("is_exam")

        line = f"Тема: {topic}. "
        if avg is not None:
            line += f"Средняя оценка {avg}. "
        if fails:
            line += f"Провалов {fails}. "
        if days is not None:
            if is_exam:
                line += f"Экзамен через {days} дней. "
            elif is_test:
                line += f"Контрольная через {days} дней. "

        parts.append(line)

    for topic, ml in ml_results.items():
        if ml.get("need_review"):
            parts.append(f"По теме {topic} модель советует повторить материал.")

    return " ".join(parts)


# ======================
# Эндпоинты
# ======================
@router.post("/chats", response_model=CreateChatResponse)
async def create_chat(
    payload: CreateChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Создать новый чат"""
    access_token = credentials.credentials
    
    try:
        external_user_id = get_user_id_from_token(access_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный токен")
    
    # Создаем новый чат
    chat = Chat(
        external_user_id=external_user_id,
        title=payload.title,
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    
    return CreateChatResponse(
        id=str(chat.id),
        title=chat.title,
        created_at=chat.created_at.isoformat(),
    )


@router.get("/chats", response_model=ChatsListResponse)
async def get_chats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Получить список всех чатов пользователя"""
    access_token = credentials.credentials
    
    try:
        external_user_id = get_user_id_from_token(access_token)
    except ValueError:
        return ChatsListResponse(chats=[])
    
    # Получаем все чаты пользователя
    result = await db.execute(
        select(Chat)
        .where(Chat.external_user_id == external_user_id)
        .order_by(Chat.created_at.desc())
    )
    chats = result.scalars().all()
    
    # Преобразуем в формат ответа
    chat_items = [
        ChatItem(
            id=str(chat.id),
            title=chat.title,
            created_at=chat.created_at.isoformat(),
        )
        for chat in chats
    ]
    
    return ChatsListResponse(chats=chat_items)


@router.delete("/chats/{chat_id}", response_model=DeleteChatResponse)
async def delete_chat(
    chat_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Удалить чат по ID"""
    access_token = credentials.credentials
    
    try:
        external_user_id = get_user_id_from_token(access_token)
        chat_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат chat_id")
    
    # Проверяем, что чат существует и принадлежит пользователю
    chat_result = await db.execute(
        select(Chat)
        .where(Chat.id == chat_uuid)
        .where(Chat.external_user_id == external_user_id)
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    
    # Удаляем чат (сообщения удалятся автоматически благодаря CASCADE)
    db.delete(chat)
    await db.commit()
    
    return DeleteChatResponse(
        message="Чат успешно удален",
        deleted_chat_id=chat_id,
    )


@router.post("/message", response_model=AIMessageResponse)
async def message(
    payload: AIMessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    access_token = credentials.credentials
    
    # Получаем user_id из токена
    try:
        external_user_id = get_user_id_from_token(access_token)
        chat_id = uuid.UUID(payload.chat_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {e}")
    
    # Проверяем, что чат существует и принадлежит пользователю
    chat_result = await db.execute(
        select(Chat)
        .where(Chat.id == chat_id)
        .where(Chat.external_user_id == external_user_id)
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    
    features = await collect_student_features(access_token)
    ml_results = predict_topic_needs(features)
    student_context = build_student_context(features, ml_results)

    # Упрощенный промпт
    prompt = f"""
Информация о студенте:
{student_context}

Вопрос студента:
"{payload.message}"

Напиши один совет (30-50 слов) для этого студента на русском языке.
Совет должен быть конкретным и мотивирующим.
Если данных по другим предметам нет, опирайся только на то, что известно (например, {student_context}).
"""
# 🔥 ЛОГИРОВАНИЕ ЗАПРОСА (INPUT)
    print("\n" + "="*50)
    print("🚀 [INPUT] CONTEXT & PROMPT:")
    print(f"Context: {student_context}")
    print("-" * 20)
    print(f"User Msg: {payload.message}")
    print("="*50 + "\n")
    
    ai_response = await hf_client.ask(prompt)

    # Сохраняем сообщение в БД
    try:
        chat_message = ChatMessage(
            chat_id=chat_id,
            external_user_id=external_user_id,
            user_message=payload.message,
            ai_response=ai_response,
        )
        db.add(chat_message)
        await db.commit()
    except Exception as e:
        # Логируем ошибку, но не прерываем выполнение
        print(f"Error saving chat message to DB: {e}")
        await db.rollback()

    return AIMessageResponse(message=ai_response)


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    chat_id: str = Query(..., description="UUID чата"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    access_token = credentials.credentials

    try:
        external_user_id = get_user_id_from_token(access_token)
        chat_uuid = uuid.UUID(chat_id)
    except ValueError:
        return ChatHistoryResponse(messages=[])

    # проверяем чат
    chat_result = await db.execute(
        select(Chat)
        .where(Chat.id == chat_uuid)
        .where(Chat.external_user_id == external_user_id)
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        return ChatHistoryResponse(messages=[])

    # тянем сообщения
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_uuid)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    rows = result.scalars().all()

    messages: list[ChatHistoryItem] = []

    for msg in rows:
        created = msg.created_at.isoformat()

        # USER
        if msg.user_message:
            messages.append(
                ChatHistoryItem(
                    id=str(msg.id),
                    chat_id=str(msg.chat_id),
                    role="user",
                    text=msg.user_message,
                    created_at=created,
                )
            )

        # ASSISTANT
        if msg.ai_response:
            messages.append(
                ChatHistoryItem(
                    id=str(msg.id),
                    chat_id=str(msg.chat_id),
                    role="assistant",
                    text=msg.ai_response,
                    created_at=created,
                )
            )

    return ChatHistoryResponse(messages=messages)
