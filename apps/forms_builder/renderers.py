
"""
Dynamic form renderer - Converts DynamicField definitions into HTML forms
"""
from django import forms
from django.utils.safestring import mark_safe
from apps.common.constants import FieldType
import json


class DynamicFormRenderer:
    """
    Render dynamic forms from DynamicFormTemplate
    """
    
    @staticmethod
    def render_form(template, submission=None):
        """
        Generate Django form class from template
        Returns a form class
        """
        fields = template.get_fields_ordered()
        form_fields = {}
        
        for field in fields:
            django_field = DynamicFormRenderer.create_django_field(field, submission)
            form_fields[field.name] = django_field
        
        # Create dynamic form class
        DynamicForm = type('DynamicForm', (forms.Form,), form_fields)
        return DynamicForm
    
    @staticmethod
    def create_django_field(field, submission=None):
        """
        Convert DynamicField to Django form field
        """
        field_kwargs = {
            'required': field.is_required,
            'label': field.label,
            'help_text': field.help_text,
        }
        
        # Get existing value if editing
        initial_value = None
        if submission:
            try:
                field_value = submission.field_values.get(field=field)
                initial_value = field_value.value
            except:
                pass
        
        if initial_value:
            field_kwargs['initial'] = initial_value
        
        # Create appropriate field based on type
        if field.field_type == FieldType.TEXT:
            if field.max_length:
                field_kwargs['max_length'] = field.max_length
            if field.placeholder:
                field_kwargs['widget'] = forms.TextInput(attrs={'placeholder': field.placeholder})
            return forms.CharField(**field_kwargs)
        
        elif field.field_type == FieldType.TEXTAREA:
            if field.placeholder:
                field_kwargs['widget'] = forms.Textarea(attrs={
                    'placeholder': field.placeholder,
                    'rows': 4
                })
            return forms.CharField(**field_kwargs)
        
        elif field.field_type == FieldType.NUMBER:
            field_kwargs['widget'] = forms.NumberInput(attrs={'step': 'any'})
            if field.min_value is not None:
                field_kwargs['min_value'] = float(field.min_value)
            if field.max_value is not None:
                field_kwargs['max_value'] = float(field.max_value)
            return forms.DecimalField(**field_kwargs)
        
        elif field.field_type == FieldType.PERCENTAGE:
            field_kwargs['widget'] = forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'max': '100'
            })
            field_kwargs['min_value'] = 0
            field_kwargs['max_value'] = 100
            return forms.DecimalField(**field_kwargs)
        
        elif field.field_type == FieldType.DATE:
            field_kwargs['widget'] = forms.DateInput(attrs={'type': 'date'})
            return forms.DateField(**field_kwargs)
        
        elif field.field_type == FieldType.URL:
            return forms.URLField(**field_kwargs)
        
        elif field.field_type == FieldType.SELECT:
            choices = field.get_choices_list()
            if not field.is_required:
                choices = [('', '--- Select ---')] + choices
            field_kwargs['choices'] = choices
            return forms.ChoiceField(**field_kwargs)
        
        elif field.field_type == FieldType.MULTISELECT:
            field_kwargs['choices'] = field.get_choices_list()
            field_kwargs['widget'] = forms.CheckboxSelectMultiple()
            return forms.MultipleChoiceField(**field_kwargs)
        
        elif field.field_type == FieldType.FILE:
            field_kwargs['required'] = field.is_required
            return forms.FileField(**field_kwargs)
        
        elif field.field_type == FieldType.MULTIFILE:
            field_kwargs['required'] = field.is_required
            field_kwargs['widget'] = forms.ClearableFileInput(attrs={'multiple': True})
            return forms.FileField(**field_kwargs)
        
        # Default to text field
        return forms.CharField(**field_kwargs)
    
    @staticmethod
    def get_field_value_display(field, value):
        """
        Get human-readable display value for a field
        """
        if not value:
            return 'N/A'
        
        if field.field_type in [FieldType.SELECT, FieldType.MULTISELECT]:
            choices_dict = dict(field.get_choices_list())
            if field.field_type == FieldType.MULTISELECT:
                try:
                    value_list = json.loads(value) if isinstance(value, str) else value
                    return ', '.join([choices_dict.get(v, v) for v in value_list])
                except:
                    return value
            else:
                return choices_dict.get(value, value)
        
        return value
