
"""
Submission models - Submissions, field values, and attachments
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.common.models import TimeStampedModel
from apps.common.constants import SubmissionStatus, MONTHS
from apps.common.utils import get_upload_path
import os


class Submission(TimeStampedModel):
    """
    KPI submission by Faculty or HoD
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="User who created this submission"
    )
    sub_parameter = models.ForeignKey(
        'kpi.SubParameter',
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="Sub-parameter this submission is for"
    )
    month = models.IntegerField(
        choices=MONTHS,
        help_text="Month of submission"
    )
    year = models.IntegerField(
        help_text="Year of submission"
    )
    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.CHOICES,
        default=SubmissionStatus.DRAFT,
        help_text="Current status of the submission"
    )
    awarded_points = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Points awarded by reviewer"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_submissions',
        help_text="User who reviewed/approved this submission"
    )
    review_comment = models.TextField(
        blank=True,
        help_text="Comment from reviewer"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the submission was reviewed"
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the submission was submitted (status changed from DRAFT)"
    )
    
    # Dean approval tracking
    dean_approved = models.BooleanField(
        default=False,
        help_text="Whether Dean has given final approval"
    )
    dean_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dean_approved_submissions',
        help_text="Dean who gave final approval"
    )
    dean_approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When Dean approved"
    )
    
    class Meta:
        db_table = 'submissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['sub_parameter', 'month', 'year']),
            models.Index(fields=['status']),
            models.Index(fields=['month', 'year']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        unique_together = [['user', 'sub_parameter', 'month', 'year']]
    
    def __str__(self):
        from apps.common.utils import format_month_year
        return f"{self.user.full_name} - {self.sub_parameter.name} - {format_month_year(self.month, self.year)}"
    
    def can_edit(self):
        """Check if submission can be edited"""
        return self.status in [SubmissionStatus.DRAFT, SubmissionStatus.NEEDS_REVISION]
    
    def can_submit(self):
        """Check if submission can be submitted"""
        return self.status == SubmissionStatus.DRAFT
    
    def can_approve(self):
        """Check if submission can be approved"""
        return self.status == SubmissionStatus.SUBMITTED
    
    def get_main_parameter(self):
        """Get the main parameter"""
        return self.sub_parameter.main_parameter
    
    def get_department(self):
        """Get the user's department"""
        return self.user.department


class SubmissionFieldValue(TimeStampedModel):
    """
    Store values for dynamic form fields
    """
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='field_values',
        help_text="Submission this value belongs to"
    )
    field = models.ForeignKey(
        'forms_builder.DynamicField',
        on_delete=models.CASCADE,
        related_name='values',
        help_text="Dynamic field this value is for"
    )
    field_name = models.CharField(
        max_length=100,
        help_text="Field name (cached for performance)"
    )
    value = models.TextField(
        blank=True,
        help_text="Field value (JSON for complex types)"
    )
    
    class Meta:
        db_table = 'submission_field_values'
        ordering = ['submission', 'field__order']
        indexes = [
            models.Index(fields=['submission']),
            models.Index(fields=['field']),
        ]
        verbose_name = 'Submission Field Value'
        verbose_name_plural = 'Submission Field Values'
        unique_together = [['submission', 'field']]
    
    def __str__(self):
        return f"{self.submission} - {self.field_name}"
    
    def save(self, *args, **kwargs):
        # Cache field name
        if self.field:
            self.field_name = self.field.name
        super().save(*args, **kwargs)


class Attachment(TimeStampedModel):
    """
    File attachments for submissions
    """
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text="Submission this attachment belongs to"
    )
    field = models.ForeignKey(
        'forms_builder.DynamicField',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attachments',
        help_text="Dynamic field this attachment is for"
    )
    file = models.FileField(
        upload_to=get_upload_path,
        help_text="Uploaded file"
    )
    original_name = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    file_size = models.PositiveIntegerField(
        help_text="File size in bytes"
    )
    content_type = models.CharField(
        max_length=100,
        help_text="MIME type of the file"
    )
    
    class Meta:
        db_table = 'attachments'
        ordering = ['submission', '-created_at']
        indexes = [
            models.Index(fields=['submission']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
    
    def __str__(self):
        return f"{self.submission} - {self.original_name}"
    
    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.original_name)[1].lower()
    
    def get_file_size_mb(self):
        """Get file size in MB"""
        return self.file_size / (1024 * 1024)
    
    def delete(self, *args, **kwargs):
        """Delete file from storage when attachment is deleted"""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)
