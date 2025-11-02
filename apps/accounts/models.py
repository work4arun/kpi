
"""
User model and related models for authentication and authorization
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator
from apps.common.constants import UserRole
from apps.common.models import TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom User model using email as the unique identifier
    """
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="User's email address (used for login)"
    )
    full_name = models.CharField(
        max_length=255,
        help_text="User's full name"
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.FACULTY,
        help_text="User's role in the system"
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="Primary department (for Faculty and HoD)"
    )
    dean_departments = models.ManyToManyField(
        'departments.Department',
        blank=True,
        related_name='deans',
        help_text="Departments managed by Dean"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the user account is active"
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Whether the user can access admin site"
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last login timestamp"
    )
    
    # Profile fields
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
    )
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        null=True,
        help_text="Employee ID"
    )
    joining_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of joining"
    )
    
    # Override flags for deadline enforcement
    can_override_deadlines = models.BooleanField(
        default=False,
        help_text="Can submit/approve after deadlines"
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    
    def get_full_name(self):
        return self.full_name
    
    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser
    
    @property
    def is_faculty(self):
        return self.role == UserRole.FACULTY
    
    @property
    def is_hod(self):
        return self.role == UserRole.HOD
    
    @property
    def is_dean(self):
        return self.role == UserRole.DEAN
    
    def get_managed_departments(self):
        """
        Get departments managed by this user based on role
        """
        if self.is_admin:
            from apps.departments.models import Department
            return Department.objects.all()
        elif self.is_dean:
            return self.dean_departments.all()
        elif self.is_hod and self.department:
            return [self.department]
        return []
    
    def can_view_department(self, department):
        """
        Check if user can view data for a specific department
        """
        if self.is_admin:
            return True
        elif self.is_dean:
            return department in self.dean_departments.all()
        elif self.is_hod:
            return self.department == department
        elif self.is_faculty:
            return self.department == department
        return False
