"""
Схемы Swagger для приложения core (аутентификация и справочники)
"""
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    inline_serializer
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers, status
from rest_framework.response import Response


# Сериализаторы для схем запросов/ответов
class LoginRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса входа"""
    username = serializers.CharField(
        help_text="Логин студента"
    )
    password = serializers.CharField(
        help_text="Пароль студента",
        style={'input_type': 'password'},
        write_only=True
    )


class LoginResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа входа"""
    access = serializers.CharField(
        help_text="JWT access токен (TTL: 15 минут). Используйте в заголовке: Authorization: Bearer <access>"
    )
    refresh = serializers.CharField(
        help_text="Refresh токен (TTL: 30 дней). Используйте для обновления access токена"
    )
    user_id = serializers.UUIDField(
        help_text="UUID студента"
    )
    username = serializers.CharField(
        help_text="Логин студента"
    )
    full_name = serializers.CharField(
        help_text="Полное имя студента"
    )


class RefreshRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса обновления токена"""
    refresh = serializers.CharField(
        help_text="Refresh токен для обновления"
    )


class RefreshResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа обновления токена"""
    access = serializers.CharField(
        help_text="Новый JWT access токен"
    )
    refresh = serializers.CharField(
        help_text="Новый refresh токен (старый токен инвалидирован - ротация)"
    )


class LogoutRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса выхода"""
    refresh = serializers.CharField(
        help_text="Refresh токен для инвалидации",
        required=False
    )


class LogoutResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа выхода"""
    message = serializers.CharField(
        help_text="Сообщение об успешном выходе"
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Сериализатор для ошибок"""
    error = serializers.CharField(
        help_text="Описание ошибки"
    )


# Схемы для аутентификации
login_schema = extend_schema(
    summary="Вход по логину и паролю",
    description="""
    Эндпоинт для аутентификации пользователя по логину и паролю.
    Возвращает JWT access токен и refresh токен.
    
    **Архитектура токенов:**
    - **Access токен**: JWT, TTL 15 минут, используется в заголовке `Authorization: Bearer <access>`
    - **Refresh токен**: Opaque string, TTL 30 дней, хранится хэшированным в БД
    
    **Пример использования:**
    1. Отправьте POST запрос с логином и паролем
    2. Получите access и refresh токены в ответе
    3. Используйте access токен в заголовке: `Authorization: Bearer <access>`
    4. При истечении access токена используйте refresh для получения нового access
    """,
    methods=['POST'],
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                'username': 'student123',
                'password': 'password123'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Успешный вход',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'xK9pL2mN4qR6sT8uV0wX2yZ4aB6cD8eF0gH2iJ4kL6mN8oP0qR2sT4uV6wX8yZ0',
                'user_id': '550e8400-e29b-41d4-a716-446655440000',
                'username': 'student123',
                'full_name': 'Иванов Иван Иванович'
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Ошибка валидации',
            value={'error': 'Необходимо указать username и password'},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            'Неверные учетные данные',
            value={'error': 'Неверный логин или пароль'},
            response_only=True,
            status_codes=['401']
        ),
    ],
    tags=['Аутентификация']
)

refresh_schema = extend_schema(
    summary="Обновление access токена",
    description="""
    Эндпоинт для обновления access токена с помощью refresh токена.
    
    **Ротация refresh токенов:**
    - При каждом обновлении старый refresh токен инвалидируется
    - Выдаётся новый refresh токен
    - Один refresh токен может быть использован только один раз
    
    **Процесс:**
    1. Отправьте POST запрос с refresh токеном
    2. Получите новый access и новый refresh токены
    3. Старый refresh токен становится невалидным
    """,
    methods=['POST'],
    request=RefreshRequestSerializer,
    responses={
        200: RefreshResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                'refresh': 'xK9pL2mN4qR6sT8uV0wX2yZ4aB6cD8eF0gH2iJ4kL6mN8oP0qR2sT4uV6wX8yZ0'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Успешное обновление',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'yL0qM3nO5rS7tU9vW1xY3zA5bC7dE9fG1hJ3kL5mN7oP9qR3sT5uV7wX9yZ1'
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Ошибка валидации',
            value={'error': 'Необходимо указать refresh токен'},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            'Невалидный refresh токен',
            value={'error': 'Невалидный или истёкший refresh токен'},
            response_only=True,
            status_codes=['401']
        ),
    ],
    tags=['Аутентификация']
)

logout_schema = extend_schema(
    summary="Выход из системы",
    description="""
    Эндпоинт для выхода из системы.
    
    **Процесс:**
    - Инвалидирует refresh токен (помечает как использованный)
    - Access токен сам истечёт через короткое время (15 минут)
    - После выхода refresh токен нельзя использовать для обновления
    
    **Примечание:** Refresh токен опционален, но рекомендуется его передавать
    для полной инвалидации сессии.
    """,
    methods=['POST'],
    request=LogoutRequestSerializer,
    responses={
        200: LogoutResponseSerializer,
        401: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                'refresh': 'xK9pL2mN4qR6sT8uV0wX2yZ4aB6cD8eF0gH2iJ4kL6mN8oP0qR2sT4uV6wX8yZ0'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Успешный выход',
            value={
                'message': 'Успешный выход'
            },
            response_only=True,
            status_codes=['200']
        ),
    ],
    tags=['Аутентификация']
)

# Схемы для справочников
teachers_list_schema = extend_schema(
    summary="Список преподавателей",
    description="Получить список всех преподавателей",
    tags=['Справочники']
)

subjects_list_schema = extend_schema(
    summary="Список предметов",
    description="Получить список всех предметов",
    tags=['Справочники']
)

groups_list_schema = extend_schema(
    summary="Список групп",
    description="Получить список всех групп студентов",
    tags=['Справочники']
)

students_list_schema = extend_schema(
    summary="Список студентов",
    description="Получить список всех студентов",
    tags=['Справочники']
)
