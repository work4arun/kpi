
"""
Views for departments app
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.departments.models import Department
from apps.common.decorators import admin_required


@admin_required
def department_list(request):
    """List all departments"""
    departments = Department.objects.all().order_by('name')
    
    context = {'departments': departments}
    return render(request, 'departments/department_list.html', context)
