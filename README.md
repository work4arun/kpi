# RTC KPI System

**Rathinam Technical Campus - KPI Management System**

A comprehensive Django web application for managing Key Performance Indicators (KPI) for faculty and administrators at Rathinam Technical Campus.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [User Roles](#user-roles)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Core Functionality
- ✅ **Multi-Role System**: Admin, Faculty, HoD, and Dean roles with role-based access control
- ✅ **Dynamic Form Builder**: Admin can create custom forms for each KPI sub-parameter
- ✅ **Multi-Stage Approval Workflow**: Faculty → HoD → Dean approval process
- ✅ **HOD Team Average Calculation**: HOD scores include department team averages
- ✅ **Cut-off Window Management**: Deadline enforcement for submissions and approvals
- ✅ **In-App Notifications**: Real-time web notifications (no email required)
- ✅ **File Upload Support**: 10MB limit with validation for multiple file types
- ✅ **CSV Import/Export**: Bulk user creation and results export
- ✅ **Department-wise Analytics**: Comprehensive dashboards with Chart.js visualizations
- ✅ **Activity Logging**: Complete audit trail of all actions

### Dashboards
- **Faculty Dashboard**: Personal KPI scores, submission history, trend analysis
- **HoD Dashboard**: Department overview, pending approvals, team performance
- **Dean Dashboard**: Multi-department comparison, faculty leaderboard, consolidated analytics
- **Admin Dashboard**: System-wide statistics, department comparison, configuration management

### Security Features
- CSRF protection
- File type and size validation
- Role-based permissions
- Secure password hashing
- Activity logging with IP tracking

---

## 🛠 Tech Stack

- **Backend**: Python 3.11, Django 5.0
- **Database**: PostgreSQL 16
- **Frontend**: Django Templates, Tailwind CSS (CDN), Chart.js (CDN)
- **Containerization**: Docker, Docker Compose
- **WSGI Server**: Gunicorn
- **Testing**: pytest, pytest-django

---

## 📦 System Requirements

- Docker (20.10+)
- Docker Compose (2.0+)
- Git

Or for local development:
- Python 3.11+
- PostgreSQL 16+
- pip

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd rtc_kpi_system

# 2. Copy environment file
cp .env.example .env

# 3. Build and start containers
docker compose up --build

# 4. In a new terminal, run migrations
docker compose exec web python manage.py migrate

# 5. Create superuser
docker compose exec web python manage.py createsuperuser

# 6. Load seed data
docker compose exec web python manage.py shell < scripts/seed_data.py

# 7. Access the application
# Open browser: http://localhost:8000
```

### Default Credentials (After Seed Data)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@rtc.edu | admin123 |
| Dean | dean@rtc.edu | dean123 |
| HoD (CSE) | suresh.babu@rtc.edu | hod123 |
| HoD (ECE) | ramesh.kumar@rtc.edu | hod123 |
| Faculty | rajesh.kumar@rtc.edu | faculty123 |
| Faculty | priya.sharma@rtc.edu | faculty123 |

⚠️ **Change these passwords in production!**

---

## 📖 Detailed Setup

### 1. Environment Configuration

Edit `.env` file with your configuration:

```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=rtc_kpi_db
DB_USER=rtc_user
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432

# Timezone
TIME_ZONE=Asia/Kolkata

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### 2. Database Migrations

```bash
# Create migrations
docker compose exec web python manage.py makemigrations

# Apply migrations
docker compose exec web python manage.py migrate

# Verify migrations
docker compose exec web python manage.py showmigrations
```

### 3. Static Files

```bash
# Collect static files (for production)
docker compose exec web python manage.py collectstatic --noinput
```

### 4. Create Superuser (Manual)

```bash
docker compose exec web python manage.py createsuperuser
# Follow prompts to create admin account
```

### 5. Load Sample Data

```bash
# Load comprehensive seed data
docker compose exec web python manage.py shell < scripts/seed_data.py

# This creates:
# - 5 Departments (CSE, ECE, MECH, CIVIL, EEE)
# - Admin user
# - 6 Faculty users
# - 3 HoD users
# - 1 Dean user
# - 5 Main KPI parameters
# - 9 Sub-parameters
# - Dynamic form templates
# - 3 Cutoff windows
```

---

## 👥 User Roles

### 1. Administrator
- Manage all users and departments
- Configure KPI parameters and sub-parameters
- Create dynamic form templates
- Set cutoff windows and deadlines
- View system-wide analytics
- Access Django admin panel

### 2. Faculty
- Submit KPI entries for assigned sub-parameters
- Fill dynamic forms with file attachments
- Track submission status
- View personal performance dashboard
- Receive notifications on submission updates

### 3. Head of Department (HoD)
- Review and approve submissions from department faculty
- Award points (within max limits)
- Request revisions or reject submissions
- View department performance dashboard
- Receive team average bonus for mapped parameters

### 4. Dean
- Give final approval for faculty submissions
- View consolidated performance across departments
- Access multi-department analytics
- Monitor department-wise comparisons
- Approve or reject entire faculty performance for a window

---

## 📚 Usage Guide

### For Faculty

#### 1. Create a Submission
1. Login to your account
2. Navigate to "My Submissions"
3. Click "New Submission"
4. Select sub-parameter, month, and year
5. Fill the dynamic form
6. Upload required proof documents
7. Save as draft or submit for review

#### 2. Track Submissions
- View all submissions in "My Submissions"
- Filter by status, month, or year
- Click on any submission to view details
- Edit drafts or revisions
- Download submission history as CSV

### For HoD

#### 1. Review Submissions
1. Navigate to "Reviews"
2. See pending submissions from your department
3. Click on a submission to review
4. View all submitted data and attachments
5. Approve (with points), Reject, or Request Revision

#### 2. View Department Dashboard
- Department-wise KPI breakdown
- Faculty performance comparison
- Pending approvals queue
- Team average calculations

### For Dean

#### 1. Final Approval
1. Navigate to "Dean Reviews"
2. Select month/year filter
3. View faculty with HOD-approved submissions
4. Review consolidated points
5. Give final approval for each faculty

#### 2. Department Comparison
- View department-wise performance charts
- Access faculty leaderboard
- Download consolidated reports

### For Admin

#### 1. User Management
1. Navigate to "Users"
2. Create individual users or import from CSV
3. Assign roles and departments
4. Manage dean department mappings

#### 2. KPI Configuration
1. Go to Django admin panel
2. Create Main Parameters with weightage
3. Add Sub-Parameters with max points
4. Configure approval routing (HOD or OTHER)
5. Set up HOD-Faculty parameter mappings for team averages

#### 3. Dynamic Form Builder
1. Navigate to Forms Builder in admin
2. Select a sub-parameter
3. Add form fields (text, number, file, etc.)
4. Configure validation rules
5. Set field order and requirements

#### 4. Cutoff Windows
1. Create cutoff windows for each month
2. Set deadlines for:
   - Faculty submissions
   - HoD approvals
   - Dean approvals
3. Assign to specific departments (optional)

---

## 🧪 Testing

### Run All Tests

```bash
# Run full test suite
docker compose exec web python manage.py test

# Run specific test file
docker compose exec web python manage.py test tests.test_models

# Run with verbose output
docker compose exec web python manage.py test --verbosity=2

# Run with coverage
docker compose exec web pytest --cov=apps --cov-report=html
```

### Manual Testing Checklist

- [ ] User authentication (login/logout)
- [ ] Role-based access control
- [ ] Submission creation and editing
- [ ] Dynamic form rendering
- [ ] File upload and validation
- [ ] Approval workflow (Faculty → HoD → Dean)
- [ ] Notification creation and display
- [ ] Dashboard data accuracy
- [ ] Chart rendering
- [ ] CSV import/export
- [ ] Cutoff deadline enforcement

---

## 🚢 Production Deployment

### 1. Update Environment Variables

```bash
# .env for production
DJANGO_SECRET_KEY=<generate-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Security settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Database (use managed PostgreSQL service)
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=rtc_kpi_production
DB_USER=rtc_production_user
DB_PASSWORD=<strong-password>
```

### 2. Collect Static Files

```bash
docker compose exec web python manage.py collectstatic --noinput
```

### 3. Use Gunicorn

Update `docker-compose.yml` command:

```yaml
command: gunicorn --bind 0.0.0.0:8000 --workers 4 rtc_kpi.wsgi:application
```

### 4. Set Up Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. Set Up SSL (Let's Encrypt)

```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 6. Database Backups

```bash
# Backup script
docker compose exec db pg_dump -U rtc_user rtc_kpi_db > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T db psql -U rtc_user rtc_kpi_db < backup_20250101.sql
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Error

```bash
# Check if database is running
docker compose ps

# Restart database
docker compose restart db

# Check logs
docker compose logs db
```

#### 2. Migration Errors

```bash
# Reset migrations (CAUTION: Loses data)
docker compose exec web python manage.py migrate --fake-initial

# Or manually fix
docker compose exec db psql -U rtc_user rtc_kpi_db
# Run SQL to fix issues
```

#### 3. Permission Denied for Uploads

```bash
# Fix file permissions
docker compose exec web chmod -R 755 /app/media
```

#### 4. Static Files Not Loading

```bash
# Re-collect static files
docker compose exec web python manage.py collectstatic --clear --noinput
```

#### 5. Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Debug Mode

Enable detailed error pages:

```python
# In .env
DEBUG=True
```

View logs:

```bash
# Web application logs
docker compose logs -f web

# Database logs
docker compose logs -f db

# All logs
docker compose logs -f
```

---

## 📊 Additional Features

### CSV Import Format

**Users CSV Format:**
```csv
email,full_name,role,department_id,phone,employee_id,password
john@rtc.edu,John Doe,FACULTY,1,9876543210,F001,faculty123
```

### File Upload Restrictions

- **Maximum Size**: 10MB per file
- **Allowed Types**: .pdf, .doc, .docx, .xls, .xlsx, .jpg, .jpeg, .png, .zip

### Notification System

Automatic notifications are sent for:
- Submission submitted (to reviewer)
- Revision requested (to faculty)
- HOD approved (to dean)
- Dean approved (to faculty and HoD)
- Submission rejected (to faculty)

---

## 📄 License

Copyright © 2025 Rathinam Technical Campus. All rights reserved.

---

## 👨‍💻 Support

For issues or questions:
- **Email**: support@rtc.edu
- **Documentation**: [Internal Wiki]
- **GitHub Issues**: [Project Repository]

---

## 🗺 Roadmap

Future enhancements:
- [ ] Mobile responsive design improvements
- [ ] Email notifications (optional SMTP)
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] API for external integrations
- [ ] Excel export for detailed reports
- [ ] Automated reminder system

---

**Happy KPI Management! 🎓**
