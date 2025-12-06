from rest_framework import serializers
from .models import Schedule
from core.serializers import SubjectSerializer, TeacherSerializer, GroupSerializer


class ScheduleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для расписания занятий.
    
    Поля:
    - weekday: День недели (1=понедельник, 7=воскресенье)
    - starts_at: Время начала занятия
    - ends_at: Время окончания занятия
    - room: Аудитория
    - topic: Тема занятия
    - group_related_topics: Темы группы на этой паре (JSON)
    - max_score: Максимальный балл за работу
    - is_control_work: Контрольная работа
    - is_test: Тест
    - is_exam: Экзамен
    - is_lab_work: Лабораторная работа
    - is_final: Финальная работа
    - is_retake: Пересдача
    - materials_link: Ссылка на материалы
    - due_date: Дата сдачи работы
    """
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Schedule
        fields = "__all__"
