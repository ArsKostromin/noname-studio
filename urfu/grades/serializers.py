from rest_framework import serializers
from .models import Grade
from core.serializers import SubjectSerializer, TeacherSerializer


class GradeSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    
    class Meta:
        model = Grade
        fields = "__all__"
