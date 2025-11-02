
#!/bin/bash

# =============================================================================
# RTC KPI System - Database Health Check Fix Script
# =============================================================================
# This script fixes the "database rtc_user does not exist" error by updating
# the PostgreSQL health check in docker-compose.yml
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"
BACKUP_FILE="${SCRIPT_DIR}/docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# =============================================================================
# Pre-flight Checks
# =============================================================================

print_header "Database Health Check Fix Script"
echo ""

print_info "Checking prerequisites..."

# Check if docker-compose.yml exists
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "docker-compose.yml not found at $COMPOSE_FILE"
    exit 1
fi
print_success "Found docker-compose.yml"

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi
print_success "Docker is available"

# Check if containers are running
if docker compose ps &> /dev/null; then
    CONTAINERS_RUNNING=true
    print_success "Docker containers are running"
else
    CONTAINERS_RUNNING=false
    print_warning "Docker containers are not currently running"
fi

echo ""

# =============================================================================
# Show Current Problem
# =============================================================================

print_header "Current Problem"
echo ""
print_info "The health check in docker-compose.yml is incorrectly configured:"
echo ""
echo "Current line 13:"
grep -n "pg_isready" "$COMPOSE_FILE" || true
echo ""
print_warning "This causes pg_isready to try connecting to database 'rtc_user' instead of 'rtc_kpi_db'"
echo ""

# Show recent errors if containers are running
if [ "$CONTAINERS_RUNNING" = true ]; then
    print_info "Recent database errors (if any):"
    docker compose logs db --tail=10 2>/dev/null | grep -i "rtc_user\|FATAL" || print_info "  (checking logs...)"
    echo ""
fi

# =============================================================================
# Create Backup
# =============================================================================

print_header "Creating Backup"
echo ""

cp "$COMPOSE_FILE" "$BACKUP_FILE"
print_success "Backup created: $BACKUP_FILE"
echo ""

# =============================================================================
# Apply Fix
# =============================================================================

print_header "Applying Fix"
echo ""

print_info "Updating health check configuration..."

# Create the fixed version
sed -i.tmp 's/test: \["CMD-SHELL", "pg_isready -U \${DB_USER:-rtc_user}"\]/test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-rtc_user} -d ${DB_NAME:-rtc_kpi_db}"]/' "$COMPOSE_FILE"
rm -f "${COMPOSE_FILE}.tmp"

# Verify the fix was applied
if grep -q 'pg_isready -U \${DB_USER:-rtc_user} -d \${DB_NAME:-rtc_kpi_db}' "$COMPOSE_FILE"; then
    print_success "Health check configuration updated successfully"
    echo ""
    print_info "New configuration:"
    grep -n "pg_isready" "$COMPOSE_FILE"
    echo ""
else
    print_error "Failed to apply fix"
    print_info "Restoring backup..."
    cp "$BACKUP_FILE" "$COMPOSE_FILE"
    exit 1
fi

# =============================================================================
# Restart Containers
# =============================================================================

print_header "Restarting Containers"
echo ""

if [ "$CONTAINERS_RUNNING" = true ]; then
    print_info "Stopping containers..."
    docker compose down
    print_success "Containers stopped"
    echo ""
fi

print_info "Starting containers with updated configuration..."
docker compose up -d
print_success "Containers started"
echo ""

# =============================================================================
# Wait for Services
# =============================================================================

print_header "Waiting for Services"
echo ""

print_info "Waiting for database to be ready (max 60 seconds)..."
COUNTER=0
MAX_WAIT=60
while [ $COUNTER -lt $MAX_WAIT ]; do
    if docker compose exec -T db pg_isready -U rtc_user -d rtc_kpi_db &> /dev/null; then
        print_success "Database is ready!"
        break
    fi
    echo -n "."
    sleep 2
    COUNTER=$((COUNTER + 2))
done
echo ""

if [ $COUNTER -ge $MAX_WAIT ]; then
    print_warning "Database health check timed out, but this may be normal"
fi

echo ""
sleep 5  # Give a bit more time for things to stabilize

# =============================================================================
# Verification
# =============================================================================

print_header "Verification"
echo ""

print_info "Checking container status..."
docker compose ps
echo ""

print_info "Checking for database errors in logs..."
ERROR_COUNT=$(docker compose logs db --tail=50 2>/dev/null | grep -c "database \"rtc_user\" does not exist" || echo "0")

if [ "$ERROR_COUNT" -eq "0" ]; then
    print_success "No 'rtc_user' database errors found in recent logs!"
else
    print_warning "Found $ERROR_COUNT error(s) - these may be from before the fix"
    print_info "New errors should not appear. Monitor logs with:"
    echo "    docker compose logs db -f"
fi
echo ""

print_info "Testing database connection..."
if docker compose exec -T db psql -U rtc_user -d rtc_kpi_db -c "SELECT 1;" &> /dev/null; then
    print_success "Successfully connected to rtc_kpi_db database"
else
    print_warning "Could not verify database connection"
fi
echo ""

print_info "Testing web application..."
sleep 3  # Give web app a moment to start
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200\|302"; then
    print_success "Web application is responding correctly"
else
    print_warning "Web application may still be starting up"
fi
echo ""

# =============================================================================
# Summary
# =============================================================================

print_header "Fix Complete!"
echo ""

print_success "The database health check has been successfully updated"
echo ""

print_info "Summary of changes:"
echo "  • Backup created: $BACKUP_FILE"
echo "  • Health check now uses correct database name (rtc_kpi_db)"
echo "  • Containers restarted with new configuration"
echo ""

print_info "Next steps:"
echo "  1. Monitor the logs to confirm no more errors:"
echo "     ${YELLOW}docker compose logs db -f${NC}"
echo ""
echo "  2. Verify the application is working:"
echo "     ${YELLOW}http://localhost:8000${NC}"
echo ""
echo "  3. To rollback if needed:"
echo "     ${YELLOW}docker compose down${NC}"
echo "     ${YELLOW}cp $BACKUP_FILE docker-compose.yml${NC}"
echo "     ${YELLOW}docker compose up -d${NC}"
echo ""

print_header "Documentation"
print_info "For detailed information, see: DATABASE_ERROR_FIX.md"
echo ""

print_success "All done! Your database error should now be resolved. 🎉"
