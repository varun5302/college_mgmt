# core/models.py
from django.db import models

class Department(models.Model):
    dept_id = models.AutoField(primary_key=True)
    dept_name = models.CharField(max_length=100)

    def __str__(self):
        return self.dept_name

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.course_name

class Register(models.Model):
    STUDENT = 1
    FACULTY = 2
    TYPE_CHOICES = ((STUDENT, 'Student'), (FACULTY, 'Faculty'))

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    reg_type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)  # renamed from `type`
    image = models.CharField(max_length=255, blank=True, null=True)
    guid = models.CharField(max_length=50, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    dept = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class LeaveType(models.Model):
    leave_id = models.AutoField(primary_key=True)
    leave_type = models.CharField(max_length=100)  # increased length to 100

    def __str__(self):
        return self.leave_type

class LeaveMaster(models.Model):
    PENDING, CLERK, HOD = 0, 1, 2
    STATUS_CHOICES = ((PENDING, 'Pending'), (CLERK, 'Clerk'), (HOD, 'HOD'))

    id = models.AutoField(primary_key=True)
    reg = models.ForeignKey(Register, on_delete=models.CASCADE)
    leave = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    leave_date = models.DateField()
    leave_reason = models.TextField()
    leave_image = models.CharField(max_length=255, blank=True, null=True)
    levmApprove = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"{self.reg} - {self.leave} ({self.leave_date})"
