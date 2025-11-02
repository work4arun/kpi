
"""
Admin configuration for common app
"""
from django.contrib import admin
from apps.common.models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'target_model', 'target_id', 'created_at')
    list_filter = ('action', 'target_model', 'created_at')
    search_fields = ('actor__full_name', 'description', 'comment')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Action Info', {'fields': ('actor', 'action', 'description')}),
        ('Target', {'fields': ('target_model', 'target_id')}),
        ('Details', {'fields': ('comment', 'metadata', 'ip_address')}),
        ('Timestamp', {'fields': ('created_at',)}),
    )
    
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
