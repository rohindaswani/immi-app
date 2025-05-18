#!/bin/bash

# Script to fix Google OAuth configuration issues

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Banner
echo -e "${GREEN}===== Google OAuth Configuration Fix Script =====${NC}"
echo -e "This script will fix Google OAuth configuration settings"

# Define config file path
CONFIG_FILE="backend/app/core/config.py"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Config file not found at $CONFIG_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Checking for existing Google OAuth settings...${NC}"

# Check if the settings file already has Google OAuth settings
if grep -q "GOOGLE_CLIENT_ID" "$CONFIG_FILE"; then
    HAS_CLIENT_ID=true
    echo -e "  - GOOGLE_CLIENT_ID: ${GREEN}Found${NC}"
else
    HAS_CLIENT_ID=false
    echo -e "  - GOOGLE_CLIENT_ID: ${RED}Missing${NC}"
fi

# Check for server URL methods vs properties
if grep -q "def SERVER_URL" "$CONFIG_FILE"; then
    URL_AS_METHOD=true
    echo -e "  - SERVER_URL: ${GREEN}Defined as method${NC}"
elif grep -q "@property" "$CONFIG_FILE" && grep -q "def SERVER_URL" "$CONFIG_FILE"; then
    URL_AS_PROPERTY=true
    echo -e "  - SERVER_URL: ${GREEN}Defined as property${NC}"
else
    URL_AS_METHOD=false
    URL_AS_PROPERTY=false
    echo -e "  - SERVER_URL: ${RED}Missing${NC}"
fi

# Adding server host/port/protocol if missing
if ! grep -q "SERVER_HOST" "$CONFIG_FILE"; then
    echo -e "${YELLOW}Adding SERVER_HOST, SERVER_PORT, SERVER_PROTOCOL settings...${NC}"
    # Find the API Configuration section and add after
    sed -i '' '/# API Configuration/a\\
    # Base URL\\
    SERVER_HOST: str = "localhost"\\
    SERVER_PORT: int = 8000\\
    SERVER_PROTOCOL: str = "http"\\
    ' "$CONFIG_FILE"
fi

# Adding Google OAuth settings if missing
if [ "$HAS_CLIENT_ID" = false ]; then
    echo -e "${YELLOW}Adding Google OAuth settings...${NC}"
    # Find the end of the class and add before
    sed -i '' '/settings = Settings/i\\
    # GOOGLE OAUTH\\
    GOOGLE_CLIENT_ID: str = "your-google-client-id"\\
    GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"\\
    GOOGLE_REDIRECT_URI: str = "/api/v1/auth/google/callback"\\
    \\
    def SERVER_URL(self) -> str:\\
        return f"{self.SERVER_PROTOCOL}://{self.SERVER_HOST}:{self.SERVER_PORT}"\\
    \\
    def GOOGLE_AUTHORIZE_URL(self) -> str:\\
        return "https://accounts.google.com/o/oauth2/auth"\\
    \\
    def GOOGLE_TOKEN_URL(self) -> str:\\
        return "https://oauth2.googleapis.com/token"\\
    \\
    def GOOGLE_USER_INFO_URL(self) -> str:\\
        return "https://www.googleapis.com/oauth2/v3/userinfo"\\
    \\
    def GOOGLE_CALLBACK_URL(self) -> str:\\
        return f"{self.SERVER_URL()}{self.API_V1_STR}{self.GOOGLE_REDIRECT_URI}"\\
    ' "$CONFIG_FILE"
fi

echo -e "${GREEN}Configuration updated successfully!${NC}"
echo -e "${YELLOW}Remember to update GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET with your actual values${NC}"

# Check GoogleAuthService file
GOOGLE_AUTH_FILE="backend/app/services/google_auth.py"

if [ -f "$GOOGLE_AUTH_FILE" ]; then
    echo -e "${YELLOW}Checking GoogleAuthService...${NC}"
    
    # Check if the file needs updates for method calls vs property access
    if grep -q "settings.GOOGLE_AUTHORIZE_URL[^(]" "$GOOGLE_AUTH_FILE"; then
        echo -e "  - Updating property references to method calls..."
        sed -i '' 's/settings.GOOGLE_AUTHORIZE_URL/settings.GOOGLE_AUTHORIZE_URL()/g' "$GOOGLE_AUTH_FILE"
        sed -i '' 's/settings.GOOGLE_TOKEN_URL/settings.GOOGLE_TOKEN_URL()/g' "$GOOGLE_AUTH_FILE" 
        sed -i '' 's/settings.GOOGLE_USER_INFO_URL/settings.GOOGLE_USER_INFO_URL()/g' "$GOOGLE_AUTH_FILE"
        sed -i '' 's/settings.GOOGLE_CALLBACK_URL/settings.GOOGLE_CALLBACK_URL()/g' "$GOOGLE_AUTH_FILE"
        sed -i '' 's/settings.SERVER_URL/settings.SERVER_URL()/g' "$GOOGLE_AUTH_FILE"
    fi
    
    echo -e "${GREEN}GoogleAuthService updated successfully!${NC}"
else
    echo -e "${RED}GoogleAuthService file not found at $GOOGLE_AUTH_FILE${NC}"
fi

echo -e "${GREEN}All fixes applied. Please restart your backend server.${NC}"