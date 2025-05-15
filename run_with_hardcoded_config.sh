#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

APP_PATH="/Users/rohindaswani/Projects/immigration_app"
BACKEND_PATH="$APP_PATH/backend"

echo -e "${YELLOW}=== Starting Immigration Advisor App with hardcoded config ===${NC}\n"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Warning: Docker is not running. Database connections may fail.${NC}"
    echo -e "Please start Docker before proceeding."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Install dependencies
echo -e "${YELLOW}Step 1: Installing dependencies...${NC}"
cd "$BACKEND_PATH"
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies.${NC}"
    exit 1
fi

echo -e "${GREEN}Dependencies installed successfully!${NC}\n"

# Step 2: Replace config with hardcoded version
echo -e "${YELLOW}Step 2: Setting up hardcoded configuration...${NC}"

# Backup the original config if not already backed up
if [ ! -f "$BACKEND_PATH/app/core/config.py.original" ]; then
    echo "Backing up original config.py to config.py.original..."
    cp "$BACKEND_PATH/app/core/config.py" "$BACKEND_PATH/app/core/config.py.original"
fi

# Create hardcoded config
cat > "$BACKEND_PATH/app/core/config.py" << 'EOF'
"""
Hardcoded configuration file with no .env dependency
"""

import secrets
from typing import List, Optional


class Settings:
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Immigration Advisor"
    
    # SECURITY
    SECRET_KEY: str = "DV8LwKMpcQsZNWzQbTHWqbjk7QchJrXjXhq6bdfP3mw"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_MAX_AGE: int = 14 * 24 * 60 * 60  # 14 days in seconds
    
    # CORS and Allowed Hosts - hardcoded
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # DATABASE
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/immigration_advisor"
    MONGODB_URL: str = "mongodb://localhost:27017/immigration_advisor"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ENVIRONMENT
    ENVIRONMENT: str = "development"
    
    # LOGGING
    LOG_LEVEL: str = "INFO"
    
    # FILE STORAGE
    STORAGE_BUCKET_NAME: Optional[str] = None
    STORAGE_ACCESS_KEY: Optional[str] = None
    STORAGE_SECRET_KEY: Optional[str] = None
    STORAGE_REGION: Optional[str] = None
    STORAGE_ENDPOINT: Optional[str] = None
    
    # RATE LIMITING
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # DEBUG
    DEBUG: bool = True
    
    # SERVICES
    PINECONE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None


settings = Settings()
EOF

echo -e "${GREEN}Hardcoded configuration set up successfully!${NC}\n"

# Step 3: Start databases
echo -e "${YELLOW}Step 3: Starting database containers...${NC}"

# Remove existing containers if they exist
echo "Removing any existing containers..."
docker rm -f immigration-postgres immigration-mongodb immigration-redis 2>/dev/null || true

# Create a Docker network if it doesn't exist
echo "Creating Docker network..."
docker network create immigration-network 2>/dev/null || true

# Start PostgreSQL
echo "Starting PostgreSQL container..."
docker run -d \
  --name immigration-postgres \
  --network immigration-network \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=immigration_advisor \
  -p 5432:5432 \
  postgres:15

# Start MongoDB
echo "Starting MongoDB container..."
docker run -d \
  --name immigration-mongodb \
  --network immigration-network \
  -p 27017:27017 \
  mongo:6

# Start Redis
echo "Starting Redis container..."
docker run -d \
  --name immigration-redis \
  --network immigration-network \
  -p 6379:6379 \
  redis:7

# Check if containers started successfully
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to start database containers.${NC}"
    exit 1
fi

echo -e "${GREEN}Database containers started successfully!${NC}\n"

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
sleep 10

# Step 4: Start the backend
echo -e "${YELLOW}Step 4: Starting backend server...${NC}"
echo -e "API will be available at: ${GREEN}http://localhost:8000${NC}"
echo -e "API documentation: ${GREEN}http://localhost:8000/api/v1/docs${NC}"
echo -e "Health check: ${GREEN}http://localhost:8000/health${NC}"
echo -e "Press Ctrl+C to stop the server\n"

cd "$BACKEND_PATH" && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000