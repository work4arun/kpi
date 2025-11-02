
# Database Error Fix: "database rtc_user does not exist"

## 🔍 Root Cause Analysis

The error `FATAL: database "rtc_user" does not exist` occurs every 10 seconds due to a configuration issue in the Docker health check.

### **What's causing the error:**

In `docker-compose.yml` line 13, the PostgreSQL health check uses:
```yaml
test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rtc_user}"]
```

**The problem:** 
- `pg_isready -U rtc_user` checks if PostgreSQL is ready by attempting to connect to a database
- When no database is specified with the `-d` flag, `pg_isready` defaults to connecting to a database with the **same name as the user**
- Since the user is `rtc_user`, it tries to connect to a database named `rtc_user`
- However, the actual database is named `rtc_kpi_db`, not `rtc_user`
- This causes the error to repeat every 10 seconds (the health check interval)

### **Why the application still works:**
The Django application correctly connects to `rtc_kpi_db` using the environment variables. The error is **only** from the health check, which is used by Docker Compose to determine if the database service is ready.

---

## ✅ The Fix

Add the `-d` flag to the health check to specify the correct database name:

```yaml
test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rtc_user} -d ${DB_NAME:-rtc_kpi_db}"]
```

This tells `pg_isready` to check the `rtc_kpi_db` database instead of trying to connect to a non-existent `rtc_user` database.

---

## 🚀 Automated Fix

### Option 1: Run the Fix Script (Recommended)

1. Make the fix script executable and run it:
```bash
cd /home/ubuntu/code_artifacts/rtc_kpi_system
chmod +x fix_database_error.sh
./fix_database_error.sh
```

The script will:
- Create a backup of your current docker-compose.yml
- Apply the fix automatically
- Restart the containers
- Verify the fix was successful

---

## 🔧 Manual Fix Steps

If you prefer to fix it manually:

### Step 1: Stop the containers
```bash
cd /home/ubuntu/code_artifacts/rtc_kpi_system
docker compose down
```

### Step 2: Backup the current configuration
```bash
cp docker-compose.yml docker-compose.yml.backup
```

### Step 3: Edit docker-compose.yml

Open `docker-compose.yml` and find line 13:
```yaml
test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rtc_user}"]
```

Replace it with:
```yaml
test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rtc_user} -d ${DB_NAME:-rtc_kpi_db}"]
```

### Step 4: Restart the containers
```bash
docker compose up -d
```

### Step 5: Verify the fix
Wait about 30 seconds, then check the logs:
```bash
docker compose logs db --tail=50
```

You should **no longer** see the `FATAL: database "rtc_user" does not exist` error.

---

## ✓ Verification Commands

After applying the fix, run these commands to verify:

### 1. Check container health status
```bash
docker compose ps
```
The `db` service should show `healthy` status.

### 2. Check database logs (should be clean)
```bash
docker compose logs db --tail=50 | grep -i "fatal\|error"
```
Should return no "rtc_user" database errors.

### 3. Verify the application still works
```bash
curl http://localhost:8000
```
Should return the login page HTML.

### 4. Connect to the database directly
```bash
docker compose exec db psql -U rtc_user -d rtc_kpi_db -c "\dt"
```
Should list all Django tables.

---

## 📊 Before and After Comparison

### Before Fix:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rtc_user}"]
  interval: 10s
  timeout: 5s
  retries: 5
```
- ❌ Tries to connect to database "rtc_user" (doesn't exist)
- ❌ Generates error every 10 seconds
- ⚠️  Health check never truly validates the correct database

### After Fix:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rtc_user} -d ${DB_NAME:-rtc_kpi_db}"]
  interval: 10s
  timeout: 5s
  retries: 5
```
- ✅ Connects to correct database "rtc_kpi_db"
- ✅ No more errors in logs
- ✅ Health check properly validates database readiness

---

## 🔄 Rollback Instructions

If you need to rollback the changes:

```bash
cd /home/ubuntu/code_artifacts/rtc_kpi_system
docker compose down
cp docker-compose.yml.backup docker-compose.yml
docker compose up -d
```

---

## 📝 Additional Notes

### Why this error wasn't breaking the application:
- The Django application uses environment variables (`DB_NAME=rtc_kpi_db`) to connect
- The health check error was isolated to the Docker health monitoring
- The database container was still functioning correctly

### Impact of not fixing:
- Cluttered logs with repeated error messages
- Potential confusion during debugging
- Health check not accurately reflecting database status

### Impact of the fix:
- ✅ Clean logs without errors
- ✅ Accurate health monitoring
- ✅ No change to application functionality
- ✅ Better Docker Compose orchestration

---

## 🆘 Troubleshooting

### If you still see errors after the fix:

1. **Check if the fix was applied:**
```bash
grep "pg_isready" docker-compose.yml
```
Should show: `pg_isready -U ${DB_USER:-rtc_user} -d ${DB_NAME:-rtc_kpi_db}`

2. **Ensure containers were restarted:**
```bash
docker compose ps
```
Check the "STATUS" column - containers should show recent restart time.

3. **Check environment variables:**
```bash
docker compose exec web env | grep DB_
```
Should show `DB_NAME=rtc_kpi_db` and `DB_USER=rtc_user`

4. **Force recreate containers:**
```bash
docker compose down
docker compose up -d --force-recreate
```

---

## 📧 Support

If you continue experiencing issues:
1. Check all verification commands above
2. Review the container logs: `docker compose logs`
3. Ensure your .env file has correct database configuration

---

**Fix Created:** November 1, 2025  
**Status:** Ready to Apply  
**Risk Level:** Low (only changes health check, no data or application logic affected)
