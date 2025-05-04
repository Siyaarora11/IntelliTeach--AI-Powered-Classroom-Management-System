from django.db import models
from django.core.mail import send_mail

from IgCMS import settings

# Create your models here.
class Student_Query(models.Model):
    student = models.ForeignKey('Admin.Student', on_delete=models.CASCADE, related_name='student_queries', null=True, blank=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=10000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attechments = models.FileField(upload_to='student_queries/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'student_queries'

    def send_succes_mail(self):
        try:
            send_mail(
                'Query Submitted',
                f'Your query has been submitted successfully, we will get back to you soon.',
                settings.DEFAULT_FROM_EMAIL,
                [self.student.user.email],
                fail_silently=False,
            )
        except:
            pass
        
    def __str__(self):
        return self.title
    
class Student_Queries_Answers(models.Model):
    student_query = models.ForeignKey(Student_Query, on_delete=models.CASCADE, related_name='student_query_answers', null=True, blank=True)
    teacher = models.ForeignKey('Admin.Faculty', on_delete=models.CASCADE, related_name='teacher_query_answers', null=True, blank=True)
    answer = models.CharField(max_length=10000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attechments = models.FileField(upload_to='student_query_answers/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'student_queries_answers'

    def send_succes_mail(self):
        try:
            send_mail(
                'Query Answered',
                f'Your query has been answered successfully, please check the answer. \n\n\n {self.answer} \n\n\n Regards, \n {self.teacher.user.get_full_name} \n',
                settings.DEFAULT_FROM_EMAIL,
                [self.student_query.student.user.email],
                fail_silently=False,
            )
        except:
            pass

    def __str__(self):
        return self.answer
    