#!/bin/bash

# RTC KPI System - Setup and Validation Script
# This script sets up the Django project and validates the installation

set -e

echo "=========================================="
echo "RTC KPI System - Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
    docker --version
else
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
echo ""
echo "2. Checking Docker Compose installation..."
if command -v docker compose &> /dev/null || command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose is installed${NC}"
    docker compose version 2>/dev/null || docker-compose --version
else
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

# Create .env if it doesn't exist
echo ""
echo "3. Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file from .env.example${NC}"
    echo -e "${YELLOW}⚠ Please update .env with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create necessary directories
echo ""
echo "4. Creating necessary directories..."
mkdir -p media/attachments
mkdir -p staticfiles
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"

# Validate project structure
echo ""
echo "5. Validating project structure..."
REQUIRED_DIRS=(
    "apps/accounts"
    "apps/departments"
    "apps/kpi"
    "apps/submissions"
    "apps/reviews"
    "apps/dashboards"
    "apps/notifications"
    "apps/forms_builder"
    "apps/common"
    "templates"
    "static"
    "scripts"
)

all_good=true
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir"
    else
        echo -e "${RED}✗${NC} $dir is missing"
        all_good=false
    fi
done

if [ "$all_good" = true ]; then
    echo -e "${GREEN}✓ All required directories exist${NC}"
else
    echo -e "${RED}✗ Some directories are missing${NC}"
    exit 1
fi

# Check required files
echo ""
echo "6. Checking required files..."
REQUIRED_FILES=(
    "manage.py"
    "requirements.txt"
    "docker-compose.yml"
    "Dockerfile"
    "rtc_kpi/settings.py"
)

all_files_good=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file is missing"
        all_files_good=false
    fi
done

if [ "$all_files_good" = true ]; then
    echo -e "${GREEN}✓ All required files exist${NC}"
else
    echo -e "${RED}✗ Some files are missing${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup validation completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review and update .env file with your configuration"
echo "2. Run: docker compose up --build"
echo "3. In a new terminal, run migrations:"
echo "   docker compose exec web python manage.py migrate"
echo "4. Create superuser:"
echo "   docker compose exec web python manage.py createsuperuser"
echo "5. Load seed data:"
echo "   docker compose exec web python manage.py shell < scripts/seed_data.py"
echo "6. Access the application at http://localhost:8000"
echo ""
echo "For detailed instructions, see README.md"
echo "=========================================="
