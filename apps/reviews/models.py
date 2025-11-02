
"""
Review models - Approval workflow tracking
"""
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class Review(TimeStampedModel):
    """
    Review/Approval record for submissions
    Tracks the approval workflow history
    """
    submission = models.ForeignKey(
        'submissions.Submission',
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Submission being reviewed"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        help_text="User who performed the review"
    )
    action = models.CharField(
        max_length=50,
        help_text="Action taken (APPROVED, REJECTED, NEEDS_REVISION)"
    )
    awarded_points = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Points awarded (if approved)"
    )
    comment = models.TextField(
        blank=True,
        help_text="Reviewer's comment"
    )
    previous_status = models.CharField(
        max_length=20,
        help_text="Status before this review"
    )
    new_status = models.CharField(
        max_length=20,
        help_text="Status after this review"
    )
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['submission', '-created_at']),
            models.Index(fields=['reviewer', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        return f"{self.reviewer.full_name} - {self.action} - {self.submission}"


class DeanApproval(TimeStampedModel):
    """
    Dean's final approval for a faculty member for a specific window
    One approval per faculty per window
    """
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dean_approvals',
        limit_choices_to={'role': 'FACULTY'},
        help_text="Faculty being approved"
    )
    month = models.IntegerField(
        help_text="Month of approval"
    )
    year = models.IntegerField(
        help_text="Year of approval"
    )
    dean = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dean_approvals_given',
        limit_choices_to={'role': 'DEAN'},
        help_text="Dean who approved"
    )
    total_points = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total points for this faculty for this window"
    )
    comment = models.TextField(
        blank=True,
        help_text="Dean's comment"
    )
    is_approved = models.BooleanField(
        default=True,
        help_text="Whether approved or rejected"
    )
    
    class Meta:
        db_table = 'dean_approvals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['faculty', 'month', 'year']),
            models.Index(fields=['dean', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Dean Approval'
        verbose_name_plural = 'Dean Approvals'
        unique_together = [['faculty', 'month', 'year']]
    
    def __str__(self):
        from apps.common.utils import format_month_year
        return f"Dean approval: {self.faculty.full_name} - {format_month_year(self.month, self.year)}"
