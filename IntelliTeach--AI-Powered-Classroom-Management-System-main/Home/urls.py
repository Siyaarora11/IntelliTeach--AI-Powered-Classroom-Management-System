from django.urls import path
from .views import attendance_runner, home_login, studentDashboard, Images
from Admin.views import add_notice, delete_notice

urlpatterns = [
    path('', home_login, name='home'),
    path('', studentDashboard, name='student_dashboard'),
    path('add_notice/', add_notice, name='add_notice'),
    path('delete_notice/<int:id>', delete_notice, name='delete_notice'),
    path('run-attendance-system', attendance_runner, name='run_att'),
    path('stop-attendance-system', attendance_runner, {'stop': True}, name='stop_att')
]
