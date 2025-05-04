from django.conf import settings
from django.db import models
from Admin.models import AuthUser, Faculty, Student
from django.core.mail import send_mail
import datetime
# Create your models here.

class Teacher_Messages(models.Model):
    admin = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    teacher = models.ManyToManyField(Faculty, related_name='teacher_messages')
    message = models.CharField(max_length=10000, blank=True, null=True)
    tag = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teacher_messages'

    def __str__(self):
        return self.message
    

class Student_Notice(models.Model):
    admin = models.ForeignKey(AuthUser, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_messages', null=True, blank=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    message = models.CharField(max_length=10000, blank=True, null=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'student_messages'

    def send_to_email(self):
        try:
            for student in Student.objects.all():
                send_mail(  
                    f"{self.title} - {settings.APP_NAME}",
                    self.message,
                    settings.DEFAULT_FROM_EMAIL,
                    [student.user.email],
                    fail_silently=False,
                )
            for teacher in Faculty.objects.all():
                send_mail( 
                    f"{self.title} - {settings.APP_NAME}",
                    self.message,
                    settings.DEFAULT_FROM_EMAIL,
                    [teacher.user.email],
                    fail_silently=False,
                )
        except:
            pass

    def __str__(self):
        return self.message
    
class Student_Marks(models.Model):
    teacher = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='teacher_marks', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_marks', null=True, blank=True)
    mst1 = models.IntegerField(blank=True, null=True)
    mst2 = models.IntegerField(blank=True, null=True)
    assignment = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'student_marks'

    def send_to_email(self):
        pass

    def get_att_marks(self):
        try:
            att = Attendance.objects.get(student=self.student)
            return att.calculate_student_marks(subject=self.teacher.subject)
        except:
            return 0

    def get_total_marks(self):
        mst1 = int(self.mst1) if self.mst1 else 0
        mst2 = int(self.mst2) if self.mst2 else 0
        assignment = int(self.assignment) if self.assignment else 0
        att = self.get_att_marks()
        total_marks = settings.TOTAL_MARKS if settings.TOTAL_MARKS else 1  # Handle division by zero
        proft =(mst1+mst2)/2
        proft1=proft+assignment+att  
        return proft1


    def __str__(self):
        return f"{self.student.user.get_full_name()} marks" # type: ignore
    
from collections import defaultdict

class Time_Table(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    )
    day = models.CharField(max_length=255, choices=DAY_CHOICES, blank=True, null=True)
    time_from = models.TimeField(blank=True, null=True)
    time_to = models.TimeField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'time_table'

    def __str__(self):
        return self.day

class Attendance(models.Model):
    teacher = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='teacher_attendance', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_attendance', null=True, blank=True)
    time = models.ForeignKey(Time_Table, on_delete=models.CASCADE, related_name='time_attendance', null=True, blank=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'

    def __str__(self):
        return self.student.user.get_full_name()

    def calculate_student_attendance_percentage(self, subject=None): 
        queryset = Attendance.objects.filter(student=self.student)
        if subject:
            queryset = queryset.filter(time__subject=subject)
        total_classes_attended = queryset.filter(status=True).count()
        total_classes = queryset.count()
        if total_classes == 0:
            return 0
        attendance_percentage = (total_classes_attended / total_classes) * 100
        return attendance_percentage

    def calculate_student_marks(self, subject=None):
        attendance_percentage = self.calculate_student_attendance_percentage(subject)
        if attendance_percentage >= 96:
            return 6
        elif 91 <= attendance_percentage <= 95:
            return 5
        elif 86 <= attendance_percentage <= 90:
            return 4
        elif 81 <= attendance_percentage <= 85:
            return 3
        elif 76 <= attendance_percentage <= 80:
            return 2
        elif attendance_percentage < 76:
            return 1
        else:
            return 0
