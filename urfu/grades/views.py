from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Grade
from .serializers import GradeSerializer
from core.serializers import SubjectSerializer


class GradeViewSet(ReadOnlyModelViewSet):
    queryset = Grade.objects.select_related("student", "subject", "teacher")
    serializer_class = GradeSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_grades(request):
    """
    Эндпоинт для получения оценок текущего пользователя.
    Возвращает оценки сгруппированные по дисциплинам с средним баллом.
    """
    student = request.user
    
    # Получаем все оценки студента
    grades = Grade.objects.filter(student=student).select_related("subject", "teacher")
    
    # Группируем по предметам и считаем средний балл
    from collections import defaultdict
    
    grades_by_subject = defaultdict(list)
    for grade in grades:
        grades_by_subject[grade.subject].append(grade.value)
    
    result = []
    for subject, values in grades_by_subject.items():
        avg_score = sum(values) / len(values)
        subject_data = SubjectSerializer(subject).data
        result.append({
            'subject': subject_data,
            'grades': [GradeSerializer(grade).data for grade in grades.filter(subject=subject)],
            'average_score': round(avg_score, 2),
            'total_grades': len(values)
        })
    
    return Response(result)
