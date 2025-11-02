
"""
Department models - Flat department structure
"""
from django.db import models
from apps.common.models import TimeStampedModel


class Department(TimeStampedModel):
    """
    Department model - Flat structure (no hierarchy)
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Department code (e.g., CSE, ECE, MECH)"
    )
    name = models.CharField(
        max_length=255,
        help_text="Department name (e.g., Computer Science Engineering)"
    )
    description = models.TextField(
        blank=True,
        help_text="Department description"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the department is active"
    )
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_faculty_count(self):
        """Get number of faculty in this department"""
        return self.users.filter(role='FACULTY', is_active=True).count()
    
    def get_hod(self):
        """Get HoD for this department"""
        return self.users.filter(role='HOD', is_active=True).first()
