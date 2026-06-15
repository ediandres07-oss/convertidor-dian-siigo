#!/bin/bash

# Health check script for CloudApp

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_URL=${BACKEND_URL:-http://localhost:8000}
FRONTEND_URL=${FRONTEND_URL:-http://localhost:3000}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-cloudapp_user}

# Check count
CHECK_COUNT=0
FAILED_COUNT=0

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local expected_code=$3

    echo -n "Checking $name... "

    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" = "$expected_code" ]; then
            echo -e "${GREEN}OK${NC} ($response)"
            CHECK_COUNT=$((CHECK_COUNT + 1))
            return 0
        else
            echo -e "${RED}FAILED${NC} (Expected: $expected_code, Got: $response)"
            FAILED_COUNT=$((FAILED_COUNT + 1))
            return 1
        fi
    else
        echo -e "${RED}FAILED${NC} (Connection error)"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        return 1
    fi
}

# Function to check database
check_database() {
    echo -n "Checking Database... "

    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        CHECK_COUNT=$((CHECK_COUNT + 1))
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    echo -n "Checking Disk Space... "

    available=$(df . | awk 'NR==2 {print $4}')
    available_gb=$((available / 1024 / 1024))

    if [ $available_gb -gt 1 ]; then
        echo -e "${GREEN}OK${NC} (${available_gb}GB available)"
        CHECK_COUNT=$((CHECK_COUNT + 1))
        return 0
    else
        echo -e "${RED}FAILED${NC} (Only ${available_gb}GB available)"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        return 1
    fi
}

# Main execution
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}CloudApp Health Check${NC}"
echo -e "${YELLOW}========================================${NC}"
echo

# Run checks
check_service "Backend" "${BACKEND_URL}/health" "200"
check_service "Backend Ready" "${BACKEND_URL}/ready" "200"
check_service "Frontend" "${FRONTEND_URL}" "200"
check_database
check_disk_space

echo
echo -e "${YELLOW}========================================${NC}"
echo -e "Total Checks: $(($CHECK_COUNT + $FAILED_COUNT))"
echo -e "${GREEN}Passed: $CHECK_COUNT${NC}"
echo -e "${RED}Failed: $FAILED_COUNT${NC}"
echo -e "${YELLOW}========================================${NC}"

if [ $FAILED_COUNT -gt 0 ]; then
    exit 1
else
    echo -e "${GREEN}All health checks passed!${NC}"
    exit 0
fi
