from django.urls import path
from .views import delete_topic, facultyDashboard, faculty_Profile, assignment_list, single_assignment, update_assignment, important_topics, delete_topic, view_query, queries, delete_assignment_r
from Home.views import marks_list, teacher_messages, marks_mst1, marks_mst2, marks_assign

urlpatterns = [
    path('', facultyDashboard, name='teacher_dashboard'),
    path('assignments/', assignment_list, name='assignments'),
    path('assignment/<int:id>', single_assignment, name='assignment'),
    path('assignment/<int:id>/delete', delete_assignment_r, name='assignment-delete'),
    path('assignment/<int:assignment_id>/update', update_assignment, name='update-assignment'),
    path('topics', important_topics, name='topics'),
    path('topic/<int:id>/delete', delete_topic, name='delete-topic'),
    path('profile', faculty_Profile, name='teacher_profile' ),
    path('query/<int:id>', view_query, name='query' ),
    path('queries/', queries, name='query-repliy' ),
    path('queries/', queries, name='queries' ),
    path('marks/', marks_list, name='marks' ),
    path('marks-mst1/', marks_mst1, name='mst1' ),
    path('marks-mst2/', marks_mst2, name='mst2' ),
    path('marks-assmarks/', marks_assign, name='assmarks' ),
    path('messages/', teacher_messages, name='teacher_messages' ),
]
