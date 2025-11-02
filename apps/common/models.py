
"""
Common models - Activity Log for audit trail
"""
from django.db import models
from django.conf import settings
from apps.common.constants import ActivityAction


class ActivityLog(models.Model):
    """
    Audit log for tracking all significant actions in the system
    """
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
        help_text="User who performed the action"
    )
    action = models.CharField(
        max_length=50,
        choices=ActivityAction.CHOICES,
        help_text="Type of action performed"
    )
    target_model = models.CharField(
        max_length=100,
        help_text="Model name of the target object"
    )
    target_id = models.PositiveIntegerField(
        help_text="ID of the target object"
    )
    description = models.TextField(
        help_text="Human-readable description of the action"
    )
    comment = models.TextField(
        blank=True,
        help_text="Additional comments or notes"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the action"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the actor"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was performed"
    )
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['actor', '-created_at']),
            models.Index(fields=['target_model', 'target_id']),
        ]
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
    
    def __str__(self):
        actor_name = self.actor.full_name if self.actor else 'System'
        return f"{actor_name} - {self.get_action_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class TimeStampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at fields
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
