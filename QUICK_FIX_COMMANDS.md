# Quick Fix Commands - Database Error

## 🚀 Apply the Fix (Choose One)

### Option 1: Restart Containers (Fix Already Applied)
```bash
cd /home/ubuntu/code_artifacts/rtc_kpi_system
docker compose down
docker compose up -d
```

### Option 2: Run Automated Fix Script
```bash
cd /home/ubuntu/code_artifacts/rtc_kpi_system
./fix_database_error.sh
```

---

## ✓ Verify the Fix

```bash
# Check container status
docker compose ps

# Check logs for errors (should be none after restart)
docker compose logs db --tail=50 | grep "rtc_user"

# Monitor logs in real-time (Ctrl+C to exit)
docker compose logs db -f

# Test application
curl http://localhost:8000
```

---

## 📊 What Changed

**File:** `docker-compose.yml` line 13

**Before:**
```yaml
test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rtc_user}"]
```

**After:**
```yaml
test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rtc_user} -d ${DB_NAME:-rtc_kpi_db}"]
```

---

## 📖 Full Documentation

- **Summary:** `FIX_SUMMARY.md`
- **Detailed Guide:** `DATABASE_ERROR_FIX.md`
- **Automated Script:** `fix_database_error.sh`

---

**Quick Reference - Keep This Handy! 📌**
