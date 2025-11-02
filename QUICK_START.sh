#!/bin/bash
#############################################################################
# RTC KPI System - Quick Start Script
# This script will set up your database and apply all migrations
#############################################################################

set -e  # Exit on error

echo "=================================================="
echo "   RTC KPI System - Quick Start Setup"
echo "=================================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed.${NC}"
    echo "Please install Docker and Docker Compose first."
    exit 1
fi

echo -e "${BLUE}Step 1: Starting PostgreSQL database...${NC}"
docker-compose up -d db

echo ""
echo -e "${YELLOW}Waiting for database to be ready (15 seconds)...${NC}"
sleep 15

echo ""
echo -e "${BLUE}Step 2: Checking database health...${NC}"
if docker-compose ps db | grep -q "healthy"; then
    echo -e "${GREEN}✓ Database is healthy and ready${NC}"
else
    echo -e "${YELLOW}⚠ Database might not be fully ready yet${NC}"
    echo "Waiting 10 more seconds..."
    sleep 10
fi

echo ""
echo -e "${BLUE}Step 3: Applying database migrations...${NC}"
docker-compose run --rm web python manage.py migrate

echo ""
echo -e "${GREEN}✓ Migrations applied successfully!${NC}"

echo ""
echo -e "${BLUE}Step 4: Creating superuser account...${NC}"
echo -e "${YELLOW}Please provide details for the admin account:${NC}"
echo ""
docker-compose run --rm web python manage.py createsuperuser

echo ""
echo -e "${GREEN}✓ Superuser created successfully!${NC}"

echo ""
echo "=================================================="
echo -e "${GREEN}   Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the application:"
echo -e "   ${BLUE}docker-compose up${NC}"
echo ""
echo "2. Access the application:"
echo -e "   Application: ${BLUE}http://localhost:8000${NC}"
echo -e "   Admin Panel: ${BLUE}http://localhost:8000/admin${NC}"
echo ""
echo "3. To stop the application:"
echo -e "   ${BLUE}docker-compose down${NC}"
echo ""
echo "For more information, see MIGRATION_GUIDE.md"
echo ""
