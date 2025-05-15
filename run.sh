#!/bin/bash

# Print commands and their execution status
set -x

# Start database containers
echo "Starting database containers..."
docker-compose up -d postgres mongodb redis

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
sleep 5

# Initialize the database
echo "Initializing the database..."
cd backend
python -m scripts.db_migrations --action create

# Run the backend server
echo "Starting the backend server..."
cd /Users/rohindaswani/Projects/immigration_app/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000