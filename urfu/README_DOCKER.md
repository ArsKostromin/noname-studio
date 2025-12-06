# Инструкция по запуску проекта в Docker

## Требования
- Docker
- Docker Compose

## Запуск проекта

1. **Соберите и запустите контейнеры:**
   ```bash
   docker-compose up --build
   ```

2. **Приложение будет доступно по адресу:**
   - http://localhost:8000

3. **Для запуска в фоновом режиме:**
   ```bash
   docker-compose up -d --build
   ```

4. **Остановка контейнеров:**
   ```bash
   docker-compose down
   ```

5. **Остановка с удалением volumes (удалит данные БД):**
   ```bash
   docker-compose down -v
   ```

## Выполнение команд Django

Для выполнения команд Django внутри контейнера:

```bash
# Создание миграций
docker-compose exec web python manage.py makemigrations

# Применение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Сборка статических файлов
docker-compose exec web python manage.py collectstatic
```

## Структура

- `Dockerfile` - конфигурация Docker образа для Django приложения
- `docker-compose.yml` - конфигурация для запуска всего стека (Django + PostgreSQL)
- `requirements.txt` - зависимости Python проекта
- `.dockerignore` - файлы, которые не нужно копировать в Docker образ

## База данных

Проект использует PostgreSQL в Docker. Данные сохраняются в volume `postgres_data`.

Параметры подключения к БД:
- Host: `db` (внутри Docker) или `localhost` (снаружи)
- Database: `urfu_db`
- User: `urfu_user`
- Password: `urfu_password`
- Port: `5432`

## API эндпоинты

После запуска доступны следующие эндпоинты:

- `POST /api/core/login/` - вход по логину и паролю
- `POST /api/core/accept-token/` - получение токена по ID студента
- `GET /api/schedule/my-schedule/` - расписание пользователя (требует токен)
- `GET /api/grades/my-grades/` - оценки пользователя (требует токен)

