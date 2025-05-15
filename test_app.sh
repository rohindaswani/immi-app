#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${YELLOW}=== Testing Immigration Advisor Application ===${NC}\n"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Test database connections
echo -e "${YELLOW}=== Testing Database Connections ===${NC}"
echo "Starting database containers..."
# Try docker-compose first, then try docker compose if the first fails
if command -v docker-compose &> /dev/null; then
    docker-compose up -d postgres mongodb redis
else
    docker compose up -d postgres mongodb redis
fi

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
sleep 10

# Run database tests
echo "Running database tests..."
cd backend
python test_db.py

# Check if database tests passed
if [ $? -ne 0 ]; then
    echo -e "${RED}Database tests failed. Please check the logs above.${NC}"
    exit 1
fi

# Test running the API
echo -e "\n${YELLOW}=== Testing API Startup ===${NC}"
echo "Starting the API server in the background..."

# Start the API server
cd /Users/rohindaswani/Projects/immigration_app/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Save the PID
API_PID=$!

# Wait for the API to start
echo "Waiting for API to start..."
sleep 5

# Run API tests
echo "Running API tests..."
python test_api.py

# Check if API tests passed
if [ $? -ne 0 ]; then
    echo -e "${RED}API tests failed. Please check the logs above.${NC}"
    kill $API_PID
    exit 1
fi

# Kill the API server
echo "Stopping API server..."
kill $API_PID

# Success message
echo -e "\n${GREEN}All tests passed! The application is working correctly.${NC}"

# Instructions for running
echo -e "\n${YELLOW}=== Running the Application ===${NC}"
echo -e "To run the backend:"
echo -e "${GREEN}cd /Users/rohindaswani/Projects/immigration_app/backend && python -m uvicorn app.main:app --reload${NC}"
echo -e "\nTo run the frontend (when implemented):"
echo -e "${GREEN}cd /Users/rohindaswani/Projects/immigration_app/frontend && npm run dev${NC}"
echo -e "\nAPI documentation will be available at: ${GREEN}http://localhost:8000/api/v1/docs${NC}"