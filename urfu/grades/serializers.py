from rest_framework import serializers
from .models import Grade, TestResult
from core.serializers import SubjectSerializer


class GradeSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    
    class Meta:
        model = Grade
        fields = "__all__"


class TestResultSerializer(serializers.ModelSerializer):
    correct_rate = serializers.FloatField(read_only=True)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = TestResult
        fields = "__all__"
