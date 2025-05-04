from django.urls import path
from student.views import student, update_student, delete_student, student_info, student_assignments, student_assignments_view, student_topics, student_enquiry
from teachers.views import queries, view_query

urlpatterns = [
    path('students/', student, name='student'),
    path('student/<str:id>/', student_info, name='student-info'),
    path('students/update-student/', update_student, name='update-student'),
    path('students/delete-student/', delete_student, name='delete-student'),
    path('assignments/', student_assignments, name='assignments-student'),
    path('topics/', student_topics, name='topics-student'),
    path('assignments/<int:id>', student_assignments_view, name='assignments-student-view'),
    path('enquiry/', student_enquiry, name='student-enquiry'),
    path('enquiries/', queries, name='student-enquiries'),
    path('enquiry/<int:id>', view_query, name='student-enquiry-single' ),
]