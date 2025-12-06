from rest_framework import serializers
from .models import Schedule
from core.serializers import SubjectSerializer, TeacherSerializer, GroupSerializer


class ScheduleSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Schedule
        fields = "__all__"
