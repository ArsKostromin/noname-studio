"""
Эндпоинты авторизации с JWT access токенами и refresh токенами
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken
from .models import Student
from .refresh_token import (
    create_refresh_token,
    validate_refresh_token,
    invalidate_refresh_token,
    rotate_refresh_token
)
from .schemas import login_schema, refresh_schema, logout_schema


def get_client_ip(request):
    """Получает IP адрес клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Эндпоинт для входа по логину и паролю.
    Возвращает JWT access токен и refresh токен.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Необходимо указать username и password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Неверный логин или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Генерируем JWT access токен
    jwt_refresh = JWTRefreshToken.for_user(user)
    access_token = str(jwt_refresh.access_token)
    
    # Создаём refresh токен (opaque, хэшированный в БД)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip_address = get_client_ip(request)
    refresh_token = create_refresh_token(user, user_agent, ip_address)
    
    return Response({
        'access': access_token,
        'refresh': refresh_token,
        'user_id': str(user.id),
        'username': user.username,
        'full_name': user.full_name
    })


@refresh_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_view(request):
    """
    Эндпоинт для обновления access токена.
    Принимает refresh токен, возвращает новый access и новый refresh (ротация).
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response(
            {'error': 'Необходимо указать refresh токен'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Ротируем refresh токен (проверяет, инвалидирует старый, создаёт новый)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = get_client_ip(request)
        new_refresh_token, user = rotate_refresh_token(refresh_token, user_agent, ip_address)
        
        # Генерируем новый JWT access токен
        jwt_refresh = JWTRefreshToken.for_user(user)
        new_access_token = str(jwt_refresh.access_token)
        
        return Response({
            'access': new_access_token,
            'refresh': new_refresh_token
        })
        
    except Exception as e:
        return Response(
            {'error': 'Невалидный или истёкший refresh токен'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@logout_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Эндпоинт для выхода.
    Инвалидирует refresh токен.
    Access токен сам истечёт через короткое время.
    """
    refresh_token = request.data.get('refresh')
    
    if refresh_token:
        try:
            invalidate_refresh_token(refresh_token)
        except Exception:
            pass  # Токен уже невалиден или не существует
    
    return Response({
        'message': 'Успешный выход'
    }, status=status.HTTP_200_OK)
