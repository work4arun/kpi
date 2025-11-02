
"""
Views for submissions app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.submissions.models import Submission
from apps.submissions.forms import SubmissionCreateForm
from apps.submissions.services import SubmissionService
from apps.kpi.models import SubParameter
from apps.kpi.services import KPIService
from apps.forms_builder.renderers import DynamicFormRenderer
from apps.common.decorators import role_required
from apps.common.constants import SubmissionStatus
import csv
from django.http import HttpResponse


@login_required
@role_required('FACULTY', 'HOD')
def submission_list(request):
    """List user's submissions"""
    filters = {
        'status': request.GET.get('status'),
        'month': request.GET.get('month'),
        'year': request.GET.get('year'),
        'main_parameter': request.GET.get('main_parameter')
    }
    
    submissions = SubmissionService.get_user_submissions(request.user, filters)
    
    context = {
        'submissions': submissions,
        'filters': filters
    }
    return render(request, 'submissions/submission_list.html', context)


@login_required
@role_required('FACULTY', 'HOD')
def submission_create(request):
    """Create new submission - Step 1: Select sub-parameter"""
    if request.method == 'POST':
        form = SubmissionCreateForm(request.POST, user=request.user)
        if form.is_valid():
            sub_parameter = form.cleaned_data['sub_parameter']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            
            # Create or get submission
            submission = SubmissionService.create_submission(
                user=request.user,
                sub_parameter=sub_parameter,
                month=month,
                year=year
            )
            
            messages.success(request, 'Submission created. Please fill in the details.')
            return redirect('submissions:submission_edit', pk=submission.id)
    else:
        form = SubmissionCreateForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'submissions/submission_create.html', context)


@login_required
@role_required('FACULTY', 'HOD')
def submission_edit(request, pk):
    """Edit submission - Step 2: Fill dynamic form"""
    submission = get_object_or_404(Submission, pk=pk)
    
    # Check permissions
    if not SubmissionService.can_edit_submission(submission, request.user):
        messages.error(request, 'You cannot edit this submission.')
        return redirect('submissions:submission_list')
    
    # Get form template
    if not hasattr(submission.sub_parameter, 'form_template'):
        messages.error(request, 'No form template defined for this sub-parameter.')
        return redirect('submissions:submission_list')
    
    template = submission.sub_parameter.form_template
    DynamicForm = DynamicFormRenderer.render_form(template, submission)
    
    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES)
        if form.is_valid():
            # Save submission data
            SubmissionService.save_submission_data(
                submission=submission,
                form_data=form.cleaned_data,
                files=request.FILES,
                request=request
            )
            
            # Check if submitting or saving draft
            if 'submit' in request.POST:
                try:
                    SubmissionService.submit_submission(submission, request)
                    messages.success(request, 'Submission submitted successfully!')
                    return redirect('submissions:submission_detail', pk=submission.id)
                except ValueError as e:
                    messages.error(request, str(e))
            else:
                messages.success(request, 'Draft saved successfully.')
            
            return redirect('submissions:submission_edit', pk=submission.id)
    else:
        # Pre-populate form with existing values
        initial_data = {}
        for field_value in submission.field_values.all():
            initial_data[field_value.field_name] = field_value.value
        form = DynamicForm(initial=initial_data)
    
    context = {
        'form': form,
        'submission': submission,
        'template': template,
        'attachments': submission.attachments.all()
    }
    return render(request, 'submissions/submission_edit.html', context)


