#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

APP_PATH="/Users/rohindaswani/Projects/immigration_app"
BACKEND_PATH="$APP_PATH/backend"

echo -e "${YELLOW}=== Starting backend for Immigration Advisor Application ===${NC}\n"

# Check if Docker is running (for database connections)
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Warning: Docker is not running. Database connections may fail.${NC}"
    echo -e "Please start Docker and run ./start_databases.sh before proceeding."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if the database containers are running
POSTGRES_RUNNING=$(docker ps -q -f name=immigration-postgres)
MONGODB_RUNNING=$(docker ps -q -f name=immigration-mongodb)
REDIS_RUNNING=$(docker ps -q -f name=immigration-redis)

if [ -z "$POSTGRES_RUNNING" ] || [ -z "$MONGODB_RUNNING" ] || [ -z "$REDIS_RUNNING" ]; then
    echo -e "${RED}Warning: Some database containers are not running.${NC}"
    echo -e "Please ensure all database containers are started with ./start_databases.sh"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if required Python packages are installed
echo -e "Checking if required Python packages are installed..."
if ! python3 -c "import uvicorn" &>/dev/null; then
    echo -e "${RED}Error: uvicorn package is not installed.${NC}"
    echo -e "Please run ${YELLOW}./install_backend_deps.sh${NC} to install dependencies."
    exit 1
fi

if ! python3 -c "import fastapi" &>/dev/null; then
    echo -e "${RED}Error: fastapi package is not installed.${NC}"
    echo -e "Please run ${YELLOW}./install_backend_deps.sh${NC} to install dependencies."
    exit 1
fi

# Start the backend server
echo -e "${YELLOW}Starting backend server...${NC}"
echo -e "API will be available at: ${GREEN}http://localhost:8000${NC}"
echo -e "API documentation: ${GREEN}http://localhost:8000/api/v1/docs${NC}"
echo -e "Health check: ${GREEN}http://localhost:8000/health${NC}"
echo -e "Press Ctrl+C to stop the server\n"

cd "$BACKEND_PATH" && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000