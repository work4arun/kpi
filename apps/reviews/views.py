
"""
Views for reviews app - Approval workflow
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.submissions.models import Submission
from apps.reviews.forms import ReviewApproveForm, ReviewRejectForm, DeanApprovalForm
from apps.reviews.services import ReviewService
from apps.common.decorators import hod_or_dean_required, dean_required
from apps.common.constants import SubmissionStatus


@login_required
@hod_or_dean_required
def review_list(request):
    """List submissions pending review"""
    pending_reviews = ReviewService.get_pending_reviews(request.user)
    
    # Apply filters
    status = request.GET.get('status')
    department = request.GET.get('department')
    
    if status:
        pending_reviews = pending_reviews.filter(status=status)
    if department:
        pending_reviews = pending_reviews.filter(user__department_id=department)
    
    context = {
        'pending_reviews': pending_reviews,
        'user': request.user
    }
    return render(request, 'reviews/review_list.html', context)


@login_required
@hod_or_dean_required
def review_detail(request, pk):
    """Review submission detail with action forms"""
    submission = get_object_or_404(Submission, pk=pk)
    
    # Check permissions
    if request.user.is_hod:
        if submission.user.department != request.user.department:
            messages.error(request, 'You cannot review this submission.')
            return redirect('reviews:review_list')
    elif request.user.is_dean:
        if submission.user.department not in request.user.dean_departments.all():
            messages.error(request, 'You cannot review this submission.')
            return redirect('reviews:review_list')
    
    # Get field values for display
    from apps.forms_builder.renderers import DynamicFormRenderer
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
    return render(request, 'reviews/review_detail.html', context)


@login_required
@hod_or_dean_required
def review_approve(request, pk):
    """Approve submission"""
    submission = get_object_or_404(Submission, pk=pk)
    
    if request.method == 'POST':
        form = ReviewApproveForm(request.POST, submission=submission)
        if form.is_valid():
            try:
                ReviewService.approve_submission(
                    submission=submission,
                    reviewer=request.user,
                    awarded_points=form.cleaned_data['awarded_points'],
                    comment=form.cleaned_data['comment'],
                    request=request
                )
                messages.success(request, 'Submission approved successfully.')
                return redirect('reviews:review_list')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = ReviewApproveForm(submission=submission)
    
    context = {
        'form': form,
        'submission': submission
    }
    return render(request, 'reviews/review_approve.html', context)


@login_required
@hod_or_dean_required
def review_reject(request, pk):
    """Reject submission"""
    submission = get_object_or_404(Submission, pk=pk)
    
    if request.method == 'POST':
        form = ReviewRejectForm(request.POST)
        if form.is_valid():
            try:
                ReviewService.reject_submission(
                    submission=submission,
                    reviewer=request.user,
                    comment=form.cleaned_data['comment'],
                    request=request
                )
                messages.success(request, 'Submission rejected.')
                return redirect('reviews:review_list')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = ReviewRejectForm()
    
    context = {
        'form': form,
        'submission': submission
    }
    return render(request, 'reviews/review_reject.html', context)


@login_required
@hod_or_dean_required
def review_request_revision(request, pk):
    """Request revision on submission"""
    submission = get_object_or_404(Submission, pk=pk)
    
    if request.method == 'POST':
        form = ReviewRejectForm(request.POST)
        if form.is_valid():
            try:
                ReviewService.request_revision(
                    submission=submission,
                    reviewer=request.user,
                    comment=form.cleaned_data['comment'],
                    request=request
                )
                messages.success(request, 'Revision requested.')
                return redirect('reviews:review_list')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = ReviewRejectForm()
    
    context = {
        'form': form,
        'submission': submission
    }
    return render(request, 'reviews/review_revision.html', context)


@login_required
@dean_required
def dean_review_list(request):
    """Dean's consolidated review list by faculty"""
    from apps.accounts.models import User
    from apps.common.constants import UserRole
    
    # Get faculty from Dean's departments
    dean_depts = request.user.dean_departments.all()
    faculty_list = User.objects.filter(
        department__in=dean_depts,
        role=UserRole.FACULTY,
        is_active=True
    ).select_related('department').order_by('full_name')
    
    # Get month/year filters
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not month or not year:
        from apps.common.utils import get_current_month_year
        month, year = get_current_month_year()
        month = int(month)
        year = int(year)
    else:
        month = int(month)
        year = int(year)
    
    # Get submissions for each faculty
    faculty_data = []
    for faculty in faculty_list:
        submissions = Submission.objects.filter(
            user=faculty,
            month=month,
            year=year,
            status=SubmissionStatus.HOD_APPROVED
        )
        
        if submissions.exists():
            total_points = sum(s.awarded_points for s in submissions)
            faculty_data.append({
                'faculty': faculty,
                'submissions': submissions,
                'total_points': total_points,
                'submission_count': submissions.count()
            })
    
    context = {
        'faculty_data': faculty_data,
        'month': month,
        'year': year
    }
    return render(request, 'reviews/dean_review_list.html', context)


@login_required
@dean_required
def dean_approve_faculty(request, faculty_id):
    """Dean approves all submissions for a faculty for a window"""
    from apps.accounts.models import User
    faculty = get_object_or_404(User, pk=faculty_id)
    
    month = int(request.GET.get('month'))
    year = int(request.GET.get('year'))
    
    if request.method == 'POST':
        form = DeanApprovalForm(request.POST)
        if form.is_valid():
            try:
                ReviewService.dean_approve_faculty(
                    faculty=faculty,
                    month=month,
                    year=year,
                    dean=request.user,
                    comment=form.cleaned_data['comment'],
                    request=request
                )
                messages.success(request, f'Approved all submissions for {faculty.full_name}')
                return redirect('reviews:dean_review_list')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = DeanApprovalForm()
    
    # Get submissions
    submissions = Submission.objects.filter(
        user=faculty,
        month=month,
        year=year,
        status=SubmissionStatus.HOD_APPROVED
    )
    
    context = {
        'form': form,
        'faculty': faculty,
        'month': month,
        'year': year,
        'submissions': submissions,
        'total_points': sum(s.awarded_points for s in submissions)
    }
    return render(request, 'reviews/dean_approve.html', context)
