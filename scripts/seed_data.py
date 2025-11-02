#!/usr/bin/env python
"""
Comprehensive seed data script for RTC KPI System
Run with: python manage.py shell < scripts/seed_data.py
"""
import os
import django
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtc_kpi.settings')
django.setup()

from django.contrib.auth.models import Group
from django.utils import timezone
from apps.accounts.models import User
from apps.departments.models import Department
from apps.kpi.models import MainParameter, SubParameter, CutoffWindow, HodSubParamMapping
from apps.forms_builder.models import DynamicFormTemplate, DynamicField

print("=" * 50)
print("RTC KPI System - Seed Data Script")
print("=" * 50)

# Create Groups
print("\n1. Creating user groups...")
groups = ['Administrator', 'Faculty', 'Head of Department', 'Dean']
for group_name in groups:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"   ✓ Created group: {group_name}")
    else:
        print(f"   - Group exists: {group_name}")

# Create Departments
print("\n2. Creating departments...")
departments_data = [
    ('CSE', 'Computer Science and Engineering'),
    ('ECE', 'Electronics and Communication Engineering'),
    ('MECH', 'Mechanical Engineering'),
    ('CIVIL', 'Civil Engineering'),
    ('EEE', 'Electrical and Electronics Engineering'),
]

departments = {}
for code, name in departments_data:
    dept, created = Department.objects.get_or_create(
        code=code,
        defaults={'name': name, 'is_active': True}
    )
    departments[code] = dept
    if created:
        print(f"   ✓ Created: {code} - {name}")
    else:
        print(f"   - Exists: {code}")

# Create Admin User
print("\n3. Creating admin user...")
admin, created = User.objects.get_or_create(
    email='admin@rtc.edu',
    defaults={
        'full_name': 'System Administrator',
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print("   ✓ Admin created: admin@rtc.edu / admin123")
else:
    print("   - Admin exists: admin@rtc.edu")

# Create Faculty Users
print("\n4. Creating faculty users...")
faculty_data = [
    ('Dr. Rajesh Kumar', 'rajesh.kumar@rtc.edu', 'CSE', 'F001'),
    ('Dr. Priya Sharma', 'priya.sharma@rtc.edu', 'CSE', 'F002'),
    ('Dr. Amit Patel', 'amit.patel@rtc.edu', 'ECE', 'F003'),
    ('Dr. Sneha Reddy', 'sneha.reddy@rtc.edu', 'ECE', 'F004'),
    ('Dr. Vijay Krishna', 'vijay.krishna@rtc.edu', 'MECH', 'F005'),
    ('Dr. Lakshmi Devi', 'lakshmi.devi@rtc.edu', 'MECH', 'F006'),
]

faculty_users = []
for name, email, dept_code, emp_id in faculty_data:
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'full_name': name,
            'role': 'FACULTY',
            'department': departments[dept_code],
            'employee_id': emp_id,
            'is_active': True
        }
    )
    if created:
        user.set_password('faculty123')
        user.save()
        print(f"   ✓ Created: {name} ({email})")
    else:
        print(f"   - Exists: {name}")
    faculty_users.append(user)

# Create HoD Users
print("\n5. Creating HoD users...")
hod_data = [
    ('Dr. Suresh Babu', 'suresh.babu@rtc.edu', 'CSE', 'H001'),
    ('Dr. Ramesh Kumar', 'ramesh.kumar@rtc.edu', 'ECE', 'H002'),
    ('Dr. Ganesh Iyer', 'ganesh.iyer@rtc.edu', 'MECH', 'H003'),
]

hod_users = []
for name, email, dept_code, emp_id in hod_data:
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'full_name': name,
            'role': 'HOD',
            'department': departments[dept_code],
            'employee_id': emp_id,
            'is_active': True
        }
    )
    if created:
        user.set_password('hod123')
        user.save()
        print(f"   ✓ Created: {name} ({email})")
    else:
        print(f"   - Exists: {name}")
    hod_users.append(user)

# Create Dean User
print("\n6. Creating Dean user...")
dean, created = User.objects.get_or_create(
    email='dean@rtc.edu',
    defaults={
        'full_name': 'Dr. Chandrasekhar',
        'role': 'DEAN',
        'employee_id': 'D001',
        'is_active': True
    }
)
if created:
    dean.set_password('dean123')
    dean.save()
    # Assign all departments to Dean
    dean.dean_departments.set(departments.values())
    print("   ✓ Created: Dean (dean@rtc.edu / dean123)")
else:
    print("   - Exists: Dean")

# Create Main Parameters
print("\n7. Creating main KPI parameters...")
main_params_data = [
    ('Research Publications', 'Publications in journals and conferences', 25, 'FACULTY', 1),
    ('Teaching Excellence', 'Student feedback and course outcomes', 20, 'FACULTY', 2),
    ('Project Guidance', 'Student projects and thesis guidance', 15, 'FACULTY', 3),
    ('Administrative Work', 'Committee memberships and admin duties', 10, 'FACULTY', 4),
    ('Departmental Leadership', 'Leadership and team management', 30, 'HOD', 5),
]

