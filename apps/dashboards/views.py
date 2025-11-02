
"""
Views for dashboards app - Role-based dashboards with charts
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.dashboards.services import ScoringService
from apps.common.utils import get_current_month_year
from apps.departments.models import Department
from apps.kpi.models import MainParameter
import json


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on role"""
    user = request.user
    
    if user.is_admin:
        return render(request, 'dashboards/admin_dashboard.html', get_admin_dashboard_data(request))
    elif user.is_hod:
        return render(request, 'dashboards/hod_dashboard.html', get_hod_dashboard_data(request))
    elif user.is_dean:
        return render(request, 'dashboards/dean_dashboard.html', get_dean_dashboard_data(request))
    else:  # Faculty
        return render(request, 'dashboards/faculty_dashboard.html', get_faculty_dashboard_data(request))


def get_faculty_dashboard_data(request):
    """Get data for faculty dashboard"""
    month = int(request.GET.get('month', get_current_month_year()[0]))
    year = int(request.GET.get('year', get_current_month_year()[1]))
    
    # Get faculty scores
    scores_data = ScoringService.get_faculty_scores(request.user, month, year)
    
    # Get submission status counts
    status_counts = ScoringService.get_submission_status_counts(
        user=request.user,
        month=month,
        year=year
    )
    
    # Prepare chart data
    param_labels = []
    param_awarded = []
    param_max = []
    
    for param_name, data in scores_data.get('scores', {}).items():
        param_labels.append(param_name)
        param_awarded.append(data.get('awarded_points', 0))
        param_max.append(data.get('max_points', 0))
    
    return {
        'scores_data': scores_data,
        'status_counts': status_counts,
        'month': month,
        'year': year,
        'param_labels': json.dumps(param_labels),
        'param_awarded': json.dumps(param_awarded),
        'param_max': json.dumps(param_max),
    }


def get_hod_dashboard_data(request):
    """Get data for HoD dashboard"""
    month = int(request.GET.get('month', get_current_month_year()[0]))
    year = int(request.GET.get('year', get_current_month_year()[1]))
    
    # Get HoD scores (including team average)
    scores_data = ScoringService.get_hod_scores(request.user, month, year)
    
    # Get department submission stats
    status_counts = ScoringService.get_submission_status_counts(
        department=request.user.department,
        month=month,
        year=year
    )
    
    # Get main parameter breakdown for department
    param_breakdown = ScoringService.get_main_parameter_breakdown(
        request.user.department,
        month,
        year
    )
    
    # Prepare chart data with safety checks
    param_labels = [item.get('main_parameter').name for item in param_breakdown if item.get('main_parameter')]
    param_points = [item.get('total_points', 0) for item in param_breakdown]
    
    return {
        'scores_data': scores_data,
        'status_counts': status_counts,
        'param_breakdown': param_breakdown,
        'month': month,
        'year': year,
        'param_labels': json.dumps(param_labels),
        'param_points': json.dumps(param_points),
    }


def get_dean_dashboard_data(request):
    """Get data for Dean dashboard"""
    month = int(request.GET.get('month', get_current_month_year()[0]))
    year = int(request.GET.get('year', get_current_month_year()[1]))
    
    # Get department comparison
    dept_comparison = ScoringService.get_department_comparison(month, year)
    
    # Filter to only Dean's departments
    dean_depts = request.user.dean_departments.all()
    dept_comparison = [d for d in dept_comparison if d.get('department') in dean_depts]
    
    # Get faculty leaderboard across all departments
    leaderboard = ScoringService.get_faculty_leaderboard(month=month, year=year, limit=20)
    
    # Prepare chart data with safety checks
    dept_labels = [d.get('department').name for d in dept_comparison if d.get('department')]
    dept_points = [d.get('total_points', 0) for d in dept_comparison]
    dept_avg_points = [d.get('average_points', 0) for d in dept_comparison]
    
    return {
        'dept_comparison': dept_comparison,
        'leaderboard': leaderboard,
        'month': month,
        'year': year,
        'dept_labels': json.dumps(dept_labels),
        'dept_points': json.dumps(dept_points),
        'dept_avg_points': json.dumps(dept_avg_points),
    }


def get_admin_dashboard_data(request):
    """Get data for Admin dashboard"""
    month = int(request.GET.get('month', get_current_month_year()[0]))
    year = int(request.GET.get('year', get_current_month_year()[1]))
    department_filter = request.GET.get('department')
    
    # Get department comparison
    dept_comparison = ScoringService.get_department_comparison(month, year)
    
    # Get faculty leaderboard
    # Convert department_filter (ID) to Department object if provided
    dept_obj = None
    if department_filter:
        dept_obj = Department.objects.get(id=department_filter)
    
    leaderboard = ScoringService.get_faculty_leaderboard(
        department=dept_obj,
        month=month,
        year=year,
        limit=20
    )
    
    # Get main parameter breakdown
    if dept_obj:
        param_breakdown = ScoringService.get_main_parameter_breakdown(dept_obj, month, year)
    else:
        # Aggregate across all departments
        param_breakdown = []
        main_params = MainParameter.objects.filter(is_active=True)
        for param in main_params:
            total = sum(
                ScoringService.get_main_parameter_breakdown(dept['department'], month, year)[0]['total_points']
                for dept in dept_comparison
                if dept['department']
            )
            param_breakdown.append({
                'main_parameter': param,
                'total_points': total
            })
    
    # Prepare chart data
    dept_labels = [d['department'].name for d in dept_comparison]
    dept_points = [d['total_points'] for d in dept_comparison]
    
    param_labels = [item['main_parameter'].name for item in param_breakdown]
    param_points = [item['total_points'] for item in param_breakdown]
    
    return {
        'dept_comparison': dept_comparison,
        'leaderboard': leaderboard,
        'param_breakdown': param_breakdown,
        'month': month,
        'year': year,
        'department_filter': department_filter,
        'dept_labels': json.dumps(dept_labels),
        'dept_points': json.dumps(dept_points),
        'param_labels': json.dumps(param_labels),
        'param_points': json.dumps(param_points),
    }
