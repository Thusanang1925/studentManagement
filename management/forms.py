from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Student, Tutor, Assessment, Mark, TimeSlot, Announcement

class StudentRegistrationForm(UserCreationForm):
    student_id = forms.CharField(max_length=20)
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address']
            )
        return user

class TutorRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=15)
    subject_expertise = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_tutor = True
        if commit:
            user.save()
            Tutor.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                subject_expertise=self.cleaned_data['subject_expertise']
            )
        return user

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'description', 'subject', 'max_marks', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['marks_obtained', 'comments']

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['day', 'start_time', 'end_time', 'subject']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'students' in self.fields:
            del self.fields['students']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'important']