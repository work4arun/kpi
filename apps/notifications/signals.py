
"""
Signals for creating notifications based on submission events
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.submissions.models import Submission
from apps.common.constants import SubmissionStatus


@receiver(post_save, sender=Submission)
def create_submission_notifications(sender, instance, created, **kwargs):
    """
    Create notifications when submission status changes
    """
    from apps.notifications.services import NotificationService
    
    # Don't create notifications for draft submissions
    if instance.status == SubmissionStatus.DRAFT:
        return
    
    # SUBMITTED - notify reviewer (HoD or OTHER)
    if instance.status == SubmissionStatus.SUBMITTED:
        if instance.sub_parameter.approval_routing == 'HOD':
            # Notify HoD of the department
            if instance.user.department:
                hod = instance.user.department.get_hod()
                if hod:
                    NotificationService.notify_submission_submitted(instance, hod)
        else:
            # Notify OTHER approver
            if instance.sub_parameter.other_approver_email:
                from apps.accounts.models import User
                try:
                    approver = User.objects.get(
                        email=instance.sub_parameter.other_approver_email,
                        is_active=True
                    )
                    NotificationService.notify_submission_submitted(instance, approver)
                except User.DoesNotExist:
                    pass
    
    # NEEDS_REVISION - notify faculty
    elif instance.status == SubmissionStatus.NEEDS_REVISION:
        NotificationService.notify_submission_needs_revision(instance)
    
    # HOD_APPROVED - notify Dean
    elif instance.status == SubmissionStatus.HOD_APPROVED:
        # Notify all deans who manage this department
        if instance.user.department:
            deans = instance.user.department.deans.filter(is_active=True)
            for dean in deans:
                NotificationService.notify_submission_hod_approved(instance, dean)
    
    # DEAN_APPROVED - notify faculty and HoD
    elif instance.status == SubmissionStatus.DEAN_APPROVED:
        NotificationService.notify_submission_dean_approved(instance)
    
    # REJECTED - notify faculty
    elif instance.status == SubmissionStatus.REJECTED:
        NotificationService.notify_submission_rejected(instance)
