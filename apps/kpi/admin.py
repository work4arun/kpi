
"""
Admin configuration for KPI app
"""
from django.contrib import admin
from apps.kpi.models import MainParameter, SubParameter, HodSubParamMapping, CutoffWindow, SubParameterWindow


class SubParameterInline(admin.TabularInline):
    model = SubParameter
    extra = 1
    fields = ('name', 'max_points', 'approval_routing', 'other_approver_email', 'is_active', 'order')


@admin.register(MainParameter)
class MainParameterAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_owner', 'weightage', 'is_active', 'order')
    list_filter = ('role_owner', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    inlines = [SubParameterInline]
    
    fieldsets = (
        (None, {'fields': ('name', 'description', 'role_owner')}),
        ('Scoring', {'fields': ('weightage', 'order')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SubParameter)
class SubParameterAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_parameter', 'max_points', 'approval_routing', 'is_active', 'order')
    list_filter = ('main_parameter', 'approval_routing', 'is_active')
    search_fields = ('name', 'description', 'main_parameter__name')
    ordering = ('main_parameter', 'order', 'name')
    
    fieldsets = (
        (None, {'fields': ('main_parameter', 'name', 'description')}),
        ('Scoring & Routing', {'fields': ('max_points', 'approval_routing', 'other_approver_email')}),
        ('Display', {'fields': ('order', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(HodSubParamMapping)
class HodSubParamMappingAdmin(admin.ModelAdmin):
    list_display = ('hod_subparam', 'faculty_subparam', 'aggregation', 'is_active')
    list_filter = ('aggregation', 'is_active')
    search_fields = ('hod_subparam__name', 'faculty_subparam__name')
    
    fieldsets = (
        (None, {'fields': ('hod_subparam', 'faculty_subparam', 'aggregation')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CutoffWindow)
class CutoffWindowAdmin(admin.ModelAdmin):
    list_display = ('month', 'year', 'faculty_submit_deadline', 'hod_approve_deadline', 'dean_approve_deadline', 'is_active')
    list_filter = ('year', 'month', 'is_active')
    search_fields = ('month', 'year')
    ordering = ('-year', '-month')
    filter_horizontal = ('departments',)
    
    fieldsets = (
        ('Period', {'fields': ('month', 'year')}),
        ('Deadlines', {'fields': ('faculty_submit_deadline', 'hod_approve_deadline', 'dean_approve_deadline')}),
        ('Scope', {'fields': ('departments', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SubParameterWindow)
class SubParameterWindowAdmin(admin.ModelAdmin):
    list_display = ('sub_parameter', 'cutoff_window', 'is_enabled')
    list_filter = ('is_enabled', 'cutoff_window')
    search_fields = ('sub_parameter__name',)
