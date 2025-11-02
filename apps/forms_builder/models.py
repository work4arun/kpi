
"""
Dynamic form builder models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TimeStampedModel
from apps.common.constants import FieldType
import json


class DynamicFormTemplate(TimeStampedModel):
    """
    Form template associated with a sub-parameter
    """
    sub_parameter = models.OneToOneField(
        'kpi.SubParameter',
        on_delete=models.CASCADE,
        related_name='form_template',
        help_text="Sub-parameter this form is for"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this form template is active"
    )
    instructions = models.TextField(
        blank=True,
        help_text="Instructions for filling the form"
    )
    
    class Meta:
        db_table = 'dynamic_form_templates'
        ordering = ['sub_parameter']
        verbose_name = 'Dynamic Form Template'
        verbose_name_plural = 'Dynamic Form Templates'
    
    def __str__(self):
        return f"Form for: {self.sub_parameter.name}"
    
    def get_fields_ordered(self):
        """Get form fields in order"""
        return self.fields.filter(is_active=True).order_by('order')


class DynamicField(TimeStampedModel):
    """
    Individual field in a dynamic form
    """
    template = models.ForeignKey(
        DynamicFormTemplate,
        on_delete=models.CASCADE,
        related_name='fields',
        help_text="Form template this field belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Machine name/key for this field (e.g., 'publication_title')"
    )
    label = models.CharField(
        max_length=255,
        help_text="Display label for this field"
    )
    field_type = models.CharField(
        max_length=20,
        choices=FieldType.CHOICES,
        help_text="Type of field"
    )
    help_text = models.TextField(
        blank=True,
        help_text="Help text to display under the field"
    )
    placeholder = models.CharField(
        max_length=255,
        blank=True,
        help_text="Placeholder text for input fields"
    )
    is_required = models.BooleanField(
        default=False,
        help_text="Whether this field is required"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order in the form"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this field is active"
    )
    
    # Field-specific options
    choices = models.JSONField(
        default=list,
        blank=True,
        help_text="Choices for select/multiselect fields (JSON array)"
    )
    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum value for number/percentage fields"
    )
    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum value for number/percentage fields"
    )
    pattern = models.CharField(
        max_length=255,
        blank=True,
        help_text="Regex pattern for validation"
    )
    max_length = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum length for text fields"
    )
    max_files = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of files for file upload fields"
    )
    
    class Meta:
        db_table = 'dynamic_fields'
        ordering = ['template', 'order']
        indexes = [
            models.Index(fields=['template', 'order']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Dynamic Field'
        verbose_name_plural = 'Dynamic Fields'
        unique_together = [['template', 'name']]
    
    def __str__(self):
        return f"{self.template.sub_parameter.name} > {self.label}"
    
    def get_choices_list(self):
        """
        Get choices as a list of tuples for form field
        """
        if not self.choices:
            return []
        
        if isinstance(self.choices, str):
            try:
                choices_data = json.loads(self.choices)
            except json.JSONDecodeError:
                return []
        else:
            choices_data = self.choices
        
        # Convert to list of tuples
        if isinstance(choices_data, list):
            if all(isinstance(c, (list, tuple)) and len(c) == 2 for c in choices_data):
                return choices_data
            else:
                return [(c, c) for c in choices_data]
        
        return []
    
    def validate_value(self, value):
        """
        Validate a value against this field's constraints
        Returns: (is_valid, error_message)
        """
        # Required check
        if self.is_required and not value:
            return False, f"{self.label} is required"
        
        # Type-specific validation
        if self.field_type in ['number', 'percentage']:
            try:
                num_value = float(value)
                if self.min_value is not None and num_value < float(self.min_value):
                    return False, f"{self.label} must be at least {self.min_value}"
                if self.max_value is not None and num_value > float(self.max_value):
                    return False, f"{self.label} must be at most {self.max_value}"
            except (ValueError, TypeError):
                return False, f"{self.label} must be a valid number"
        
        elif self.field_type in ['text', 'textarea']:
            if self.max_length and len(value) > self.max_length:
                return False, f"{self.label} must be at most {self.max_length} characters"
        
        elif self.field_type == 'url':
            if value and not value.startswith(('http://', 'https://')):
                return False, f"{self.label} must be a valid URL"
        
        elif self.field_type in ['select', 'multiselect']:
            valid_choices = [c[0] for c in self.get_choices_list()]
            if self.field_type == 'multiselect':
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        value = [value]
                if not all(v in valid_choices for v in value):
                    return False, f"{self.label} contains invalid choices"
            else:
                if value not in valid_choices:
                    return False, f"{self.label} contains an invalid choice"
        
        return True, ""
