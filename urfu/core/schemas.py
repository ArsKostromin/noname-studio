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
    token = serializers.CharField(
        help_text="Токен для аутентификации"
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
    Возвращает токен для дальнейшей работы с API.
    
    **Пример использования:**
    1. Отправьте POST запрос с логином и паролем
    2. Получите токен в ответе
    3. Используйте токен в заголовке Authorization: Token <ваш_токен>
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
                'token': '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b',
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

class AcceptTokenRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса получения токена по ID"""
    id = serializers.UUIDField(
        help_text="UUID студента"
    )


accept_token_schema = extend_schema(
    summary="Получение токена по ID студента",
    description="""
    Эндпоинт для получения токена аутентификации по ID студента.
    Полезно для тестирования или восстановления доступа.
    
    **Пример использования:**
    1. Отправьте POST запрос с ID студента
    2. Получите токен в ответе
    3. Используйте токен в заголовке Authorization: Token <ваш_токен>
    """,
    methods=['POST'],
    request=AcceptTokenRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                'id': '550e8400-e29b-41d4-a716-446655440000'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Успешное получение токена',
            value={
                'token': '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b',
                'user_id': '550e8400-e29b-41d4-a716-446655440000',
                'username': 'student123',
                'full_name': 'Иванов Иван Иванович'
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Ошибка валидации',
            value={'error': 'Необходимо указать id студента'},
            response_only=True,
            status_codes=['400']
        ),
        OpenApiExample(
            'Студент не найден',
            value={'error': 'Студент с таким id не найден'},
            response_only=True,
            status_codes=['404']
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
