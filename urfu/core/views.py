from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Teacher, Student, Group, Subject
from .serializers import TeacherSerializer, StudentSerializer, GroupSerializer, SubjectSerializer


class TeacherViewSet(ReadOnlyModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.select_related("subject")
    serializer_class = GroupSerializer


class StudentViewSet(ReadOnlyModelViewSet):
    queryset = Student.objects.prefetch_related("groups")
    serializer_class = StudentSerializer


class SubjectViewSet(ReadOnlyModelViewSet):
    queryset = Subject.objects.select_related("teacher")
    serializer_class = SubjectSerializer
