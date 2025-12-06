"""
Схемы Swagger для приложения core (аутентификация и справочники)
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import status


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
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string',
                    'description': 'Логин студента',
                    'example': 'student123'
                },
                'password': {
                    'type': 'string',
                    'description': 'Пароль студента',
                    'format': 'password',
                    'example': 'password123'
                }
            },
            'required': ['username', 'password']
        }
    },
    responses={
        200: {
            'description': 'Успешная аутентификация',
            'examples': {
                'application/json': {
                    'token': '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b',
                    'user_id': '550e8400-e29b-41d4-a716-446655440000',
                    'username': 'student123',
                    'full_name': 'Иванов Иван Иванович'
                }
            }
        },
        400: {
            'description': 'Не указаны обязательные поля',
            'examples': {
                'application/json': {
                    'error': 'Необходимо указать username и password'
                }
            }
        },
        401: {
            'description': 'Неверный логин или пароль',
            'examples': {
                'application/json': {
                    'error': 'Неверный логин или пароль'
                }
            }
        }
    },
    tags=['Аутентификация']
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
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'string',
                    'format': 'uuid',
                    'description': 'UUID студента',
                    'example': '550e8400-e29b-41d4-a716-446655440000'
                }
            },
            'required': ['id']
        }
    },
    responses={
        200: {
            'description': 'Токен успешно получен',
            'examples': {
                'application/json': {
                    'token': '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b',
                    'user_id': '550e8400-e29b-41d4-a716-446655440000',
                    'username': 'student123',
                    'full_name': 'Иванов Иван Иванович'
                }
            }
        },
        400: {
            'description': 'Не указан ID студента',
            'examples': {
                'application/json': {
                    'error': 'Необходимо указать id студента'
                }
            }
        },
        404: {
            'description': 'Студент не найден',
            'examples': {
                'application/json': {
                    'error': 'Студент с таким id не найден'
                }
            }
        }
    },
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
