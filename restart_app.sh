#!/bin/bash

# Script to restart both frontend and backend

# Stop all running processes related to the app
echo "Stopping any running processes..."
pkill -f "npm run dev" || true
pkill -f "python -m uvicorn" || true

# Clear terminal
clear

echo "===== Restarting Immigration Advisor App ====="
echo "$(date)"

# Start backend in background
echo "Starting backend..."
cd backend
source ./venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to initialize
echo "Waiting for backend to initialize..."
sleep 5

# Start frontend in background
echo "Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo ""
echo "=== App started successfully ==="
echo "Backend running on: http://localhost:8000"
echo "Frontend running on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for Ctrl+C and then clean up
trap "echo 'Stopping services...'; kill $BACKEND_PID; kill $FRONTEND_PID; exit" INT
wait