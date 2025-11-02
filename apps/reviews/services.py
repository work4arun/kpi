
"""
Service layer for review and approval workflow
"""
from django.db import transaction
from django.utils import timezone
from apps.submissions.models import Submission
from apps.reviews.models import Review, DeanApproval
from apps.common.constants import SubmissionStatus, ActivityAction, ApprovalRouting
from apps.common.utils import log_activity, check_cutoff_deadline
from apps.kpi.models import CutoffWindow


class ReviewService:
    """
    Service for handling review and approval operations
    """
    
    @staticmethod
    def get_pending_reviews(reviewer):
        """
        Get submissions pending review for a given reviewer
        """
        queryset = Submission.objects.filter(
            status=SubmissionStatus.SUBMITTED
        ).select_related(
            'user', 'sub_parameter', 'sub_parameter__main_parameter'
        ).order_by('-submitted_at')
        
        # Filter based on reviewer role
        if reviewer.is_hod:
            # HoD sees submissions from their department with HOD routing
            queryset = queryset.filter(
                user__department=reviewer.department,
                sub_parameter__approval_routing=ApprovalRouting.HOD
            )
        elif reviewer.is_dean:
            # Dean sees HOD-approved submissions from their departments
            dean_depts = reviewer.dean_departments.all()
            queryset = Submission.objects.filter(
                status=SubmissionStatus.HOD_APPROVED,
                user__department__in=dean_depts
            ).select_related(
                'user', 'sub_parameter', 'sub_parameter__main_parameter'
            ).order_by('-reviewed_at')
        else:
            # For OTHER approvers, check email match
            queryset = queryset.filter(
                sub_parameter__approval_routing=ApprovalRouting.OTHER,
                sub_parameter__other_approver_email=reviewer.email
            )
        
        return queryset
    
    @staticmethod
    @transaction.atomic
    def approve_submission(submission, reviewer, awarded_points, comment='', request=None):
        """
        Approve a submission and award points
        """
        if submission.status != SubmissionStatus.SUBMITTED:
            raise ValueError("Only submitted submissions can be approved")
        
        # Validate awarded points
        if awarded_points < 0:
            raise ValueError("Awarded points cannot be negative")
        if awarded_points > submission.sub_parameter.max_points:
            raise ValueError(f"Awarded points cannot exceed {submission.sub_parameter.max_points}")
        
        # Check deadline
        cutoff_window = CutoffWindow.get_active_window(
            submission.month,
            submission.year,
            submission.user.department
        )
        
        if cutoff_window and not reviewer.can_override_deadlines:
            is_within, _ = check_cutoff_deadline(cutoff_window, reviewer.role)
            if not is_within:
                raise ValueError("Approval deadline has passed")
        
        # Update submission
        previous_status = submission.status
        submission.status = SubmissionStatus.HOD_APPROVED
        submission.awarded_points = awarded_points
        submission.reviewer = reviewer
        submission.review_comment = comment
        submission.reviewed_at = timezone.now()
        submission.save()
        
        # Create review record
        Review.objects.create(
            submission=submission,
            reviewer=reviewer,
            action='APPROVED',
            awarded_points=awarded_points,
            comment=comment,
            previous_status=previous_status,
            new_status=submission.status
        )
        
        log_activity(
            actor=reviewer,
            action=ActivityAction.APPROVED,
            target=submission,
            description=f"Approved with {awarded_points} points",
            comment=comment,
            request=request
        )
        
        return submission
    
    @staticmethod
    @transaction.atomic
    def reject_submission(submission, reviewer, comment, request=None):
        """
        Reject a submission
        """
        if submission.status != SubmissionStatus.SUBMITTED:
            raise ValueError("Only submitted submissions can be rejected")
        
        previous_status = submission.status
        submission.status = SubmissionStatus.REJECTED
        submission.reviewer = reviewer
        submission.review_comment = comment
        submission.reviewed_at = timezone.now()
        submission.save()
        
        Review.objects.create(
            submission=submission,
            reviewer=reviewer,
            action='REJECTED',
            awarded_points=0,
            comment=comment,
            previous_status=previous_status,
            new_status=submission.status
        )
        
        log_activity(
            actor=reviewer,
            action=ActivityAction.REJECTED,
            target=submission,
            description="Rejected submission",
            comment=comment,
            request=request
        )
        
        return submission
    
    @staticmethod
    @transaction.atomic
    def request_revision(submission, reviewer, comment, request=None):
        """
        Request revision on a submission
        """
        if submission.status != SubmissionStatus.SUBMITTED:
            raise ValueError("Only submitted submissions can be sent for revision")
        
        previous_status = submission.status
        submission.status = SubmissionStatus.NEEDS_REVISION
        submission.reviewer = reviewer
        submission.review_comment = comment
        submission.reviewed_at = timezone.now()
        submission.save()
        
        Review.objects.create(
            submission=submission,
            reviewer=reviewer,
            action='NEEDS_REVISION',
            awarded_points=0,
            comment=comment,
            previous_status=previous_status,
            new_status=submission.status
        )
        
        log_activity(
            actor=reviewer,
            action=ActivityAction.NEEDS_REVISION,
            target=submission,
            description="Requested revision",
            comment=comment,
            request=request
        )
        
        return submission
    
    @staticmethod
    @transaction.atomic
    def dean_approve_faculty(faculty, month, year, dean, comment='', request=None):
        """
        Dean gives final approval for a faculty for a specific window
        """
        # Get all HOD-approved submissions for this faculty in this window
        submissions = Submission.objects.filter(
            user=faculty,
            month=month,
            year=year,
            status=SubmissionStatus.HOD_APPROVED
        )
        
        # Calculate total points
        total_points = sum(s.awarded_points for s in submissions)
        
        # Create dean approval record
        dean_approval, created = DeanApproval.objects.update_or_create(
            faculty=faculty,
            month=month,
            year=year,
            defaults={
                'dean': dean,
                'total_points': total_points,
                'comment': comment,
                'is_approved': True
            }
        )
        
        # Update all submissions to DEAN_APPROVED
        submissions.update(
            status=SubmissionStatus.DEAN_APPROVED,
            dean_approved=True,
            dean_approver=dean,
            dean_approved_at=timezone.now()
        )
        
        log_activity(
            actor=dean,
            action=ActivityAction.APPROVED,
            target=dean_approval,
            description=f"Dean approved faculty for {month}/{year} with {total_points} points",
            comment=comment,
            request=request
        )
        
        return dean_approval
