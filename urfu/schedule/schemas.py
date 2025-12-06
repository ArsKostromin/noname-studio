"""
Схемы Swagger для приложения schedule (расписание)
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


my_schedule_schema = extend_schema(
    summary="Получить расписание текущего пользователя",
    description="""
    Эндпоинт для получения расписания занятий текущего аутентифицированного студента.
    
    Возвращает полное расписание студента со всеми группами, в которых он состоит.
    Каждая группа соответствует одному предмету.
    
    **Особенности:**
    - Расписание включает все группы студента (студент может быть в нескольких группах)
    - Для каждого занятия указывается:
      - Предмет, группа, преподаватель
      - День недели и время
      - Аудитория
      - Тема занятия
      - Тип работы (контрольная, тест, экзамен, лабораторная)
      - Ссылки на материалы
      - Даты сдачи работ
    
    **Требует аутентификации:** Да (токен в заголовке Authorization)
    """,
    responses={
        200: {
            'description': 'Список занятий в расписании студента',
            'examples': {
                'application/json': [
                    {
                        'id': '550e8400-e29b-41d4-a716-446655440000',
                        'subject': {
                            'id': '660e8400-e29b-41d4-a716-446655440001',
                            'title': 'Математический анализ',
                            'teacher': {
                                'id': '770e8400-e29b-41d4-a716-446655440002',
                                'full_name': 'Петров Петр Петрович'
                            }
                        },
                        'group': {
                            'id': '880e8400-e29b-41d4-a716-446655440003',
                            'name': 'МАТ-21-01',
                            'subject': {
                                'id': '660e8400-e29b-41d4-a716-446655440001',
                                'title': 'Математический анализ'
                            }
                        },
                        'weekday': 1,
                        'starts_at': '09:00:00',
                        'ends_at': '10:30:00',
                        'room': 'Аудитория 101',
                        'topic': 'Пределы функций',
                        'is_control_work': False,
                        'is_test': True,
                        'is_exam': False,
                        'is_lab_work': False
                    }
                ]
            }
        },
        401: {
            'description': 'Требуется аутентификация',
            'examples': {
                'application/json': {
                    'detail': 'Учетные данные не были предоставлены.'
                }
            }
        }
    },
    tags=['Расписание']
)

schedule_list_schema = extend_schema(
    summary="Список всех расписаний",
    description="""
    Получить список всех расписаний с возможностью фильтрации.
    
    **Параметры запроса:**
    - `group` - UUID группы для фильтрации
    - `weekday` - День недели (1-7, где 1=понедельник, 7=воскресенье)
    """,
    parameters=[
        OpenApiParameter(
            name='group',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description='UUID группы для фильтрации расписания',
            required=False
        ),
        OpenApiParameter(
            name='weekday',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='День недели (1-7)',
            required=False
        ),
    ],
    tags=['Расписание']
)

