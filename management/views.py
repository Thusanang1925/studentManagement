from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()
from django.db.models import Avg, Max, Min, F
from decimal import Decimal
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
from .forms import (
    StudentRegistrationForm, TutorRegistrationForm, AssessmentForm,
    MarkForm, TimeSlotForm, AnnouncementForm
)
from .models import Student, Tutor, Assessment, Mark, TimeSlot, Announcement
from django.contrib.auth.decorators import user_passes_test

def is_tutor(user):
    return user.is_authenticated and user.is_tutor

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please login to continue.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration/register_student.html', {'form': form})

def register_tutor(request):
    if request.method == 'POST':
        form = TutorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please login to continue.')
            return redirect('login')
    else:
        form = TutorRegistrationForm()
    return render(request, 'registration/register_tutor.html', {'form': form})

@login_required
def home(request):
    if request.user.is_tutor:
        tutor = Tutor.objects.get(user=request.user)
        assessments = Assessment.objects.filter(tutor=tutor).order_by('-date')
        
        # Get performance data for graphs
        performance_data = []
        subject_averages = {}
        total_students = Student.objects.count()
        
        for assessment in assessments:
            marks = Mark.objects.filter(assessment=assessment)
            if marks.exists():
                avg_marks = marks.aggregate(Avg('marks_obtained'))['marks_obtained__avg']
                passing_count = marks.filter(marks_obtained__gte=assessment.max_marks * 0.5).count()
                
                performance_data.append({
                    'title': assessment.title,
                    'average': round(avg_marks, 2),
                    'max_marks': assessment.max_marks,
                    'passing_percentage': round((passing_count / total_students) * 100, 2),
                    'date': assessment.date.strftime('%Y-%m-%d')
                })
                
                # Calculate subject-wise averages
                if assessment.subject not in subject_averages:
                    subject_averages[assessment.subject] = {'total': 0, 'count': 0}
                subject_averages[assessment.subject]['total'] += (avg_marks / assessment.max_marks) * 100
                subject_averages[assessment.subject]['count'] += 1
        
        # Calculate final subject averages
        subject_performance = [
            {
                'subject': subject,
                'average': round(data['total'] / data['count'], 2)
            }
            for subject, data in subject_averages.items()
        ]
        
        return render(request, 'management/tutor_dashboard.html', {
            'performance_data': json.dumps(performance_data, cls=DecimalEncoder),
            'subject_performance': json.dumps(subject_performance, cls=DecimalEncoder),
            'announcements': Announcement.objects.filter(tutor=tutor).order_by('-date_posted')
        })
    else:
        student = Student.objects.get(user=request.user)
        marks = Mark.objects.filter(student=student)
        timeslots = TimeSlot.objects.filter(students=student)
        announcements = Announcement.objects.all()
        return render(request, 'management/student_dashboard.html', {
            'marks': marks,
            'timeslots': timeslots,
            'announcements': announcements
        })

# Assessment Views
@user_passes_test(is_tutor)
def edit_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, tutor__user=request.user)

    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.tutor = Tutor.objects.get(user=request.user)
            assessment.save()
            messages.success(request, 'Assessment updated successfully!')
            return redirect('manage_marks')
    else:
        form = AssessmentForm(instance=assessment)

    return render(request, 'management/assessment_form.html', {'form': form, 'assessment': assessment})

@user_passes_test(is_tutor)
def delete_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, tutor__user=request.user)

    if request.method == 'POST':
        assessment.delete()
        messages.success(request, 'Assessment deleted successfully!')
        return redirect('manage_marks')

    return render(request, 'management/delete_assessment.html', {'assessment': assessment})

@user_passes_test(is_tutor)
def create_assessment(request):
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.tutor = Tutor.objects.get(user=request.user)
            assessment.save()
            messages.success(request, 'Assessment created successfully!')
            return redirect('manage_marks')
    else:
        form = AssessmentForm()
    return render(request, 'management/assessment_form.html', {'form': form})

@user_passes_test(is_tutor)
def add_marks(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    if request.method == 'POST':
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, id=student_id)
        form = MarkForm(request.POST)
        if form.is_valid():
            mark = form.save(commit=False)
            mark.student = student
            mark.assessment = assessment
            mark.save()
            messages.success(request, 'Marks added successfully')
            return redirect('assessment_detail', assessment_id=assessment_id)
    else:
        form = MarkForm()
    students = Student.objects.all()
    return render(request, 'management/add_marks.html', {
        'form': form,
        'assessment': assessment,
        'students': students
    })



