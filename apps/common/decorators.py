
"""
Custom decorators for role-based access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """
    Decorator to restrict access to specific roles
    Usage: @role_required('ADMIN', 'HOD')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('common:home')
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator to restrict access to admin users only
    """
    return role_required('ADMIN')(view_func)


def faculty_required(view_func):
    """
    Decorator to restrict access to faculty users
    """
    return role_required('FACULTY')(view_func)


def hod_required(view_func):
    """
    Decorator to restrict access to HoD users
    """
    return role_required('HOD')(view_func)


def dean_required(view_func):
    """
    Decorator to restrict access to Dean users
    """
    return role_required('DEAN')(view_func)


def hod_or_dean_required(view_func):
    """
    Decorator to restrict access to HoD or Dean users
    """
    return role_required('HOD', 'DEAN')(view_func)
