from django import template
from django.db.models import Avg, Max
from django.forms.widgets import CheckboxSelectMultiple
from ..models import TimeSlot

register = template.Library()

@register.filter
def average_score(marks):
    if not marks:
        return 0
    total_percentage = sum((mark.marks_obtained / mark.assessment.max_marks * 100) for mark in marks)
    return total_percentage / len(marks)

@register.filter
def highest_score(marks):
    if not marks:
        return 0
    return max((mark.marks_obtained / mark.assessment.max_marks * 100) for mark in marks)

@register.filter
def unique_subjects(marks):
    if not marks:
        return []
    return list(set(mark.assessment.subject for mark in marks))

@register.filter
def divide(value, arg):
    """Divides the value by the argument"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return None

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return None

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary using the key"""
    return dictionary.get(key)

@register.filter
def get_day_display(day_code):
    """Gets the display name for a day code"""
    day_dict = dict(TimeSlot.DAY_CHOICES)
    return day_dict.get(day_code, day_code)

@register.filter
def get_student_mark(student, assessment):
    """Gets a student's mark for a given assessment"""
    try:
        return student.mark_set.filter(assessment=assessment).first()
    except:
        return None

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field"""
    if isinstance(field.field.widget, CheckboxSelectMultiple):
        return field
    return field.as_widget(attrs={"class": css_class})
