from django.urls import path
from . import views

urlpatterns = [
    # Timetable URLs
    path('timetable/create/', views.create_timetable, name='create_timetable'),
    path('timetable/edit/<int:timeslot_id>/', views.edit_timetable, name='edit_timetable'),
    path('timetable/delete/<int:timeslot_id>/', views.delete_timetable, name='delete_timetable'),
    path('', views.home, name='home'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/tutor/', views.register_tutor, name='register_tutor'),
    
    # Assessment URLs
    path('assessment/create/', views.create_assessment, name='create_assessment'),
    path('assessment/edit/<int:assessment_id>/', views.edit_assessment, name='edit_assessment'),
    path('assessment/delete/<int:assessment_id>/', views.delete_assessment, name='delete_assessment'),
    path('assessments/', views.view_assessments, name='view_assessments'),
    
    # Marks URLs
    path('marks/manage/', views.manage_marks, name='manage_marks'),
    path('marks/view/', views.student_marks, name='view_marks'),
    path('marks/view/<int:assessment_id>/', views.view_marks, name='view_marks_assessment'),
    path('marks/add/<int:assessment_id>/', views.add_marks, name='add_marks'),
    
    # Timetable URLs
    path('timetable/all/', views.view_timetable_all, name='view_timetable_all'),
    path('timetable/create/', views.create_timetable, name='create_timetable'),

    # Announcement URLs
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/edit/<int:announcement_id>/', views.edit_announcement, name='edit_announcement'),
    path('announcements/delete/<int:announcement_id>/', views.delete_announcement, name='delete_announcement'),
    path('announcements/all/', views.view_announcements_all, name='view_announcements_all'),
    
    # Student Management URLs
    path('students/', views.student_list, name='student_list'),
    path('student/add/', views.add_student, name='add_student'),
    path('student/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('student/<int:student_id>/remove/', views.remove_student, name='remove_student'),
]