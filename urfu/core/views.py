from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Teacher, Student, Group, Subject
from .serializers import TeacherSerializer, StudentSerializer, GroupSerializer, SubjectSerializer


class TeacherViewSet(ReadOnlyModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class StudentViewSet(ReadOnlyModelViewSet):
    queryset = Student.objects.select_related("group")
    serializer_class = StudentSerializer


class SubjectViewSet(ReadOnlyModelViewSet):
    queryset = Subject.objects.select_related("teacher")
    serializer_class = SubjectSerializer