main_params = {}
for name, desc, weightage, role_owner, order in main_params_data:
    param, created = MainParameter.objects.get_or_create(
        name=name,
        defaults={
            'description': desc,
            'weightage': weightage,
            'role_owner': role_owner,
            'is_active': True,
            'order': order
        }
    )
    main_params[name] = param
    if created:
        print(f"   ✓ Created: {name} (Weight: {weightage})")
    else:
        print(f"   - Exists: {name}")

# Create Sub Parameters
print("\n8. Creating sub-parameters...")
sub_params_data = [
    ('Research Publications', 'Journal Paper - SCI/SCIE', 50, 'HOD', None),
    ('Research Publications', 'Conference Paper - International', 30, 'HOD', None),
    ('Research Publications', 'Conference Paper - National', 20, 'HOD', None),
    ('Teaching Excellence', 'Student Feedback Score', 40, 'HOD', None),
    ('Teaching Excellence', 'Course Completion Rate', 30, 'HOD', None),
    ('Project Guidance', 'UG Projects Guided', 20, 'HOD', None),
    ('Project Guidance', 'PG Projects Guided', 30, 'HOD', None),
    ('Administrative Work', 'Committee Participation', 15, 'HOD', None),
    ('Departmental Leadership', 'Faculty Coordination', 50, 'HOD', None),
]

sub_params = {}
for main_name, sub_name, max_points, routing, other_email in sub_params_data:
    param, created = SubParameter.objects.get_or_create(
        main_parameter=main_params[main_name],
        name=sub_name,
        defaults={
            'max_points': max_points,
            'approval_routing': routing,
            'other_approver_email': other_email,
            'is_active': True
        }
    )
    sub_params[sub_name] = param
    if created:
        print(f"   ✓ Created: {sub_name} (Max: {max_points} points)")
    else:
        print(f"   - Exists: {sub_name}")

# Create Dynamic Form Templates
print("\n9. Creating dynamic form templates...")
for sub_param in sub_params.values():
    template, created = DynamicFormTemplate.objects.get_or_create(
        sub_parameter=sub_param,
        defaults={'is_active': True}
    )
    
    if created:
        print(f"   ✓ Created form for: {sub_param.name}")
        
        # Add common fields based on sub-parameter type
        if 'Journal' in sub_param.name or 'Conference' in sub_param.name:
            fields_data = [
                ('paper_title', 'Paper Title', 'text', True, 1),
                ('authors', 'Authors', 'textarea', True, 2),
                ('publication_name', 'Publication/Conference Name', 'text', True, 3),
                ('publication_date', 'Publication Date', 'date', True, 4),
                ('doi_url', 'DOI/URL', 'url', False, 5),
                ('proof_file', 'Upload Proof', 'file', True, 6),
            ]
        elif 'Project' in sub_param.name:
            fields_data = [
                ('student_name', 'Student Name(s)', 'textarea', True, 1),
                ('project_title', 'Project Title', 'text', True, 2),
                ('project_description', 'Description', 'textarea', True, 3),
                ('completion_date', 'Completion Date', 'date', True, 4),
                ('proof_file', 'Upload Proof', 'file', True, 5),
            ]
        else:
            fields_data = [
                ('activity_description', 'Activity Description', 'textarea', True, 1),
                ('date', 'Date', 'date', True, 2),
                ('proof_file', 'Upload Proof', 'file', False, 3),
            ]
        
        for field_name, label, field_type, required, order in fields_data:
            DynamicField.objects.create(
                template=template,
                name=field_name,
                label=label,
                field_type=field_type,
                is_required=required,
                order=order,
                is_active=True
            )

# Create Cutoff Windows
print("\n10. Creating cutoff windows...")
current_date = timezone.now()
current_month = current_date.month
current_year = current_date.year

for i in range(3):  # Create 3 months of windows
    month = current_month - i
    year = current_year
    if month <= 0:
        month += 12
        year -= 1
    
    faculty_deadline = current_date + timedelta(days=30-i*30)
    hod_deadline = faculty_deadline + timedelta(days=7)
    dean_deadline = hod_deadline + timedelta(days=7)
    
    window, created = CutoffWindow.objects.get_or_create(
        month=month,
        year=year,
        defaults={
            'faculty_submit_deadline': faculty_deadline,
            'hod_approve_deadline': hod_deadline,
            'dean_approve_deadline': dean_deadline,
            'is_active': True
        }
    )
    if created:
        print(f"   ✓ Created cutoff window: {month}/{year}")
    else:
        print(f"   - Exists: {month}/{year}")

print("\n" + "=" * 50)
print("Seed Data Creation Complete!")
print("=" * 50)
print("\nDefault Credentials:")
print("-" * 50)
print("Admin:   admin@rtc.edu / admin123")
print("Dean:    dean@rtc.edu / dean123")
print("HoD:     suresh.babu@rtc.edu / hod123 (CSE)")
print("         ramesh.kumar@rtc.edu / hod123 (ECE)")
print("Faculty: rajesh.kumar@rtc.edu / faculty123")
print("         priya.sharma@rtc.edu / faculty123")
print("-" * 50)
print("\nYou can now login to the system!")
print("=" * 50)
