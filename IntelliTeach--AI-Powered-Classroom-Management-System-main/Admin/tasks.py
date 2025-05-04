from celery import shared_task
from Admin.utils import set_attendance
from Home.models import Attendance
from .models import Student
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def get_Attendance():
    now = datetime.now()
    current_day = now.strftime("%A").lower()

    if (current_day == 'saturday' or current_day == 'sunday'):
        if should_process_attendance() and settings.TIME_TABLE_WEEKEND_CLASSES:
            process_attendance()
        else:
            pass
    else:
        if should_process_attendance():
            process_attendance()
        else:
            pass
        
def should_process_attendance():
    return True

def process_attendance():
    set_attendance(time=300)

@shared_task
def send_attendance_email():
    students = Student.objects.all()
    for student in students:
        att = Attendance.objects.filter(student=student)
        if att:
            att = att.last()
            att_p = att.calculate_student_attendance_percentage()
            if att_p < 75:
                subject = f'Attendance Alert from {settings.APP_NAME}'
                message = f'Hello {student.user.get_full_name()},\n\nYour attendance is below 75%. Please make sure to attend the classes regularly.\n\n\n\nThis is an auto-generated email by the system and does not support incoming mails. If you have any queries, please reach out to us through your dashboard.'
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student.user.email])
            else:
                pass