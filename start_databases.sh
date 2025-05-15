#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Starting databases for Immigration Advisor Application ===${NC}\n"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

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

echo -e "\n${GREEN}Databases started successfully!${NC}"
echo "PostgreSQL: localhost:5432"
echo "MongoDB: localhost:27017"
echo "Redis: localhost:6379"

echo -e "\n${YELLOW}To start the backend, run:${NC}"
echo "cd /Users/rohindaswani/Projects/immigration_app/backend"
echo "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo -e "\n${YELLOW}To start the frontend, run:${NC}"
echo "cd /Users/rohindaswani/Projects/immigration_app/frontend"
echo "npm install"
echo "npm run dev"