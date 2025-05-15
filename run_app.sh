#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Path to the application
APP_PATH="/Users/rohindaswani/Projects/immigration_app"
BACKEND_PATH="$APP_PATH/backend"
FRONTEND_PATH="$APP_PATH/frontend"

# Print header
echo -e "${YELLOW}=== Running Immigration Advisor Application ===${NC}\n"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Start database containers
echo -e "Starting database containers..."
# Try docker-compose first, then try docker compose if the first fails
if command -v docker-compose &> /dev/null; then
    cd "$APP_PATH" && docker-compose up -d postgres mongodb redis
else
    cd "$APP_PATH" && docker compose up -d postgres mongodb redis
fi

# Check if containers started successfully
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to start database containers. Please check Docker logs.${NC}"
    exit 1
fi

echo -e "${GREEN}Database containers started successfully.${NC}"

# Wait for databases to be ready
echo -e "Waiting for databases to be ready..."
sleep 10

# Initialize the database if it doesn't exist
echo -e "Checking database status..."
cd "$BACKEND_PATH" && python -m scripts.db_migrations --action test > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "Initializing database..."
    cd "$BACKEND_PATH" && python -m scripts.db_migrations --action create
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to initialize database. Please check the logs above.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Database initialized successfully.${NC}"
else
    echo -e "${GREEN}Database already initialized.${NC}"
fi

# Start the backend server in one terminal
echo -e "\n${YELLOW}=== Starting Backend Server ===${NC}"
echo -e "Starting backend server at http://localhost:8000"
echo -e "API docs will be available at http://localhost:8000/api/v1/docs"
echo -e "Press Ctrl+C to stop the server"
echo -e "${GREEN}cd $BACKEND_PATH && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000${NC}"

# Instructions for frontend
echo -e "\n${YELLOW}=== Frontend Instructions ===${NC}"
echo -e "To start the frontend server, open a new terminal and run:"
echo -e "${GREEN}cd $FRONTEND_PATH && npm run dev${NC}"
echo -e "The frontend will be available at http://localhost:3000"

# Start the backend server
cd "$BACKEND_PATH" && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000