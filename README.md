# URFU Project

Проект состоит из двух сервисов:
- **Django API** (urfu/) - основной API для работы с расписанием и оценками
- **ML Service** (ml_service/) - FastAPI сервис для ML функционала

## Структура проекта

```
noname studio/
├── urfu/              # Django сервис
│   ├── core/         # Основные модели и аутентификация
│   ├── grades/       # Оценки
│   ├── schedule/     # Расписание
│   └── Dockerfile
├── ml_service/       # FastAPI ML сервис
│   ├── api/         # API роуты
│   ├── config.py    # Конфигурация
│   ├── main.py      # Точка входа
│   └── Dockerfile
├── docker-compose.yml  # Общая конфигурация Docker
└── README.md
```

## Запуск проекта

### Все сервисы одновременно:

```bash
docker compose up --build
```

### Отдельные сервисы:

```bash
# Только Django
docker compose up django

# Только ML сервис
docker compose up ml_service

# Только база данных
docker compose up db
```

## Эндпоинты

### Django API (порт 8000):
- `http://localhost:8000/api/docs/` - Swagger UI
- `http://localhost:8000/api/core/auth/login/` - Вход
- `http://localhost:8000/api/core/auth/refresh/` - Обновление токенов
- `http://localhost:8000/api/schedule/my-schedule/` - Расписание
- `http://localhost:8000/api/grades/my-grades/` - Оценки

### ML Service (порт 8001):
- `http://localhost:8001/` - Health check
- `http://localhost:8001/docs` - Swagger UI (автоматическая документация FastAPI)
- `http://localhost:8001/api/v1/ml/predict` - Предсказание (Logistic Regression)
- `http://localhost:8001/api/v1/ml/cluster` - Кластеризация (K-Means)
- `http://localhost:8001/api/v1/ml/models` - Список моделей

## База данных

Оба сервиса используют общую PostgreSQL базу данных:
- Host: `db` (внутри Docker) или `localhost` (снаружи)
- Database: `urfu_db`
- User: `urfu_user`
- Password: `urfu_password`
- Port: `5432`

## Авторизация

Проект использует JWT токены:
- **Access токен**: JWT, TTL 15 минут
- **Refresh токен**: Opaque string, TTL 30 дней, хэшированный в БД

Использование:
```bash
Authorization: Bearer <access_token>
```

