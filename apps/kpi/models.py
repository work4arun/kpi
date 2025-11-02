
"""
KPI models - Main parameters, sub-parameters, HOD mappings, and cutoff windows
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TimeStampedModel
from apps.common.constants import RoleOwner, ApprovalRouting, AggregationType, MONTHS


class MainParameter(TimeStampedModel):
    """
    Main KPI parameter category
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the main parameter"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the main parameter"
    )
    weightage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0)],
        help_text="Weightage or percentage for this parameter"
    )
    role_owner = models.CharField(
        max_length=20,
        choices=RoleOwner.CHOICES,
        default=RoleOwner.FACULTY,
        help_text="Who owns this parameter (Faculty or HoD)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this parameter is active"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )
    
    class Meta:
        db_table = 'main_parameters'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'order']),
            models.Index(fields=['role_owner']),
        ]
        verbose_name = 'Main Parameter'
        verbose_name_plural = 'Main Parameters'
    
    def __str__(self):
        return f"{self.name} ({self.get_role_owner_display()})"
    
    def get_total_max_points(self):
        """Calculate total max points from all sub-parameters"""
        return self.sub_parameters.filter(is_active=True).aggregate(
            total=models.Sum('max_points')
        )['total'] or 0


class SubParameter(TimeStampedModel):
    """
    Sub-parameter under a main parameter
    """
    main_parameter = models.ForeignKey(
        MainParameter,
        on_delete=models.CASCADE,
        related_name='sub_parameters',
        help_text="Parent main parameter"
    )
    name = models.CharField(
        max_length=255,
        help_text="Name of the sub-parameter"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the sub-parameter"
    )
    max_points = models.PositiveIntegerField(
        help_text="Maximum effort coins/points for this sub-parameter"
    )
    approval_routing = models.CharField(
        max_length=20,
        choices=ApprovalRouting.CHOICES,
        default=ApprovalRouting.HOD,
        help_text="Routing for approval (HoD or Other)"
    )
    other_approver_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email of other approver (if routing is OTHER)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this sub-parameter is active"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )
    
    class Meta:
        db_table = 'sub_parameters'
        ordering = ['main_parameter', 'order', 'name']
        indexes = [
            models.Index(fields=['main_parameter', 'is_active']),
            models.Index(fields=['approval_routing']),
        ]
        verbose_name = 'Sub Parameter'
        verbose_name_plural = 'Sub Parameters'
        unique_together = [['main_parameter', 'name']]
    
    def __str__(self):
        return f"{self.main_parameter.name} > {self.name}"
    
    def get_role_owner(self):
        """Get role owner from main parameter"""
        return self.main_parameter.role_owner


class HodSubParamMapping(TimeStampedModel):
    """
    Mapping between HoD sub-parameters and Faculty sub-parameters
    for team average calculation
    """
    hod_subparam = models.ForeignKey(
        SubParameter,
        on_delete=models.CASCADE,
        related_name='hod_mappings',
        limit_choices_to={'main_parameter__role_owner': RoleOwner.HOD},
        help_text="HoD sub-parameter"
    )
    faculty_subparam = models.ForeignKey(
        SubParameter,
        on_delete=models.CASCADE,
        related_name='faculty_mappings',
        limit_choices_to={'main_parameter__role_owner': RoleOwner.FACULTY},
        help_text="Corresponding Faculty sub-parameter"
    )
    aggregation = models.CharField(
        max_length=20,
        choices=AggregationType.CHOICES,
        default=AggregationType.AVERAGE,
        help_text="Aggregation type"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this mapping is active"
    )
    
    class Meta:
        db_table = 'hod_subparam_mappings'
        ordering = ['hod_subparam']
        indexes = [
            models.Index(fields=['hod_subparam', 'is_active']),
            models.Index(fields=['faculty_subparam']),
        ]
        verbose_name = 'HOD Sub-Parameter Mapping'
        verbose_name_plural = 'HOD Sub-Parameter Mappings'
        unique_together = [['hod_subparam', 'faculty_subparam']]
    
    def __str__(self):
        return f"HOD: {self.hod_subparam.name} <- Faculty: {self.faculty_subparam.name}"


class CutoffWindow(TimeStampedModel):
    """
    Cut-off window with deadlines for submissions and approvals
    """
    month = models.IntegerField(
        choices=MONTHS,
        help_text="Month for this cutoff window"
    )
    year = models.IntegerField(
        help_text="Year for this cutoff window"
    )
    faculty_submit_deadline = models.DateTimeField(
        help_text="Deadline for faculty to submit"
    )
    hod_approve_deadline = models.DateTimeField(
        help_text="Deadline for HoD to approve"
    )
    dean_approve_deadline = models.DateTimeField(
        help_text="Deadline for Dean to give final approval"
    )
    departments = models.ManyToManyField(
        'departments.Department',
        blank=True,
        related_name='cutoff_windows',
        help_text="Departments this window applies to (blank = all departments)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this cutoff window is active"
    )
    
    class Meta:
        db_table = 'cutoff_windows'
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['month', 'year', 'is_active']),
            models.Index(fields=['-year', '-month']),
        ]
        verbose_name = 'Cutoff Window'
        verbose_name_plural = 'Cutoff Windows'
        unique_together = [['month', 'year']]
    
    def __str__(self):
        from apps.common.utils import format_month_year
        return f"{format_month_year(self.month, self.year)} - Cutoff Window"
    
    @classmethod
    def get_active_window(cls, month, year, department=None):
        """
        Get active cutoff window for given month/year and optional department
        """
        query = cls.objects.filter(month=month, year=year, is_active=True)
        
        if department:
            # Get windows that include this department or apply to all departments
            query = query.filter(
                models.Q(departments=department) | models.Q(departments__isnull=True)
            ).distinct()
        
        return query.first()
    
    def applies_to_department(self, department):
        """
        Check if this window applies to the given department
        """
        if not self.departments.exists():
            return True  # Applies to all departments
        return department in self.departments.all()


class SubParameterWindow(models.Model):
    """
    Many-to-many relationship between SubParameters and CutoffWindows
    to enable/disable sub-parameters per window
    """
    sub_parameter = models.ForeignKey(
        SubParameter,
        on_delete=models.CASCADE,
        related_name='window_associations'
    )
    cutoff_window = models.ForeignKey(
        CutoffWindow,
        on_delete=models.CASCADE,
        related_name='subparam_associations'
    )
    is_enabled = models.BooleanField(
        default=True,
        help_text="Whether this sub-parameter is enabled for this window"
    )
    
    class Meta:
        db_table = 'subparameter_windows'
        unique_together = [['sub_parameter', 'cutoff_window']]
        verbose_name = 'Sub-Parameter Window'
        verbose_name_plural = 'Sub-Parameter Windows'
    
    def __str__(self):
        return f"{self.sub_parameter.name} - {self.cutoff_window}"
