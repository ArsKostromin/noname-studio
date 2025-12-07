#urfu\core\auth.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Student
from .schemas import login_schema, accept_token_schema


@login_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Эндпоинт для входа по логину и паролю.
    Возвращает токен для аутентификации.
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

    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': str(user.id),
        'username': user.username,
        'full_name': user.full_name
    })


@accept_token_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def accept_token(request):
    """
    Эндпоинт для принятия токена по ID студента.
    Принимает id студента и возвращает токен.
    """
    student_id = request.data.get('id')
    
    if not student_id:
        return Response(
            {'error': 'Необходимо указать id студента'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response(
            {'error': 'Студент с таким id не найден'},
            status=status.HTTP_404_NOT_FOUND
        )

    token, created = Token.objects.get_or_create(user=student)
    
    return Response({
        'token': token.key,
        'user_id': str(student.id),
        'username': student.username,
        'full_name': student.full_name
    })

