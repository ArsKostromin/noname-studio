#urfu\core\models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class StudentManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.full_name


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, related_name="subjects")

    def __str__(self):
        return self.title


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    # Каждая группа связана с одним предметом (одна группа = один предмет)
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name="groups",
        help_text="Предмет, для которого создана эта группа"
    )

    def __str__(self):
        return f"{self.name} ({self.subject})"


class Student(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    # Студент может быть в нескольких группах (одна группа = один предмет)
    groups = models.ManyToManyField(Group, related_name="students", blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = StudentManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class RefreshToken(models.Model):
    """
    Модель для хранения refresh токенов.
    Токены хранятся в хэшированном виде для безопасности.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="refresh_tokens"
    )
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'refresh_tokens'
        indexes = [
            models.Index(fields=['token_hash']),
            models.Index(fields=['user', 'used_at']),
        ]
    
    def mark_as_used(self):
        """Помечает токен как использованный"""
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])
    
    def is_valid(self):
        """Проверяет, валиден ли токен"""
        return (
            self.used_at is None and
            self.expires_at > timezone.now()
        )
    
    def __str__(self):
        return f"RefreshToken for {self.user.username} (expires: {self.expires_at})"
