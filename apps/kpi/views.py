
"""
Views for KPI app - Parameter management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.kpi.models import MainParameter, SubParameter, CutoffWindow
from apps.common.decorators import admin_required


@admin_required
def main_parameter_list(request):
    """List all main parameters"""
    parameters = MainParameter.objects.prefetch_related('sub_parameters').order_by('order', 'name')
    
    context = {'parameters': parameters}
    return render(request, 'kpi/main_parameter_list.html', context)


@admin_required
def sub_parameter_list(request):
    """List all sub-parameters"""
    sub_parameters = SubParameter.objects.select_related('main_parameter').order_by('main_parameter', 'order')
    
    context = {'sub_parameters': sub_parameters}
    return render(request, 'kpi/sub_parameter_list.html', context)


@admin_required
def cutoff_window_list(request):
    """List all cutoff windows"""
    windows = CutoffWindow.objects.prefetch_related('departments').order_by('-year', '-month')
    
    context = {'windows': windows}
    return render(request, 'kpi/cutoff_window_list.html', context)
