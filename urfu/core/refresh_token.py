"""
Утилиты для работы с refresh токенами
"""
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from .models import RefreshToken


def generate_refresh_token() -> str:
    """
    Генерирует случайный opaque refresh токен.
    
    Returns:
        str: Случайная строка длиной 64 символа
    """
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    """
    Хэширует токен для безопасного хранения.
    
    Args:
        token: Исходный токен
        
    Returns:
        str: Хэш токена
    """
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token(user, user_agent=None, ip_address=None) -> str:
    """
    Создаёт новый refresh токен для пользователя.
    
    Args:
        user: Объект Student
        user_agent: User-Agent заголовок (опционально)
        ip_address: IP адрес (опционально)
        
    Returns:
        str: Новый refresh токен (не хэшированный)
    """
    # Генерируем новый токен
    token = generate_refresh_token()
    token_hash = hash_token(token)
    
    # Создаём запись в БД
    RefreshToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=timezone.now() + timedelta(days=30),
        user_agent=user_agent,
        ip_address=ip_address
    )
    
    return token


def validate_refresh_token(token: str) -> RefreshToken:
    """
    Проверяет refresh токен и возвращает объект RefreshToken.
    
    Args:
        token: Refresh токен для проверки
        
    Returns:
        RefreshToken: Объект токена, если валиден
        
    Raises:
        RefreshToken.DoesNotExist: Если токен не найден или невалиден
    """
    token_hash = hash_token(token)
    
    try:
        refresh_token = RefreshToken.objects.get(
            token_hash=token_hash,
            used_at__isnull=True,
            expires_at__gt=timezone.now()
        )
        return refresh_token
    except RefreshToken.DoesNotExist:
        raise RefreshToken.DoesNotExist("Invalid or expired refresh token")


def invalidate_refresh_token(token: str) -> None:
    """
    Инвалидирует refresh токен (помечает как использованный).
    
    Args:
        token: Refresh токен для инвалидации
    """
    token_hash = hash_token(token)
    
    try:
        refresh_token = RefreshToken.objects.get(
            token_hash=token_hash,
            used_at__isnull=True
        )
        refresh_token.mark_as_used()
    except RefreshToken.DoesNotExist:
        pass  # Токен уже невалиден или не существует


def rotate_refresh_token(old_token: str, user_agent=None, ip_address=None) -> tuple:
    """
    Ротирует refresh токен: инвалидирует старый и создаёт новый.
    
    Args:
        old_token: Старый refresh токен
        user_agent: User-Agent заголовок (опционально)
        ip_address: IP адрес (опционально)
        
    Returns:
        tuple: (новый refresh токен, объект Student)
        
    Raises:
        RefreshToken.DoesNotExist: Если старый токен невалиден
    """
    # Проверяем и получаем старый токен
    old_refresh_token = validate_refresh_token(old_token)
    user = old_refresh_token.user
    
    # Сначала создаём новый токен
    new_token = create_refresh_token(user, user_agent, ip_address)
    
    # Потом инвалидируем старый
    old_refresh_token.mark_as_used()
    
    return new_token, user

