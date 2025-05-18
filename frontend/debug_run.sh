#!/bin/bash

# Debug script for running the frontend

# Clear terminal
clear

echo "===== Frontend Debug Run Script ====="
echo "Current directory: $(pwd)"
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

# Check for node_modules
if [ ! -d "node_modules" ]; then
  echo "Warning: node_modules directory not found"
  echo "Installing dependencies..."
  npm install
else
  echo "node_modules directory found"
  echo "Total modules: $(find node_modules -type d -maxdepth 1 | wc -l)"
fi

# Check for required files
echo "Checking for required files..."
for file in "package.json" "vite.config.ts" "index.html" "src/index.tsx" "src/App.tsx" "src/SimpleFallbackApp.tsx"; do
  if [ -f "$file" ]; then
    echo "✅ $file exists"
  else
    echo "❌ $file is missing"
  fi
done

# Check if port 3000 is already in use
PORT_IN_USE=$(lsof -i :3000 | grep LISTEN)
if [ ! -z "$PORT_IN_USE" ]; then
  echo "Warning: Port 3000 is already in use"
  echo "$PORT_IN_USE"
  echo "Attempting to kill the process..."
  kill $(lsof -t -i:3000) 2>/dev/null || echo "Failed to kill process"
else
  echo "Port 3000 is available"
fi

echo "Starting Vite dev server with debugging..."
echo "=========================================="
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Run with debug flag
DEBUG=vite:* npm run dev