@login_required
def submission_detail(request, pk):
    """View submission details"""
    submission = get_object_or_404(Submission, pk=pk)
    
    # Check permissions
    if request.user != submission.user and not request.user.is_staff:
        if request.user.is_hod and submission.user.department != request.user.department:
            messages.error(request, 'You do not have permission to view this submission.')
            return redirect('submissions:submission_list')
    
    # Get field values with display
    field_values = []
    if hasattr(submission.sub_parameter, 'form_template'):
        template = submission.sub_parameter.form_template
        for field_value in submission.field_values.all():
            display_value = DynamicFormRenderer.get_field_value_display(
                field_value.field,
                field_value.value
            )
            field_values.append({
                'field': field_value.field,
                'value': display_value
            })
    
    context = {
        'submission': submission,
        'field_values': field_values,
        'attachments': submission.attachments.all(),
        'reviews': submission.reviews.all()
    }
    return render(request, 'submissions/submission_detail.html', context)


@login_required
@role_required('FACULTY', 'HOD')
def submission_delete(request, pk):
    """Delete submission (only drafts)"""
    submission = get_object_or_404(Submission, pk=pk)
    
    if submission.user != request.user:
        messages.error(request, 'You cannot delete this submission.')
        return redirect('submissions:submission_list')
    
    if submission.status != SubmissionStatus.DRAFT:
        messages.error(request, 'Only draft submissions can be deleted.')
        return redirect('submissions:submission_list')
    
    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'Submission deleted successfully.')
        return redirect('submissions:submission_list')
    
    context = {'submission': submission}
    return render(request, 'submissions/submission_confirm_delete.html', context)


@login_required
def export_submissions_csv(request):
    """Export submissions to CSV - Role-based filtering"""
    # Determine which submissions to export based on user role
    if request.user.is_admin:
        # Admin can export all submissions
        submissions = Submission.objects.all()
    elif request.user.is_hod:
        # HoD can export all submissions from their department
        submissions = Submission.objects.filter(
            user__department=request.user.department
        )
    elif request.user.is_dean:
        # Dean can export submissions from all their departments
        submissions = Submission.objects.filter(
            user__department__in=request.user.dean_departments.all()
        )
    else:
        # Faculty can only export their own submissions
        submissions = Submission.objects.filter(user=request.user)
    
    submissions = submissions.select_related(
        'sub_parameter',
        'sub_parameter__main_parameter',
        'user',
        'user__department'
    )
    
    # Apply filters
    status = request.GET.get('status')
    if status:
        submissions = submissions.filter(status=status)
    
    month = request.GET.get('month')
    if month:
        submissions = submissions.filter(month=int(month))
    
    year = request.GET.get('year')
    if year:
        submissions = submissions.filter(year=int(year))
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="submissions.csv"'
    
    writer = csv.writer(response)
    
    # Header row - include user info for HoD/Admin/Dean
    if request.user.is_hod or request.user.is_admin or request.user.is_dean:
        writer.writerow([
            'Faculty Name',
            'Department',
            'Month',
            'Year',
            'Main Parameter',
            'Sub Parameter',
            'Status',
            'Awarded Points',
            'Max Points',
            'Submitted At'
        ])
    else:
        writer.writerow([
            'Month',
            'Year',
            'Main Parameter',
            'Sub Parameter',
            'Status',
            'Awarded Points',
            'Max Points',
            'Submitted At'
        ])
    
    # Data rows
    for submission in submissions:
        if request.user.is_hod or request.user.is_admin or request.user.is_dean:
            writer.writerow([
                submission.user.full_name,
                submission.user.department.name,
                submission.month,
                submission.year,
                submission.sub_parameter.main_parameter.name,
                submission.sub_parameter.name,
                submission.get_status_display(),
                submission.awarded_points if submission.awarded_points is not None else '',
                submission.sub_parameter.max_points,
                submission.submitted_at.strftime('%Y-%m-%d %H:%M') if submission.submitted_at else ''
            ])
        else:
            writer.writerow([
                submission.month,
                submission.year,
                submission.sub_parameter.main_parameter.name,
                submission.sub_parameter.name,
                submission.get_status_display(),
                submission.awarded_points if submission.awarded_points is not None else '',
                submission.sub_parameter.max_points,
                submission.submitted_at.strftime('%Y-%m-%d %H:%M') if submission.submitted_at else ''
            ])
    
    return response
