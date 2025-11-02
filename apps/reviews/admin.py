
"""
Admin configuration for reviews app
"""
from django.contrib import admin
from apps.reviews.models import Review, DeanApproval


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('submission', 'reviewer', 'action', 'awarded_points', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('submission__user__full_name', 'reviewer__full_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('submission', 'reviewer', 'action')}),
        ('Details', {'fields': ('awarded_points', 'comment')}),
        ('Status Change', {'fields': ('previous_status', 'new_status')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeanApproval)
class DeanApprovalAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'month', 'year', 'dean', 'total_points', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'year', 'month')
    search_fields = ('faculty__full_name', 'dean__full_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('faculty', 'month', 'year')}),
        ('Approval', {'fields': ('dean', 'total_points', 'is_approved', 'comment')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
