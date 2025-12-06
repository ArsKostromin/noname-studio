import uuid
from django.db import models
from core.models import Subject, Group, Teacher

class Schedule(models.Model):
    # Уникальный идентификатор записи
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Предмет пары
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name="schedule"
    )

    # Группа студентов
    group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        related_name="schedule"
    )

    # Преподаватель, ведущий пару
    teacher = models.ForeignKey(
        Teacher, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="classes"
    )

    # День недели (1=понедельник … 7=воскресенье)
    weekday = models.IntegerField()

    # Время начала занятия
    starts_at = models.TimeField()

    # Время окончания занятия
    ends_at = models.TimeField()

    # Длительность занятия в минутах (опционально)
    duration_minutes = models.IntegerField(null=True, blank=True)

    # Аудитория (номер, название)
    room = models.CharField(max_length=100, null=True, blank=True)

    # Тема занятия
    topic = models.CharField(max_length=255, null=True, blank=True, help_text="Тема занятия")

    # Темы, которые группа будет проходить на этой паре (для планирования/ML)
    group_related_topics = models.JSONField(null=True, blank=True, help_text="Темы группы на этой паре")

    # Максимальный балл за работу/контрольную на этой паре
    max_score = models.FloatField(default=0.0)

    # Тип работы — булевы флаги для классификации
    is_control_work = models.BooleanField(default=False)
    is_test = models.BooleanField(default=False)
    is_exam = models.BooleanField(default=False)
    is_lab_work = models.BooleanField(default=False)

    # Финальная работа или пересдача (если применимо)
    is_final = models.BooleanField(default=False)
    is_retake = models.BooleanField(default=False)

    # Ссылка на материалы (лекции, статьи, видео)
    materials_link = models.URLField(null=True, blank=True)

    # Дата проведения/сдачи работы (если отличается от расписания)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        # Уникальность пары по предмету, группе, дню недели и времени начала
        unique_together = ('subject', 'group', 'weekday', 'starts_at')

    def __str__(self):
        return f"{self.subject} / {self.group} / {self.weekday}"
