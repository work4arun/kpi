
"""
Utility functions used throughout the application
"""
import os
from datetime import datetime, date
from django.conf import settings
from django.utils import timezone
from apps.common.constants import MONTHS


def get_current_month_year():
    """
    Get current month and year in Indian timezone
    """
    now = timezone.now()
    return now.month, now.year


def get_month_name(month_number):
    """
    Convert month number to name
    """
    month_dict = dict(MONTHS)
    return month_dict.get(month_number, '')


def format_month_year(month, year):
    """
    Format month and year as string (e.g., "January 2025")
    """
    return f"{get_month_name(month)} {year}"


def validate_file_extension(filename):
    """
    Validate file extension against allowed types
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in settings.ALLOWED_FILE_TYPES


def validate_file_size(file_size):
    """
    Validate file size against max upload size
    """
    return file_size <= settings.MAX_UPLOAD_SIZE


def sanitize_filename(filename):
    """
    Sanitize filename to prevent security issues
    """
    # Remove path components
    filename = os.path.basename(filename)
    # Replace spaces and special characters
    filename = filename.replace(' ', '_')
    return filename


def get_upload_path(instance, filename):
    """
    Generate upload path for attachments
    Format: attachments/YYYY/MM/user_id/filename
    """
    now = timezone.now()
    user_id = instance.submission.user.id if hasattr(instance, 'submission') else 'unknown'
    filename = sanitize_filename(filename)
    return f'attachments/{now.year}/{now.month:02d}/{user_id}/{filename}'


def check_cutoff_deadline(cutoff_window, user_role):
    """
    Check if current time is within deadline for the given role
    Returns: (is_within_deadline, deadline_field_name)
    """
    now = timezone.now()
    
    if user_role == 'FACULTY':
        deadline = cutoff_window.faculty_submit_deadline
        field_name = 'faculty_submit_deadline'
    elif user_role == 'HOD':
        deadline = cutoff_window.hod_approve_deadline
        field_name = 'hod_approve_deadline'
    elif user_role == 'DEAN':
        deadline = cutoff_window.dean_approve_deadline
        field_name = 'dean_approve_deadline'
    else:
        return False, None
    
    # Convert deadline to timezone-aware datetime if it's naive
    if deadline and timezone.is_naive(deadline):
        deadline = timezone.make_aware(deadline)
    
    is_within = deadline is None or now <= deadline
    return is_within, field_name


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(actor, action, target, description, comment='', metadata=None, request=None):
    """
    Helper function to create activity log entries
    """
    from apps.common.models import ActivityLog
    
    log_data = {
        'actor': actor,
        'action': action,
        'target_model': target.__class__.__name__,
        'target_id': target.id,
        'description': description,
        'comment': comment,
        'metadata': metadata or {},
    }
    
    if request:
        log_data['ip_address'] = get_client_ip(request)
    
    return ActivityLog.objects.create(**log_data)
