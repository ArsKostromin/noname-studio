from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Grade
from .serializers import GradeSerializer
from .presenters import GradesPresenter
from .schemas import my_grades_schema, grades_list_schema


class GradeViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с оценками.
    Предоставляет только чтение (ReadOnly).
    """
    queryset = Grade.objects.select_related("student", "subject", "teacher")
    serializer_class = GradeSerializer
    
    @grades_list_schema
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@my_grades_schema
def my_grades(request):
    """
    Эндпоинт для получения оценок текущего пользователя.
    Возвращает оценки сгруппированные по дисциплинам с средним баллом.
    """
    student = request.user
    result = GradesPresenter.get_student_grades_by_subject(student)
    return Response(result)
