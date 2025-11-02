
"""
Service layer for submission management
"""
from django.db import transaction
from django.utils import timezone
from apps.submissions.models import Submission, SubmissionFieldValue, Attachment
from apps.common.constants import SubmissionStatus, ActivityAction
from apps.common.utils import log_activity, check_cutoff_deadline
from apps.kpi.models import CutoffWindow
import json


class SubmissionService:
    """
    Service for handling submission operations
    """
    
    @staticmethod
    def create_submission(user, sub_parameter, month, year):
        """
        Create a new submission (or get existing draft)
        """
        submission, created = Submission.objects.get_or_create(
            user=user,
            sub_parameter=sub_parameter,
            month=month,
            year=year,
            defaults={'status': SubmissionStatus.DRAFT}
        )
        
        if created:
            log_activity(
                actor=user,
                action=ActivityAction.CREATED,
                target=submission,
                description=f"Created submission for {sub_parameter.name}"
            )
        
        return submission
    
    @staticmethod
    @transaction.atomic
    def save_submission_data(submission, form_data, files=None, request=None):
        """
        Save submission field values and attachments
        """
        # Get form template
        if not hasattr(submission.sub_parameter, 'form_template'):
            raise ValueError("No form template defined for this sub-parameter")
        
        template = submission.sub_parameter.form_template
        fields = template.get_fields_ordered()
        
        # Save field values
        for field in fields:
            value = form_data.get(field.name, '')
            
            # Skip file fields (handled separately)
            if field.field_type in ['file', 'multifile']:
                continue
            
            # Convert complex values to JSON
            if field.field_type in ['multiselect'] and isinstance(value, list):
                value = json.dumps(value)
            
            # Save or update field value
            SubmissionFieldValue.objects.update_or_create(
                submission=submission,
                field=field,
                defaults={
                    'value': value,
                    'field_name': field.name
                }
            )
        
        # Handle file uploads
        if files:
            for field in fields:
                if field.field_type in ['file', 'multifile']:
                    uploaded_files = files.getlist(field.name) if field.field_type == 'multifile' else [files.get(field.name)]
                    
                    for uploaded_file in uploaded_files:
                        if uploaded_file:
                            Attachment.objects.create(
                                submission=submission,
                                field=field,
                                file=uploaded_file,
                                original_name=uploaded_file.name,
                                file_size=uploaded_file.size,
                                content_type=uploaded_file.content_type
                            )
        
        # Update submission timestamp
        submission.updated_at = timezone.now()
        submission.save()
        
        log_activity(
            actor=submission.user,
            action=ActivityAction.UPDATED,
            target=submission,
            description="Updated submission data",
            request=request
        )
        
        return submission
    
    @staticmethod
    @transaction.atomic
    def submit_submission(submission, request=None):
        """
        Submit a draft submission for review
        """
        if submission.status != SubmissionStatus.DRAFT:
            raise ValueError("Only draft submissions can be submitted")
        
        # Check cutoff deadline
        cutoff_window = CutoffWindow.get_active_window(
            submission.month,
            submission.year,
            submission.user.department
        )
        
        if cutoff_window and not submission.user.can_override_deadlines:
            is_within, _ = check_cutoff_deadline(cutoff_window, submission.user.role)
            if not is_within:
                raise ValueError("Submission deadline has passed")
        
        # Update status
        submission.status = SubmissionStatus.SUBMITTED
        submission.submitted_at = timezone.now()
        submission.save()
        
        log_activity(
            actor=submission.user,
            action=ActivityAction.SUBMITTED,
            target=submission,
            description=f"Submitted for review",
            request=request
        )
        
        return submission
    
    @staticmethod
    def can_edit_submission(submission, user):
        """
        Check if user can edit this submission
        """
        # User must be the owner
        if submission.user != user:
            return False
        
        # Can only edit drafts or revisions
        if submission.status not in [SubmissionStatus.DRAFT, SubmissionStatus.NEEDS_REVISION]:
            return False
        
        return True
    
    @staticmethod
    def get_user_submissions(user, filters=None):
        """
        Get submissions for a user with optional filters
        """
        queryset = Submission.objects.filter(user=user).select_related(
            'sub_parameter', 'sub_parameter__main_parameter', 'reviewer'
        ).order_by('-created_at')
        
        if filters:
            if 'status' in filters and filters['status']:
                queryset = queryset.filter(status=filters['status'])
            if 'month' in filters and filters['month']:
                queryset = queryset.filter(month=filters['month'])
            if 'year' in filters and filters['year']:
                queryset = queryset.filter(year=filters['year'])
            if 'main_parameter' in filters and filters['main_parameter']:
                queryset = queryset.filter(sub_parameter__main_parameter=filters['main_parameter'])
        
        return queryset
