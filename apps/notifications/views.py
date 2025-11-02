
"""
Views for notifications app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


@login_required
def notification_list(request):
    """List user's notifications"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:50]
    
    # Mark as read if requested
    if request.GET.get('mark_read') == 'all':
        NotificationService.mark_all_as_read(request.user)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:notification_list')
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def notification_detail(request, pk):
    """View notification detail and mark as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    
    # Mark as read
    notification.mark_as_read()
    
    # Redirect to linked resource if available
    if notification.link:
        return redirect(notification.link)
    
    context = {'notification': notification}
    return render(request, 'notifications/notification_detail.html', context)


@login_required
def notification_mark_read(request, pk):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    messages.success(request, 'Notification marked as read.')
    return redirect('notifications:notification_list')
