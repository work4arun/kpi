
"""
Admin configuration for forms builder app
"""
from django.contrib import admin
from apps.forms_builder.models import DynamicFormTemplate, DynamicField


class DynamicFieldInline(admin.TabularInline):
    model = DynamicField
    extra = 1
    fields = ('name', 'label', 'field_type', 'is_required', 'order', 'is_active')


@admin.register(DynamicFormTemplate)
class DynamicFormTemplateAdmin(admin.ModelAdmin):
    list_display = ('sub_parameter', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('sub_parameter__name',)
    inlines = [DynamicFieldInline]
    
    fieldsets = (
        (None, {'fields': ('sub_parameter', 'instructions')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DynamicField)
class DynamicFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'field_type', 'template', 'is_required', 'order', 'is_active')
    list_filter = ('field_type', 'is_required', 'is_active')
    search_fields = ('name', 'label', 'template__sub_parameter__name')
    ordering = ('template', 'order')
    
    fieldsets = (
        (None, {'fields': ('template', 'name', 'label', 'field_type')}),
        ('Configuration', {'fields': ('help_text', 'placeholder', 'is_required', 'order')}),
        ('Field Options', {'fields': ('choices', 'min_value', 'max_value', 'pattern', 'max_length', 'max_files')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
