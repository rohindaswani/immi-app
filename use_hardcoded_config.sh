#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

APP_PATH="/Users/rohindaswani/Projects/immigration_app"
BACKEND_PATH="$APP_PATH/backend"

echo -e "${YELLOW}=== Using hardcoded config and running backend ===${NC}\n"

# Backup the original config if not already backed up
if [ ! -f "$BACKEND_PATH/app/core/config.py.original" ]; then
    echo "Backing up original config.py to config.py.original..."
    cp "$BACKEND_PATH/app/core/config.py" "$BACKEND_PATH/app/core/config.py.original"
fi

# Replace with hardcoded config
echo "Replacing with hardcoded config..."
cp "$BACKEND_PATH/app/core/hardcoded_config.py" "$BACKEND_PATH/app/core/config.py"

# Start the backend
echo -e "\n${GREEN}Starting backend server...${NC}"
echo -e "API will be available at: ${GREEN}http://localhost:8000${NC}"
echo -e "API documentation: ${GREEN}http://localhost:8000/api/v1/docs${NC}"
echo -e "Health check: ${GREEN}http://localhost:8000/health${NC}"
echo -e "Press Ctrl+C to stop the server\n"

cd "$BACKEND_PATH" && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000