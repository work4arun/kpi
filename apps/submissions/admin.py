
"""
Admin configuration for submissions app
"""
from django.contrib import admin
from apps.submissions.models import Submission, SubmissionFieldValue, Attachment


class SubmissionFieldValueInline(admin.TabularInline):
    model = SubmissionFieldValue
    extra = 0
    readonly_fields = ('field', 'field_name', 'value')
    can_delete = False


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('file', 'original_name', 'file_size', 'content_type', 'created_at')
    can_delete = False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'sub_parameter', 'month', 'year', 'status', 'awarded_points', 'submitted_at', 'created_at')
    list_filter = ('status', 'month', 'year', 'sub_parameter__main_parameter')
    search_fields = ('user__full_name', 'user__email', 'sub_parameter__name')
    ordering = ('-created_at',)
    inlines = [SubmissionFieldValueInline, AttachmentInline]
    
    fieldsets = (
        ('Submission Info', {'fields': ('user', 'sub_parameter', 'month', 'year', 'status')}),
        ('Review Info', {'fields': ('reviewer', 'awarded_points', 'review_comment', 'reviewed_at')}),
        ('Dean Approval', {'fields': ('dean_approved', 'dean_approver', 'dean_approved_at')}),
        ('Timestamps', {'fields': ('submitted_at', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'submitted_at', 'reviewed_at', 'dean_approved_at')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('submission', 'original_name', 'file_size', 'content_type', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('submission__user__full_name', 'original_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
