"""
URL configuration for IgCMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Admin.views import admin_dashboard, update_password, logout, time_table, update_time_table, attendance_view, one_attendance_view, attendance_view_faculty
from teachers.views import teachers_list, delete_teacher, update_teacher

urlpatterns = [
    # path('admin/', admin.site.urls), # This is the default admin url, we are using custom admin url
    path('', include('Home.urls')),
    path('dashboard/', include('teachers.urls')),
    path('', include('student.urls')),
    path('admin/', admin_dashboard, name='admin_dashboard' ),
    path('admin/update_time_table/', update_time_table, name='update_time_table' ),
    path('time-table/', time_table, name='time_table' ),
    path('admin/attendance/', attendance_view, name='attendance' ),
    path('dashboard/attendance/', attendance_view_faculty, name='attendance_faculty' ),
    path('attendance/<str:id>/', one_attendance_view, name='attendance_one' ),
    path('teachers/', teachers_list, name='teachers_list'),
    path('delete_teacher/', delete_teacher, name='delete-teacher'),
    path('update_teacher/', update_teacher, name='update-teacher'),
    path('update_password/', update_password, name='update-password'),
    path('logout/', logout, name='logout'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)