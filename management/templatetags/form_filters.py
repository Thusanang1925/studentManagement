from django import template
from django.forms.widgets import CheckboxSelectMultiple

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field"""
    if isinstance(field.field.widget, CheckboxSelectMultiple):
        return field
    return field.as_widget(attrs={"class": css_class})
