#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

APP_PATH="/Users/rohindaswani/Projects/immigration_app"
FRONTEND_PATH="$APP_PATH/frontend"

echo -e "${YELLOW}=== Starting frontend for Immigration Advisor Application ===${NC}\n"

# Check if the backend is running
BACKEND_RUNNING=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "404")

if [ "$BACKEND_RUNNING" != "200" ]; then
    echo -e "${RED}Warning: Backend server does not appear to be running.${NC}"
    echo -e "Please start the backend with ./start_backend.sh to ensure full functionality."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Node.js is installed
if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}Error: Node.js is not installed. Please install Node.js and try again.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}Error: npm is not installed. Please install npm and try again.${NC}"
    exit 1
fi

# Check if node_modules exists, if not, install dependencies
if [ ! -d "$FRONTEND_PATH/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd "$FRONTEND_PATH" && npm install
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to install frontend dependencies.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Frontend dependencies installed successfully.${NC}\n"
else
    echo -e "${GREEN}Frontend dependencies already installed.${NC}\n"
fi

# Start the frontend server
echo -e "${YELLOW}Starting frontend development server...${NC}"
echo -e "Frontend will be available at: ${GREEN}http://localhost:3000${NC}"
echo -e "Press Ctrl+C to stop the server\n"

cd "$FRONTEND_PATH" && npm run dev