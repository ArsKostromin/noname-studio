from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Teacher, Student, Group, Subject
from .serializers import TeacherSerializer, StudentSerializer, GroupSerializer, SubjectSerializer
from .schemas import (
    teachers_list_schema,
    subjects_list_schema,
    groups_list_schema,
    students_list_schema
)


class TeacherViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с преподавателями.
    Предоставляет только чтение (ReadOnly).
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    
    @teachers_list_schema
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class GroupViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с группами студентов.
    Предоставляет только чтение (ReadOnly).
    """
    queryset = Group.objects.select_related("subject")
    serializer_class = GroupSerializer
    
    @groups_list_schema
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class StudentViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы со студентами.
    Предоставляет только чтение (ReadOnly).
    """
    queryset = Student.objects.prefetch_related("groups")
    serializer_class = StudentSerializer
    
    @students_list_schema
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SubjectViewSet(ReadOnlyModelViewSet):
    """
    ViewSet для работы с предметами.
    Предоставляет только чтение (ReadOnly).
    """
    queryset = Subject.objects.select_related("teacher")
    serializer_class = SubjectSerializer
    
    @subjects_list_schema
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
