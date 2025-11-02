
"""
Constants used throughout the RTC KPI System
"""

# User Roles
class UserRole:
    ADMIN = 'ADMIN'
    FACULTY = 'FACULTY'
    HOD = 'HOD'
    DEAN = 'DEAN'
    
    CHOICES = [
        (ADMIN, 'Administrator'),
        (FACULTY, 'Faculty'),
        (HOD, 'Head of Department'),
        (DEAN, 'Dean'),
    ]


# Submission Statuses
class SubmissionStatus:
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    NEEDS_REVISION = 'NEEDS_REVISION'
    HOD_APPROVED = 'HOD_APPROVED'
    DEAN_APPROVED = 'DEAN_APPROVED'
    REJECTED = 'REJECTED'
    
    CHOICES = [
        (DRAFT, 'Draft'),
        (SUBMITTED, 'Submitted'),
        (NEEDS_REVISION, 'Needs Revision'),
        (HOD_APPROVED, 'HoD Approved'),
        (DEAN_APPROVED, 'Dean Approved'),
        (REJECTED, 'Rejected'),
    ]


# Role Owner (for KPI Parameters)
class RoleOwner:
    FACULTY = 'FACULTY'
    HOD = 'HOD'
    
    CHOICES = [
        (FACULTY, 'Faculty'),
        (HOD, 'Head of Department'),
    ]


# Approval Routing
class ApprovalRouting:
    HOD = 'HOD'
    OTHER = 'OTHER'
    
    CHOICES = [
        (HOD, 'HoD Approval'),
        (OTHER, 'Other Approver'),
    ]


# Dynamic Field Types
class FieldType:
    TEXT = 'text'
    TEXTAREA = 'textarea'
    NUMBER = 'number'
    PERCENTAGE = 'percentage'
    DATE = 'date'
    URL = 'url'
    SELECT = 'select'
    MULTISELECT = 'multiselect'
    FILE = 'file'
    MULTIFILE = 'multifile'
    
    CHOICES = [
        (TEXT, 'Text'),
        (TEXTAREA, 'Text Area'),
        (NUMBER, 'Number'),
        (PERCENTAGE, 'Percentage'),
        (DATE, 'Date'),
        (URL, 'URL'),
        (SELECT, 'Select'),
        (MULTISELECT, 'Multi Select'),
        (FILE, 'File Upload'),
        (MULTIFILE, 'Multiple Files'),
    ]


# Activity Log Actions
class ActivityAction:
    CREATED = 'CREATED'
    SUBMITTED = 'SUBMITTED'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    NEEDS_REVISION = 'NEEDS_REVISION'
    UPDATED = 'UPDATED'
    DELETED = 'DELETED'
    
    CHOICES = [
        (CREATED, 'Created'),
        (SUBMITTED, 'Submitted'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (NEEDS_REVISION, 'Needs Revision'),
        (UPDATED, 'Updated'),
        (DELETED, 'Deleted'),
    ]


# Aggregation Types for HOD Mapping
class AggregationType:
    AVERAGE = 'AVERAGE'
    
    CHOICES = [
        (AVERAGE, 'Average'),
    ]


# Months
MONTHS = [
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),
]


# File Upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.zip']
