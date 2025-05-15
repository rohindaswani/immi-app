#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Installing additional dependencies ===${NC}\n"

# Install additional packages
echo -e "Installing email_validator..."
pip3 install email_validator

# Install other common packages
echo -e "Installing other common packages..."
pip3 install fastapi uvicorn sqlalchemy pymongo redis httpx

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install additional dependencies.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Additional dependencies installed successfully!${NC}"
echo -e "You can now try running the backend with: ${YELLOW}./use_hardcoded_config.sh${NC}"