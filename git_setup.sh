#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

APP_PATH="/Users/rohindaswani/Projects/immigration_app"
cd "$APP_PATH"

echo -e "${YELLOW}=== Setting up Git repository ===${NC}\n"

# Initialize git repository
echo "Initializing git repository..."
git init

# Create .gitignore file
echo "Creating .gitignore file..."
cat > .gitignore << 'EOF'
# Backend
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
venv/
.env
.venv
.pytest_cache/
htmlcov/
.coverage
.coverage.*

# Frontend
node_modules/
/frontend/dist
/frontend/build
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
.DS_Store
coverage/
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Docker
.docker/
docker-compose.override.yml
EOF

# Add all files
echo "Adding files to git..."
git add .

# Commit
echo "Creating initial commit..."
git commit -m "Initial commit: Immigration Advisor application setup

- Created project structure
- Set up FastAPI backend with basic endpoint structure
- Set up React frontend with basic components
- Added database models and schemas
- Configured Docker containers for development
- Added documentation"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to commit changes.${NC}"
    echo "You may need to set up git user.name and user.email:"
    echo "git config --global user.name \"Your Name\""
    echo "git config --global user.email \"your.email@example.com\""
    exit 1
fi

echo -e "\n${GREEN}Git repository initialized successfully!${NC}"
echo -e "Next steps:"
echo -e "1. ${YELLOW}Add a remote repository:${NC}"
echo -e "   git remote add origin <repository-url>"
echo -e "2. ${YELLOW}Push to remote:${NC}"
echo -e "   git push -u origin main"