#urfu\grades\models.py
import uuid
from django.db import models
from core.models import Student, Subject, Teacher


class Grade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Студент
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    # Предмет
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    # Преподаватель (кто поставил)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grades"
    )

    # Тип работы
    WORK_TYPE_CHOICES = [
        ("homework", "Домашняя работа"),
        ("test", "Тест"),
        ("exam", "Контрольная"),
        ("quiz", "Мини-тест"),
        ("lab", "Лабораторная"),
        ("project", "Проект"),
        ("other", "Другое"),
    ]
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES)

    # Тема работы
    topic = models.CharField(max_length=255)

    # Контекст/описание работы — для ML очень полезно
    description = models.TextField(blank=True, null=True)

    # Оценка
    value = models.IntegerField()

    # Вес работы (контрольная = 1.0, домашка = 0.3, тест = 0.6)
    weight = models.FloatField(default=1.0)

    # Это финальная оценка или пересдача
    is_final = models.BooleanField(default=False)
    is_retake = models.BooleanField(default=False)

    # Дата проведения / дата выставления оценки
    work_date = models.DateField(null=True, blank=True)

    # Когда запись добавили
    created_at = models.DateTimeField(auto_now_add=True)
    # Когда обновили (если преподаватель поменял оценку)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.student} | {self.subject} | "
            f"{self.work_type} | {self.topic} => {self.value}"
        )