# Announcement Views
@user_passes_test(is_tutor)
def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.tutor = Tutor.objects.get(user=request.user)
            announcement.save()
            return redirect('home')
    else:
        form = AnnouncementForm()
    return render(request, 'management/announcement_form.html', {'form': form})

# Student Management Views
@user_passes_test(is_tutor)
def student_list(request):
    students = Student.objects.all()
    return render(request, 'management/student_list.html', {'students': students})

@user_passes_test(is_tutor)
def add_student(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return render(request, 'management/add_student.html', {
                'error': 'Username already exists',
                'data': request.POST  # Send back the data to refill the form
            })
            
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please use a different email address.')
            return render(request, 'management/add_student.html', {
                'error': 'Email already exists',
                'data': request.POST
            })
            
        try:
            # Create a new user account
            user = User.objects.create_user(
                username=username,
                password=request.POST['password'],
                email=email,
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                is_student=True
            )
            
            # Check if student ID already exists
            student_id = request.POST['student_id']
            if Student.objects.filter(student_id=student_id).exists():
                messages.error(request, 'Student ID already exists. Please use a different ID.')
                return render(request, 'management/add_student.html', {
                    'error': 'Student ID already exists',
                    'data': request.POST
                })

            # Create student profile
            student = Student.objects.create(
                user=user,
                phone=request.POST['phone'],
                address=request.POST['address'],
                student_id=student_id
            )
            
            # Create default timetable entry
            tutor = get_object_or_404(Tutor, user=request.user)
            timeslot = TimeSlot.objects.create(
                tutor=tutor,
                day='MON',
                start_time='09:00',
                end_time='10:30',
                subject='Introduction Session'
            )
            timeslot.students.add(student)
            
            messages.success(request, f'Student {user.get_full_name()} has been added successfully with a default timetable.')
            return redirect('student_list')
            
        except Exception as e:
            # If anything goes wrong, delete the user if it was created
            if 'user' in locals():
                user.delete()
            messages.error(request, f'Error creating student: {str(e)}')
            return render(request, 'management/add_student.html', {
                'error': str(e),
                'data': request.POST
            })
    
    return render(request, 'management/add_student.html')

@user_passes_test(is_tutor)
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        # Handle student edit
        student.phone = request.POST.get('phone')
        student.address = request.POST.get('address')
        student.save()
        messages.success(request, 'Student information updated successfully')
        return redirect('student_list')
    return render(request, 'management/edit_student.html', {'student': student})

@user_passes_test(is_tutor)
def remove_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.user.delete()  # This will also delete the student due to CASCADE
        messages.success(request, 'Student removed successfully')
        return redirect('student_list')
    return render(request, 'management/remove_student.html', {'student': student})

# View Pages
@login_required
def view_assessments(request):
    if request.user.is_tutor:
        tutor = get_object_or_404(Tutor, user=request.user)
        assessments = Assessment.objects.filter(tutor=tutor)
    else:
        student = get_object_or_404(Student, user=request.user)
        assessments = Assessment.objects.filter(mark__student=student).distinct()
    
    return render(request, 'management/view_assessments.html', {
        'assessments': assessments,
        'is_tutor': request.user.is_tutor
    })

@login_required
def view_timetable_all(request):
    if request.user.is_tutor:
        tutor = get_object_or_404(Tutor, user=request.user)
        timeslots = TimeSlot.objects.filter(tutor=tutor).prefetch_related('students')
        students = Student.objects.all()  # Get all students for the modal form
    else:
        student = get_object_or_404(Student, user=request.user)
        # Show all timeslots to students since they're all automatically enrolled
        timeslots = TimeSlot.objects.all().select_related('tutor', 'tutor__user')
        students = None

    # Define day order and create empty slots for each day
    day_order = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    timeslots_by_day = {day: [] for day in day_order}
    
    # Group timeslots by day
    for slot in timeslots:
        timeslots_by_day[slot.day].append(slot)
    
    # Sort each day's slots by start time
    for day in timeslots_by_day:
        timeslots_by_day[day].sort(key=lambda x: x.start_time)
    
    # Get total number of students for display
    student_count = Student.objects.count()

    return render(request, 'management/view_timetable.html', {
        'timeslots_by_day': timeslots_by_day,
        'day_order': day_order,
        'is_tutor': request.user.is_tutor,
        'students': students,
        'day_choices': TimeSlot.DAY_CHOICES,
        'student_count': student_count
    })

@login_required
def create_timetable(request):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can create timetable entries.')
        return redirect('view_timetable_all')

    tutor = get_object_or_404(Tutor, user=request.user)
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            timeslot = form.save(commit=False)
            timeslot.tutor = tutor
            timeslot.save()
            # Add all students to the timeslot
            students = Student.objects.all()
            timeslot.students.add(*students)
            messages.success(request, 'Timetable entry created successfully.')
            return redirect('view_timetable_all')
    else:
        form = TimeSlotForm(initial={'tutor': tutor})

    return render(request, 'management/edit_timetable.html', {
        'form': form,
        'is_tutor': True,
        'is_create': True
    })

@login_required
def edit_timetable(request, timeslot_id):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can edit timetable entries.')
        return redirect('view_timetable_all')

    timeslot = get_object_or_404(TimeSlot, id=timeslot_id)
    if timeslot.tutor.user != request.user:
        messages.error(request, 'You can only edit your own timetable entries.')
        return redirect('view_timetable_all')

    if request.method == 'POST':
        form = TimeSlotForm(request.POST, instance=timeslot)
        if form.is_valid():
            timeslot = form.save(commit=False)
            timeslot.save()
            # Keep all students assigned
            students = Student.objects.all()
            timeslot.students.clear()
            timeslot.students.add(*students)
            messages.success(request, 'Timetable entry updated successfully.')
            return redirect('view_timetable_all')
    else:
        form = TimeSlotForm(instance=timeslot)

    return render(request, 'management/edit_timetable.html', {
        'form': form,
        'timeslot': timeslot,
        'is_tutor': True,
        'is_create': False
    })

@login_required
def delete_timetable(request, timeslot_id):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can delete timetable entries.')
        return redirect('view_timetable_all')

    timeslot = get_object_or_404(TimeSlot, id=timeslot_id)
    if timeslot.tutor.user != request.user:
        messages.error(request, 'You can only delete your own timetable entries.')
        return redirect('view_timetable_all')

    if request.method == 'POST':
        timeslot.delete()
        messages.success(request, 'Timetable entry deleted successfully.')
        return redirect('view_timetable_all')

    return render(request, 'management/delete_timetable.html', {
        'timeslot': timeslot,
        'is_tutor': True
    })

@login_required
def view_announcements_all(request):
    if request.user.is_tutor:
        tutor = get_object_or_404(Tutor, user=request.user)
        announcements = Announcement.objects.filter(tutor=tutor).order_by('-date_posted')
    else:
        announcements = Announcement.objects.all().order_by('-date_posted')
    
    return render(request, 'management/view_announcements.html', {
        'announcements': announcements,
        'is_tutor': request.user.is_tutor
    })

@login_required
def manage_marks(request):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can manage marks.')
        return redirect('home')

    tutor = get_object_or_404(Tutor, user=request.user)
    assessments = Assessment.objects.filter(tutor=tutor).order_by('-date')
    
    # Get all students and their marks for each assessment
    students = Student.objects.all()
    marks = Mark.objects.filter(assessment__tutor=tutor)
    
    # Create a dictionary of student marks by assessment
    student_marks = {}
    for mark in marks:
        if mark.student_id not in student_marks:
            student_marks[mark.student_id] = {}
        student_marks[mark.student_id][mark.assessment_id] = mark
    
    # Add marks data to the context
    for student in students:
        student.marks_by_assessment = student_marks.get(student.id, {})

    return render(request, 'management/manage_marks.html', {
        'assessments': assessments,
        'students': students,
        'is_tutor': True
    })

@login_required
def student_marks(request):
    if request.user.is_tutor:
        messages.error(request, 'This page is only for students.')
        return redirect('home')

    student = get_object_or_404(Student, user=request.user)
    marks = Mark.objects.filter(student=student).select_related('assessment').order_by('-assessment__date')
    
    if not marks.exists():
        messages.info(request, 'You have no marks recorded yet.')

    # Calculate percentages for each mark
    marks_with_percentages = []
    for mark in marks:
        percentage = (mark.marks_obtained / mark.assessment.max_marks * 100)
        marks_with_percentages.append({
            'mark': mark,
            'percentage': round(percentage, 1)
        })

    return render(request, 'management/student_marks.html', {
        'marks_with_percentages': marks_with_percentages,
        'is_tutor': False
    })

@login_required
def view_marks(request, assessment_id):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can view all marks.')
        return redirect('home')

    assessment = get_object_or_404(Assessment, id=assessment_id, tutor__user=request.user)
    marks = Mark.objects.filter(assessment=assessment).select_related('student', 'assessment').order_by('student__user__first_name')
    students = Student.objects.all().order_by('user__first_name')

    # Calculate statistics
    total_students = students.count()
    marked_students = marks.count()
    if marked_students > 0:
        avg_marks = marks.aggregate(Avg('marks_obtained'))['marks_obtained__avg']
        max_marks = marks.aggregate(Max('marks_obtained'))['marks_obtained__max']
        min_marks = marks.aggregate(Min('marks_obtained'))['marks_obtained__min']
    else:
        avg_marks = max_marks = min_marks = 0

    context = {
        'assessment': assessment,
        'marks': marks,
        'students': students,
        'total_students': total_students,
        'marked_students': marked_students,
        'unmarked_students': total_students - marked_students,
        'avg_marks': round(avg_marks, 2) if avg_marks else 0,
        'max_marks': max_marks,
        'min_marks': min_marks,
    }

    return render(request, 'management/view_marks.html', context)

@login_required
def add_marks(request, assessment_id):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can add marks.')
        return redirect('home')

    assessment = get_object_or_404(Assessment, id=assessment_id, tutor__user=request.user)

    if request.method == 'POST':
        try:
            for key, value in request.POST.items():
                if key.startswith('marks_'):
                    student_id = int(key.split('_')[1])
                    student = get_object_or_404(Student, id=student_id)
                    marks = value.strip()
                    comments = request.POST.get(f'comments_{student_id}', '').strip()
                    
                    if marks:  # Only save if marks are provided
                        try:
                            marks_float = float(marks)
                            if marks_float < 0:
                                raise ValueError('Marks cannot be negative')
                            if marks_float > assessment.max_marks:
                                raise ValueError(f'Marks cannot exceed maximum marks ({assessment.max_marks})')
                            
                            Mark.objects.update_or_create(
                                student=student,
                                assessment=assessment,
                                defaults={
                                    'marks_obtained': marks_float,
                                    'comments': comments
                                }
                            )
                        except ValueError as ve:
                            messages.error(request, f'Invalid marks for {student.user.get_full_name()}: {str(ve)}')
                            return redirect('manage_marks')
            
            messages.success(request, 'Marks have been saved successfully!')
        except Exception as e:
            messages.error(request, f'Error saving marks: {str(e)}')
        
        return redirect('manage_marks')

    return redirect('manage_marks')

@login_required
def create_assessment(request):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can create assessments.')
        return redirect('home')

    if request.method == 'POST':
        tutor = get_object_or_404(Tutor, user=request.user)
        assessment = Assessment.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            subject=request.POST['subject'],
            max_marks=request.POST['max_marks'],
            date=request.POST['date'],
            tutor=tutor
        )
        messages.success(request, 'Assessment created successfully!')
        return redirect('view_assessments')

    return redirect('view_assessments')

