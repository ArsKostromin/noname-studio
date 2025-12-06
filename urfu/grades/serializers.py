from rest_framework import serializers
from .models import Grade
from core.serializers import SubjectSerializer, TeacherSerializer


class GradeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для оценки студента.
    
    Поля:
    - work_type: Тип работы (homework, test, exam, quiz, lab, project, other)
    - value: Оценка (число)
    - weight: Вес работы (контрольная = 1.0, домашка = 0.3, тест = 0.6)
    - topic: Тема работы
    - description: Описание работы
    - is_final: Финальная оценка
    - is_retake: Пересдача
    - work_date: Дата проведения работы
    """
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    
    class Meta:
        model = Grade
        fields = "__all__"
