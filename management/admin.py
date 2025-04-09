from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Tutor, Assessment, Mark, TimeSlot, Announcement

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_tutor', 'is_student')
    list_filter = ('is_tutor', 'is_student')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_tutor', 'is_student')}),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'phone')
    search_fields = ('user__username', 'student_id', 'phone')

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'subject_expertise')
    search_fields = ('user__username', 'phone', 'subject_expertise')

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'tutor', 'date', 'max_marks')
    list_filter = ('subject', 'tutor', 'date')
    search_fields = ('title', 'subject')

@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'assessment', 'marks_obtained', 'date_added')
    list_filter = ('assessment', 'date_added')
    search_fields = ('student__user__username', 'assessment__title')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'subject', 'tutor')
    list_filter = ('day', 'subject', 'tutor')
    filter_horizontal = ('students',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'tutor', 'date_posted', 'important')
    list_filter = ('tutor', 'date_posted', 'important')
    search_fields = ('title', 'content')
