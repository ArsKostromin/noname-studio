# ml_service/api/ai/router.py
import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
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
    EditMessageRequest,
)
from fastapi import Response


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


async def get_chat_history_before_message(
    db: AsyncSession,
    chat_id: uuid.UUID,
    message_id: uuid.UUID,
) -> list[ChatMessage]:
    """Получить историю чата до указанного сообщения (для контекста)"""
    # Сначала получаем время создания редактируемого сообщения
    msg_result = await db.execute(
        select(ChatMessage.created_at)
        .where(ChatMessage.id == message_id)
    )
    msg_time = msg_result.scalar_one_or_none()
    
    if not msg_time:
        return []
    
    # Получаем все сообщения до этого времени
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .where(ChatMessage.id != message_id)
        .where(ChatMessage.created_at < msg_time)
        .order_by(ChatMessage.created_at.asc())
    )
    return result.scalars().all()


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


@router.post("/message")
async def message(
    payload: AIMessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    access_token = credentials.credentials
    
    print(f"\n{'='*50}")
    print(f"📨 [MESSAGE] POST /api/ai/message - НОВЫЙ ЗАПРОС")
    print(f"{'='*50}")
    
    # Получаем user_id из токена
    try:
        external_user_id = get_user_id_from_token(access_token)
        chat_id = uuid.UUID(payload.chat_id)
        print(f"✅ [MESSAGE] User ID из токена: {external_user_id}")
        print(f"✅ [MESSAGE] Chat ID из запроса: {chat_id}")
    except ValueError as e:
        print(f"❌ [MESSAGE] Ошибка парсинга данных: {e}")
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {e}")
    
    # Проверяем, что чат существует и принадлежит пользователю
    print(f"🔍 [MESSAGE] Проверяем существование чата...")
    chat_result = await db.execute(
        select(Chat)
        .where(Chat.id == chat_id)
        .where(Chat.external_user_id == external_user_id)
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        print(f"❌ [MESSAGE] Чат не найден или не принадлежит пользователю")
        raise HTTPException(status_code=404, detail="Чат не найден")
    print(f"✅ [MESSAGE] Чат найден: {chat.title}")
    
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
    
    # Собираем полный ответ для сохранения в БД
    full_response = ""
    chunk_count = 0
    
    print(f"📨 [MESSAGE] Начало обработки запроса")
    print(f"📨 [MESSAGE] Chat ID: {chat_id}")
    print(f"📨 [MESSAGE] User message: {payload.message[:100]}...")
    
    async def stream_generator():
        nonlocal full_response, chunk_count
        try:
            print(f"🔄 [MESSAGE] Начало стриминга от HF")
            async for chunk in hf_client.ask_stream(prompt):
                if chunk:
                    full_response += chunk
                    chunk_count += 1
                    print(f"📦 [MESSAGE] Получен chunk #{chunk_count}, длина: {len(chunk)}, всего: {len(full_response)} символов")
                    # Отправляем Markdown напрямую без оборачивания в data:
                    yield chunk
                else:
                    print(f"⚠️ [MESSAGE] Получен пустой chunk")
            
            print(f"✅ [MESSAGE] Стриминг завершен")
            print(f"📊 [MESSAGE] Всего чанков: {chunk_count}")
            print(f"📊 [MESSAGE] Полная длина ответа: {len(full_response)} символов")
            print(f"📊 [MESSAGE] Ответ (первые 200 символов): {full_response[:200]}...")
            
            # Сохраняем в БД после завершения стриминга
            if full_response and full_response.strip():
                try:
                    print(f"💾 [MESSAGE] Сохраняем сообщение в БД...")
                    chat_message = ChatMessage(
                        chat_id=chat_id,
                        external_user_id=external_user_id,
                        user_message=payload.message,
                        ai_response=full_response.strip(),
                    )
                    db.add(chat_message)
                    await db.flush()
                    await db.commit()
                    await db.refresh(chat_message)
                    print(f"✅ [MESSAGE] Сообщение успешно сохранено в БД")
                    print(f"✅ [MESSAGE] ID сообщения: {chat_message.id}")
                    print(f"✅ [MESSAGE] Проверка ai_response: '{chat_message.ai_response[:100]}...'")
                except Exception as e:
                    print(f"❌ [MESSAGE] Ошибка сохранения в БД: {e}")
                    import traceback
                    traceback.print_exc()
                    try:
                        await db.rollback()
                    except:
                        pass
            else:
                print(f"⚠️ [MESSAGE] Пустой ответ от AI (длина: {len(full_response)}), не сохраняем в БД")
        except Exception as e:
            print(f"❌ [MESSAGE] Ошибка в stream generator: {e}")
            import traceback
            traceback.print_exc()
            yield f"Произошла ошибка при получении ответа.\n"
        
    return StreamingResponse(
        stream_generator(),
        media_type="text/markdown; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


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


@router.patch("/messages/{message_id}")
async def edit_message(
    message_id: str,
    payload: EditMessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Редактировать сообщение пользователя и получить новый ответ от AI"""
    access_token = credentials.credentials
    
    try:
        external_user_id = get_user_id_from_token(access_token)
        msg_uuid = uuid.UUID(message_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат данных: {e}")
    
    # Находим сообщение
    msg_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.id == msg_uuid)
        .where(ChatMessage.external_user_id == external_user_id)
    )
    chat_message = msg_result.scalar_one_or_none()
    if not chat_message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    
    # Проверяем, что чат принадлежит пользователю
    chat_result = await db.execute(
        select(Chat)
        .where(Chat.id == chat_message.chat_id)
        .where(Chat.external_user_id == external_user_id)
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    
    # Получаем историю чата до этого сообщения для контекста
    history_messages = await get_chat_history_before_message(
        db, chat_message.chat_id, msg_uuid
    )
    
    # Сохраняем время создания редактируемого сообщения
    edit_message_time = chat_message.created_at
    
    # Удаляем все сообщения после редактируемого (как в ChatGPT)
    # Удаляем сообщения, которые были созданы после редактируемого
    deleted_result = await db.execute(
        delete(ChatMessage)
        .where(ChatMessage.chat_id == chat_message.chat_id)
        .where(ChatMessage.created_at > edit_message_time)
        .where(ChatMessage.external_user_id == external_user_id)  # Безопасность: только свои сообщения
    )
    
    # Логируем количество удаленных сообщений
    deleted_count = deleted_result.rowcount if hasattr(deleted_result, 'rowcount') else 0
    print(f"✏️ [EDIT] Удалено сообщений после редактируемого: {deleted_count}")
    
    # Обновляем текст сообщения пользователя
    chat_message.user_message = payload.new_text
    # Очищаем старый ответ AI
    chat_message.ai_response = ""
    
    # Сохраняем изменения
    await db.commit()
    await db.refresh(chat_message)
    
    # Получаем фичи студента
    features = await collect_student_features(access_token)
    ml_results = predict_topic_needs(features)
    student_context = build_student_context(features, ml_results)
    
    # Строим контекст из истории чата
    history_context = ""
    if history_messages:
        history_parts = []
        for hist_msg in history_messages:
            if hist_msg.user_message:
                history_parts.append(f"Пользователь: {hist_msg.user_message}")
            if hist_msg.ai_response:
                history_parts.append(f"Ассистент: {hist_msg.ai_response}")
        history_context = "\n".join(history_parts)
    
    # Формируем промпт с учетом истории
    if history_context:
        prompt = f"""
Информация о студенте:
{student_context}

Предыдущая переписка:
{history_context}

Вопрос студента (отредактированный):
"{payload.new_text}"

Напиши один совет (30-50 слов) для этого студента на русском языке.
Совет должен быть конкретным и мотивирующим.
Если данных по другим предметам нет, опирайся только на то, что известно.
"""
    else:
        prompt = f"""
Информация о студенте:
{student_context}

Вопрос студента:
"{payload.new_text}"

Напиши один совет (30-50 слов) для этого студента на русском языке.
Совет должен быть конкретным и мотивирующим.
Если данных по другим предметам нет, опирайся только на то, что известно (например, {student_context}).
"""
    
    # Логируем запрос
    print("\n" + "="*50)
    print("✏️ [EDIT] CONTEXT & PROMPT:")
    print(f"Context: {student_context}")
    if history_context:
        print(f"History: {history_context[:200]}...")
    print("-" * 20)
    print(f"Edited Msg: {payload.new_text}")
    print("="*50 + "\n")
    
    # Собираем полный ответ для сохранения в БД
    full_response = ""
    message_id_to_update = chat_message.id  # Сохраняем UUID напрямую
    
    async def stream_generator():
        nonlocal full_response, message_id_to_update
        try:
            async for chunk in hf_client.ask_stream(prompt):
                full_response += chunk
                # Отправляем Markdown напрямую без оборачивания в data:
                yield chunk
            
            # Обновляем ответ AI в БД после завершения стриминга
            print(f"🔍 [EDIT] Стриминг завершен, full_response длина: {len(full_response)}")
            
            if full_response and full_response.strip():
                try:
                    # Перезагружаем сообщение из БД, чтобы убедиться, что оно привязано к сессии
                    print(f"🔍 [EDIT] Ищем сообщение с ID: {message_id_to_update}")
                    msg_result = await db.execute(
                        select(ChatMessage)
                        .where(ChatMessage.id == message_id_to_update)
                    )
                    msg_to_update = msg_result.scalar_one_or_none()
                    
                    if msg_to_update:
                        print(f"✅ [EDIT] Сообщение найдено, обновляем ai_response")
                        msg_to_update.ai_response = full_response.strip()
                        await db.flush()  # Сначала flush для проверки
                        await db.commit()  # Затем commit для сохранения
                        await db.refresh(msg_to_update)  # Обновляем объект из БД
                        print(f"✅ [EDIT] Ответ AI сохранен в БД: {len(full_response)} символов")
                        print(f"✅ [EDIT] Проверка: ai_response = '{msg_to_update.ai_response[:50]}...'")
                    else:
                        print(f"❌ [EDIT] Сообщение {message_id_to_update} не найдено для обновления")
                except Exception as e:
                    print(f"❌ [EDIT] Error updating chat message in DB: {e}")
                    import traceback
                    traceback.print_exc()
                    try:
                        await db.rollback()
                    except:
                        pass
            else:
                print(f"⚠️ [EDIT] Пустой ответ от AI (длина: {len(full_response)}), не сохраняем в БД")
        except Exception as e:
            print(f"❌ [EDIT] Error in stream generator: {e}")
            import traceback
            traceback.print_exc()
            yield f"Произошла ошибка при получении ответа.\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/markdown; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@router.options("/messages/{message_id}")
async def options_edit_message(message_id: str):
    return Response(status_code=200)