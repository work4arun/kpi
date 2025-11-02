
"""
Service layer for notification management
"""
from django.urls import reverse
from apps.notifications.models import Notification


class NotificationService:
    """
    Service for creating and managing notifications
    """
    
    @staticmethod
    def create_notification(recipient, title, message, link='', notification_type='info', related_submission=None):
        """
        Create a new notification
        """
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            link=link,
            notification_type=notification_type,
            related_submission=related_submission
        )
    
    @staticmethod
    def notify_submission_submitted(submission, reviewer):
        """
        Notify reviewer when submission is submitted
        """
        title = "New Submission for Review"
        message = f"{submission.user.full_name} submitted a KPI entry for {submission.sub_parameter.name}"
        link = reverse('reviews:review_detail', kwargs={'pk': submission.id})
        
        return NotificationService.create_notification(
            recipient=reviewer,
            title=title,
            message=message,
            link=link,
            notification_type='info',
            related_submission=submission
        )
    
    @staticmethod
    def notify_submission_needs_revision(submission):
        """
        Notify faculty when submission needs revision
        """
        title = "Revision Requested"
        message = f"Your submission for {submission.sub_parameter.name} needs revision. Comment: {submission.review_comment}"
        link = reverse('submissions:submission_detail', kwargs={'pk': submission.id})
        
        return NotificationService.create_notification(
            recipient=submission.user,
            title=title,
            message=message,
            link=link,
            notification_type='warning',
            related_submission=submission
        )
    
    @staticmethod
    def notify_submission_hod_approved(submission, dean):
        """
        Notify dean when submission is approved by HoD
        """
        title = "Submission Approved by HoD"
        message = f"{submission.user.full_name}'s submission for {submission.sub_parameter.name} has been approved by HoD with {submission.awarded_points} points"
        link = reverse('reviews:dean_review_list')
        
        return NotificationService.create_notification(
            recipient=dean,
            title=title,
            message=message,
            link=link,
            notification_type='info',
            related_submission=submission
        )
    
    @staticmethod
    def notify_submission_dean_approved(submission):
        """
        Notify faculty when submission is approved by Dean
        """
        title = "Final Approval Received"
        message = f"Your submission for {submission.sub_parameter.name} has been given final approval by Dean"
        link = reverse('submissions:submission_detail', kwargs={'pk': submission.id})
        
        # Notify faculty
        NotificationService.create_notification(
            recipient=submission.user,
            title=title,
            message=message,
            link=link,
            notification_type='success',
            related_submission=submission
        )
        
        # Also notify HoD
        if submission.user.department:
            hod = submission.user.department.get_hod()
            if hod:
                NotificationService.create_notification(
                    recipient=hod,
                    title=title,
                    message=f"{submission.user.full_name}'s submission for {submission.sub_parameter.name} has been given final approval",
                    link=link,
                    notification_type='success',
                    related_submission=submission
                )
    
    @staticmethod
    def notify_submission_rejected(submission):
        """
        Notify faculty when submission is rejected
        """
        title = "Submission Rejected"
        message = f"Your submission for {submission.sub_parameter.name} has been rejected. Comment: {submission.review_comment}"
        link = reverse('submissions:submission_detail', kwargs={'pk': submission.id})
        
        return NotificationService.create_notification(
            recipient=submission.user,
            title=title,
            message=message,
            link=link,
            notification_type='error',
            related_submission=submission
        )
    
    @staticmethod
    def mark_all_as_read(user):
        """
        Mark all notifications as read for a user
        """
        from django.utils import timezone
        Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
