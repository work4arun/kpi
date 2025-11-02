
"""
Validators for dynamic form fields
"""
import re
from django.core.exceptions import ValidationError
from django.conf import settings


def validate_json_choices(value):
    """
    Validate that choices are in the correct JSON format
    """
    if not value:
        return
    
    if not isinstance(value, list):
        raise ValidationError("Choices must be a list")
    
    # Check if it's a list of simple values or list of [value, label] pairs
    for item in value:
        if isinstance(item, (list, tuple)):
            if len(item) != 2:
                raise ValidationError("Choice pairs must have exactly 2 elements [value, label]")
        elif not isinstance(item, (str, int, float)):
            raise ValidationError("Choice values must be strings, numbers, or [value, label] pairs")


def validate_field_name(value):
    """
    Validate field name (machine name) - only alphanumeric and underscores
    """
    if not re.match(r'^[a-z][a-z0-9_]*$', value):
        raise ValidationError(
            "Field name must start with a lowercase letter and contain only "
            "lowercase letters, numbers, and underscores"
        )


def validate_file_size(file):
    """
    Validate uploaded file size
    """
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"File size cannot exceed {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB"
        )


def validate_file_extension(filename):
    """
    Validate file extension
    """
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(
            f"File type {ext} is not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )
