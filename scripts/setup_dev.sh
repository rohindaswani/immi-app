#!/bin/bash

# Script to set up development environment for Immigration Advisor app

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print section header
print_header() {
    echo -e "\n${YELLOW}====== $1 ======${NC}\n"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Docker and Docker Compose
print_header "Checking for Docker and Docker Compose"

if command_exists docker; then
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${RED}✗ Docker not found${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

if command_exists docker-compose; then
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${RED}✗ Docker Compose not found${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for Python
print_header "Checking for Python"

if command_exists python3; then
    echo -e "${GREEN}✓ Python installed: $(python3 --version)${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Check for Node.js
print_header "Checking for Node.js"

if command_exists node; then
    echo -e "${GREEN}✓ Node.js installed: $(node --version)${NC}"
else
    echo -e "${RED}✗ Node.js not found${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

if command_exists npm; then
    echo -e "${GREEN}✓ npm installed: $(npm --version)${NC}"
else
    echo -e "${RED}✗ npm not found${NC}"
    echo "Please install npm (should come with Node.js)"
    exit 1
fi

# Set up Python virtual environment
print_header "Setting up Python virtual environment"

if [ -d "backend/venv" ]; then
    echo "Virtual environment already exists"
else
    echo "Creating virtual environment..."
    cd backend && python3 -m venv venv
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    else
        echo -e "${RED}✗ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source backend/venv/bin/activate && pip install -r backend/requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install Python dependencies${NC}"
    exit 1
fi

# Set up frontend dependencies
print_header "Setting up frontend dependencies"

echo "Installing frontend dependencies..."
cd frontend && npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install frontend dependencies${NC}"
    exit 1
fi

# Set up environment files
print_header "Setting up environment files"

if [ ! -f "backend/.env" ]; then
    echo "Creating backend .env file..."
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ Created backend/.env${NC}"
    echo -e "${YELLOW}! Remember to update the values in backend/.env${NC}"
else
    echo "backend/.env already exists"
fi

# Start the development environment
print_header "Starting development environment"

echo "Starting Docker containers..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker containers started${NC}"
else
    echo -e "${RED}✗ Failed to start Docker containers${NC}"
    exit 1
fi

# Set up database
print_header "Setting up database"

echo "Creating database tables and initializing database..."
source backend/venv/bin/activate && python backend/scripts/db_migrations.py --action create

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${RED}✗ Failed to initialize database${NC}"
    echo "You may need to run this manually after updating your .env file"
fi

# Print success message
print_header "Development environment setup complete!"

echo -e "You can now start the application:

Backend:
  ${GREEN}cd backend && source venv/bin/activate && uvicorn app.main:app --reload${NC}

Frontend:
  ${GREEN}cd frontend && npm run dev${NC}

API Documentation:
  ${GREEN}http://localhost:8000/api/v1/docs${NC}

Frontend:
  ${GREEN}http://localhost:3000${NC}
"

echo -e "${YELLOW}Note: Make sure to update your environment variables in backend/.env${NC}"