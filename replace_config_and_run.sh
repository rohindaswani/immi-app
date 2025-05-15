#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

APP_PATH="/Users/rohindaswani/Projects/immigration_app"
BACKEND_PATH="$APP_PATH/backend"

echo -e "${YELLOW}=== Replacing config and running backend ===${NC}\n"

# Backup the original config
echo "Backing up original config.py..."
cp "$BACKEND_PATH/app/core/config.py" "$BACKEND_PATH/app/core/config.py.backup"

# Replace with simplified config
echo "Replacing with simplified config..."
cp "$BACKEND_PATH/app/core/config.py.new" "$BACKEND_PATH/app/core/config.py"

# Start the backend
echo -e "\n${GREEN}Starting backend server...${NC}"
echo -e "API will be available at: ${GREEN}http://localhost:8000${NC}"
echo -e "API documentation: ${GREEN}http://localhost:8000/api/v1/docs${NC}"
echo -e "Health check: ${GREEN}http://localhost:8000/health${NC}"
echo -e "Press Ctrl+C to stop the server\n"

cd "$BACKEND_PATH" && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000