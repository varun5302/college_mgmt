# core/serializers.py
from rest_framework import serializers
from .models import Department, Course, Register, LeaveType, LeaveMaster

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = '__all__'

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class LeaveMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveMaster
        fields = '__all__'
