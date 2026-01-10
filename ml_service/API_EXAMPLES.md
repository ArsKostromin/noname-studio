# Примеры запросов к API

Все эндпоинты требуют заголовок `Authorization: Bearer <token>` с JWT токеном.

## 1. POST /api/ai/chats - Создать новый чат

**Запрос:**
```http
POST /api/ai/chats
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Вопросы по математике"
}
```

**Ответ:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Вопросы по математике",
  "created_at": "2024-01-15T10:30:00.000000+00:00"
}
```

---

## 2. GET /api/ai/chats - Получить список всех чатов

**Запрос:**
```http
GET /api/ai/chats
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**
```json
{
  "chats": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Вопросы по математике",
      "created_at": "2024-01-15T10:30:00.000000+00:00"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Подготовка к экзамену",
      "created_at": "2024-01-14T15:20:00.000000+00:00"
    }
  ]
}
```

---

## 3. POST /api/ai/message - Отправить сообщение в чат

**Запрос:**
```http
POST /api/ai/message
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "Как лучше подготовиться к экзамену?",
  "chat_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Ответ:**
```json
{
  "message": "Для успешной подготовки к экзамену рекомендую составить план изучения материала, разбив его на небольшие блоки. Начните с повторения самых сложных тем, которые вызывают у вас затруднения. Регулярно решайте практические задачи и проверяйте свои знания. Не забывайте делать перерывы для отдыха - это поможет лучше усвоить информацию."
}
```

---

## 4. GET /api/ai/history - Получить историю чата

**Запрос:**
```http
GET /api/ai/history?chat_id=550e8400-e29b-41d4-a716-446655440000&limit=50
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Параметры запроса:**
- `chat_id` (обязательный) - UUID чата
- `limit` (опциональный, по умолчанию 50) - максимальное количество сообщений (от 1 до 100)

**Ответ:**
```json
{
  "messages": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "user_message": "Как лучше подготовиться к экзамену?",
      "ai_response": "Для успешной подготовки к экзамену рекомендую составить план изучения материала...",
      "created_at": "2024-01-15T10:35:00.000000+00:00"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "user_message": "Спасибо за совет!",
      "ai_response": "Пожалуйста! Если возникнут еще вопросы, обращайтесь.",
      "created_at": "2024-01-15T10:40:00.000000+00:00"
    }
  ]
}
```

---

## 5. DELETE /api/ai/chats/{chat_id} - Удалить чат

**Запрос:**
```http
DELETE /api/ai/chats/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**
```json
{
  "message": "Чат успешно удален",
  "deleted_chat_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Примеры с использованием curl

### Создать чат
```bash
curl -X POST "http://localhost:8001/api/ai/chats" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Вопросы по математике"
  }'
```

### Получить список чатов
```bash
curl -X GET "http://localhost:8001/api/ai/chats" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Отправить сообщение
```bash
curl -X POST "http://localhost:8001/api/ai/message" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Как лучше подготовиться к экзамену?",
    "chat_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### Получить историю чата
```bash
curl -X GET "http://localhost:8001/api/ai/history?chat_id=550e8400-e29b-41d4-a716-446655440000&limit=50" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Удалить чат
```bash
curl -X DELETE "http://localhost:8001/api/ai/chats/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Примеры с использованием Python (requests)

```python
import requests

BASE_URL = "http://localhost:8001/api/ai"
TOKEN = "YOUR_JWT_TOKEN"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Создать чат
response = requests.post(
    f"{BASE_URL}/chats",
    headers=HEADERS,
    json={"title": "Вопросы по математике"}
)
chat_data = response.json()
chat_id = chat_data["id"]
print(f"Создан чат: {chat_id}")

# 2. Получить список чатов
response = requests.get(f"{BASE_URL}/chats", headers=HEADERS)
chats = response.json()
print(f"Всего чатов: {len(chats['chats'])}")

# 3. Отправить сообщение
response = requests.post(
    f"{BASE_URL}/message",
    headers=HEADERS,
    json={
        "message": "Как лучше подготовиться к экзамену?",
        "chat_id": chat_id
    }
)
ai_response = response.json()
print(f"Ответ AI: {ai_response['message']}")

# 4. Получить историю чата
response = requests.get(
    f"{BASE_URL}/history",
    headers=HEADERS,
    params={"chat_id": chat_id, "limit": 50}
)
history = response.json()
print(f"Сообщений в истории: {len(history['messages'])}")

# 5. Удалить чат
response = requests.delete(
    f"{BASE_URL}/chats/{chat_id}",
    headers=HEADERS
)
delete_result = response.json()
print(f"Результат удаления: {delete_result['message']}")
```
```
