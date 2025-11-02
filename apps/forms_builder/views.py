
"""
Views for forms builder app (Admin only)
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.common.decorators import admin_required


@admin_required
def form_builder_index(request):
    """Form builder management index"""
    return render(request, 'forms_builder/index.html')
