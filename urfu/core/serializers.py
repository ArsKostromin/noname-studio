from rest_framework import serializers
from .models import Teacher, Student, Group, Subject


class TeacherSerializer(serializers.ModelSerializer):
    """
    Сериализатор для преподавателя.
    
    Поля:
    - full_name: Полное имя преподавателя
    - email: Email преподавателя
    - department: Кафедра
    """
    class Meta:
        model = Teacher
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    """
    Сериализатор для предмета.
    
    Поля:
    - title: Название предмета
    - teacher: Преподаватель предмета
    """
    teacher = TeacherSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    """
    Сериализатор для группы студентов.
    
    Поля:
    - name: Название группы
    - subject: Предмет, для которого создана группа
    """
    subject = SubjectSerializer(read_only=True)
    
    class Meta:
        model = Group
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для студента.
    
    Поля:
    - username: Логин студента
    - full_name: Полное имя
    - email: Email
    - groups: Список групп, в которых состоит студент
    """
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = "__all__"