@login_required
def create_timetable(request):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can create timetable entries.')
        return redirect('home')

    if request.method == 'POST':
        tutor = get_object_or_404(Tutor, user=request.user)
        timeslot = TimeSlot.objects.create(
            day=request.POST['day'],
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time'],
            subject=request.POST['subject'],
            tutor=tutor
        )
        
        # Add selected students
        student_ids = request.POST.getlist('students')
        for student_id in student_ids:
            student = get_object_or_404(Student, id=student_id)
            timeslot.students.add(student)

        messages.success(request, 'Timetable entry created successfully!')
        return redirect('view_timetable_all')

    return redirect('view_timetable_all')

@login_required
def edit_announcement(request, announcement_id):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can edit announcements.')
        return redirect('home')

    announcement = get_object_or_404(Announcement, id=announcement_id, tutor__user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            announcement.title = title
            announcement.content = content
            announcement.save()
            messages.success(request, 'Announcement updated successfully!')
        else:
            messages.error(request, 'Title and content are required.')
        return redirect('view_announcements_all')

    return redirect('view_announcements_all')

@login_required
def delete_announcement(request, announcement_id):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can delete announcements.')
        return redirect('home')

    announcement = get_object_or_404(Announcement, id=announcement_id, tutor__user=request.user)

    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully!')

    return redirect('view_announcements_all')

@login_required
def create_announcement(request):
    if not request.user.is_tutor:
        messages.error(request, 'Only tutors can create announcements.')
        return redirect('home')

    if request.method == 'POST':
        tutor = get_object_or_404(Tutor, user=request.user)
        announcement = Announcement.objects.create(
            title=request.POST['title'],
            content=request.POST['content'],
            important=request.POST.get('important', False) == 'on',
            tutor=tutor
        )
        messages.success(request, 'Announcement created successfully!')
        return redirect('view_announcements_all')

    return redirect('view_announcements_all')
