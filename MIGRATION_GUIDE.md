# Django Migration Guide - RTC KPI System

## Overview
This guide provides step-by-step instructions for applying database migrations and setting up your RTC KPI System.

## Issues Fixed ✅

### 1. Docker Compose Warning
**Fixed:** Removed the obsolete `version` attribute from `docker-compose.yml`. Modern Docker Compose versions don't require this attribute.

### 2. Missing Migrations
**Fixed:** Created initial migration files for all Django apps in the correct dependency order:
- ✅ `common` - Base models and utilities
- ✅ `departments` - Department structure
- ✅ `accounts` - Custom User model
- ✅ `kpi` - KPI parameters and cutoff windows
- ✅ `forms_builder` - Dynamic form builder
- ✅ `submissions` - KPI submissions and attachments
- ✅ `reviews` - Review and approval workflow
- ✅ `notifications` - In-app notifications

## App Dependency Chain

Understanding the dependency order is important for troubleshooting:

```
1. common (base, no dependencies)
   └── TimeStampedModel (abstract base class)
   └── ActivityLog (audit trail)

2. departments (depends on: common)
   └── Department

3. accounts (depends on: common, departments)
   └── User (custom user model)

4. kpi (depends on: common, departments)
   └── MainParameter, SubParameter, CutoffWindow

5. forms_builder (depends on: common, kpi)
   └── DynamicFormTemplate, DynamicField

6. submissions (depends on: accounts, kpi, forms_builder)
   └── Submission, SubmissionFieldValue, Attachment

7. reviews (depends on: accounts, submissions)
   └── Review, DeanApproval

8. notifications (depends on: accounts, submissions)
   └── Notification

9. dashboards (no models, views only)
```

---

## Quick Start Guide

### Step 1: Start the Database Container

```bash
cd /Users/arun/Desktop/RTC_KPI_System_Development/code_artifacts/rtc_kpi_system/
docker-compose up -d db
```

**Wait for the database to be ready:**
```bash
docker-compose ps
```
You should see the `db` container with status "healthy".

### Step 2: Apply Migrations

Run migrations to create all database tables:

```bash
docker-compose run --rm web python manage.py migrate
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: accounts, admin, auth, common, contenttypes, departments, forms_builder, kpi, notifications, reviews, sessions, submissions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  ...
  Applying common.0001_initial... OK
  Applying departments.0001_initial... OK
  Applying accounts.0001_initial... OK
  Applying kpi.0001_initial... OK
  ...
```

### Step 3: Create a Superuser

Create an admin account to access the system:

```bash
docker-compose run --rm web python manage.py createsuperuser
```

**Follow the prompts:**
```
Email: admin@rtc.edu
Full name: System Administrator
Password: [enter secure password]
Password (again): [confirm password]
```

### Step 4: Start the Application

```bash
docker-compose up
```

The application will be available at: **http://localhost:8000**

Admin panel: **http://localhost:8000/admin**

---

## Verification Steps

### 1. Check Migration Status

Verify all migrations are applied:

```bash
docker-compose run --rm web python manage.py showmigrations
```

All migrations should have `[X]` marks (applied).

### 2. Verify Database Tables

Check that tables were created:

```bash
docker-compose exec db psql -U rtc_user -d rtc_kpi_db -c "\dt"
```

You should see tables like:
- `users`
- `departments`
- `main_parameters`
- `sub_parameters`
- `submissions`
- etc.

### 3. Test Login

1. Visit http://localhost:8000/admin
2. Login with your superuser credentials
3. You should see the Django admin interface

---

## Common Commands Reference

### Database Management

```bash
# Start only the database
docker-compose up -d db

# Stop all services
docker-compose down

# View database logs
docker-compose logs db

# Access PostgreSQL shell
docker-compose exec db psql -U rtc_user -d rtc_kpi_db
```

### Django Management Commands

