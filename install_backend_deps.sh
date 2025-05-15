#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

APP_PATH="/Users/rohindaswani/Projects/immigration_app"
BACKEND_PATH="$APP_PATH/backend"

echo -e "${YELLOW}=== Installing backend dependencies ===${NC}\n"

# Check if Python is installed
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Go to backend directory
cd "$BACKEND_PATH"

# Install dependencies
echo -e "Installing Python dependencies..."
python3 -m pip install -r requirements.txt --upgrade

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Dependencies installed successfully!${NC}"
echo -e "You can now run the backend with: ${YELLOW}./start_backend.sh${NC}"