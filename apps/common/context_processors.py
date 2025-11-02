
"""
Context processors to add common variables to all templates
"""
from apps.notifications.models import Notification


def notification_count(request):
    """
    Add unread notification count to template context
    """
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return {'unread_notification_count': count}
    return {'unread_notification_count': 0}