```bash
# Create new migrations (if you modify models)
docker-compose run --rm web python manage.py makemigrations

# Apply migrations
docker-compose run --rm web python manage.py migrate

# Check migration status
docker-compose run --rm web python manage.py showmigrations

# Create superuser
docker-compose run --rm web python manage.py createsuperuser

# Run Django shell
docker-compose run --rm web python manage.py shell

# Collect static files (for production)
docker-compose run --rm web python manage.py collectstatic --noinput
```

### Application Commands

```bash
# Start all services (database + web)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f web

# Restart web service
docker-compose restart web

# Stop all services
docker-compose down

# Stop and remove all data (⚠️ CAUTION: This deletes the database!)
docker-compose down -v
```

---

## Troubleshooting

### Issue: "could not translate host name 'db'"

**Cause:** Database container is not running.

**Solution:**
```bash
docker-compose up -d db
# Wait 10 seconds for db to be ready
docker-compose run --rm web python manage.py migrate
```

### Issue: "relation does not exist"

**Cause:** Migrations have not been applied.

**Solution:**
```bash
docker-compose run --rm web python manage.py migrate
```

### Issue: "No such file or directory: 'manage.py'"

**Cause:** You're not in the project directory.

**Solution:**
```bash
cd /Users/arun/Desktop/RTC_KPI_System_Development/code_artifacts/rtc_kpi_system/
```

### Issue: "Port 5432 is already allocated"

**Cause:** Another PostgreSQL instance is running on port 5432.

**Solution:**
```bash
# Option 1: Stop the other PostgreSQL service
sudo systemctl stop postgresql  # On Linux
brew services stop postgresql   # On macOS

# Option 2: Change the port in docker-compose.yml
# Change "5432:5432" to "5433:5432"
```

### Issue: Migrations out of order

**Cause:** Migrations were applied in wrong order or dependencies changed.

**Solution:**
```bash
# Drop and recreate the database (⚠️ CAUTION: Deletes all data!)
docker-compose down -v
docker-compose up -d db
# Wait for db to be ready
docker-compose run --rm web python manage.py migrate
```

---

## Environment Configuration

The system uses environment variables defined in `.env` file. Key settings:

```bash
# Database
DB_NAME=rtc_kpi_db
DB_USER=rtc_user
DB_PASSWORD=rtc_password_change_me
DB_HOST=db
DB_PORT=5432

# Django
DJANGO_SECRET_KEY=dev-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Application
TIME_ZONE=Asia/Kolkata
LANGUAGE_CODE=en-us
```

**⚠️ Important for Production:**
- Change `DJANGO_SECRET_KEY` to a random string
- Set `DEBUG=False`
- Change database password
- Update `ALLOWED_HOSTS` with your domain

---

## Next Steps After Setup

1. **Configure Departments**
   - Access Admin panel: http://localhost:8000/admin
   - Add departments (e.g., CSE, ECE, MECH)

2. **Create User Accounts**
   - Add Faculty, HoD, and Dean users
   - Assign them to departments

3. **Define KPI Parameters**
   - Create Main Parameters
   - Add Sub-Parameters with weightage
   - Configure approval routing

4. **Set Up Cutoff Windows**
   - Define submission and approval deadlines
   - Associate with departments

5. **Build Dynamic Forms**
   - Create form templates for sub-parameters
   - Add fields for data collection

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review Django logs: `docker-compose logs -f web`
- Check database logs: `docker-compose logs -f db`
- Consult the main README.md for project documentation

---

## Files Modified/Created

### Modified:
- ✅ `docker-compose.yml` - Removed obsolete version attribute

### Created:
- ✅ `apps/common/migrations/0001_initial.py`
- ✅ `apps/departments/migrations/0001_initial.py`
- ✅ `apps/accounts/migrations/0001_initial.py`
- ✅ `apps/kpi/migrations/0001_initial.py`
- ✅ `apps/forms_builder/migrations/0001_initial.py`
- ✅ `apps/submissions/migrations/0001_initial.py`
- ✅ `apps/reviews/migrations/0001_initial.py`
- ✅ `apps/notifications/migrations/0001_initial.py`

---

**Last Updated:** November 1, 2025  
**Django Version:** 5.0.0  
**Python Version:** 3.11+
