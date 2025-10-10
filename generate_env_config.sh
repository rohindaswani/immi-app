#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Immigration Advisor - Environment Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Generate a secure secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo -e "${GREEN}✓ Generated new JWT secret key${NC}\n"

# Prompt for Google OAuth credentials
echo -e "${YELLOW}Please enter your NEW Google OAuth credentials:${NC}"
echo -e "${RED}(You must regenerate these from Google Cloud Console first!)${NC}\n"

read -p "Google Client ID: " GOOGLE_CLIENT_ID
read -p "Google Client Secret: " GOOGLE_CLIENT_SECRET

# Optional credentials
echo -e "\n${YELLOW}Optional: Enter additional API keys (press Enter to skip):${NC}\n"
read -p "OpenAI API Key (optional): " OPENAI_API_KEY
read -p "Pinecone API Key (optional): " PINECONE_API_KEY

# Create the .zshrc snippet
SNIPPET_FILE="$HOME/.immigration_advisor_env"

cat > "$SNIPPET_FILE" << EOF
# Immigration Advisor Environment Variables
# Generated on $(date)

# Google OAuth Credentials
export GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID"
export GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET"

# JWT Secret Key (auto-generated)
export SECRET_KEY="$SECRET_KEY"
EOF

if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "" >> "$SNIPPET_FILE"
    echo "# OpenAI API Key" >> "$SNIPPET_FILE"
    echo "export OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> "$SNIPPET_FILE"
fi

if [ ! -z "$PINECONE_API_KEY" ]; then
    echo "" >> "$SNIPPET_FILE"
    echo "# Pinecone API Key" >> "$SNIPPET_FILE"
    echo "export PINECONE_API_KEY=\"$PINECONE_API_KEY\"" >> "$SNIPPET_FILE"
fi

echo -e "\n${GREEN}✓ Configuration saved to: $SNIPPET_FILE${NC}\n"

# Display the snippet
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Add this to your ~/.zshrc file:${NC}"
echo -e "${BLUE}========================================${NC}\n"

cat "$SNIPPET_FILE"

echo -e "\n${BLUE}========================================${NC}"

# Ask if they want to auto-append
echo -e "\n${YELLOW}Would you like to automatically add this to your ~/.zshrc?${NC}"
read -p "This will append to the end of your ~/.zshrc file (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "" >> ~/.zshrc
    cat "$SNIPPET_FILE" >> ~/.zshrc
    echo -e "${GREEN}✓ Added to ~/.zshrc${NC}\n"
    echo -e "${YELLOW}Run this command to reload your shell:${NC}"
    echo -e "${BLUE}source ~/.zshrc${NC}\n"
else
    echo -e "${YELLOW}To manually add, run:${NC}"
    echo -e "${BLUE}cat $SNIPPET_FILE >> ~/.zshrc${NC}"
    echo -e "${BLUE}source ~/.zshrc${NC}\n"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. ${BLUE}source ~/.zshrc${NC} (if not done yet)"
echo -e "2. Verify: ${BLUE}echo \$GOOGLE_CLIENT_ID${NC}"
echo -e "3. Start databases: ${BLUE}./start_databases.sh${NC}"
echo -e "4. Start backend: ${BLUE}./start_backend.sh${NC}\n"

echo -e "${RED}IMPORTANT: Delete the old OAuth client from Google Cloud Console!${NC}"
echo -e "Go to: ${BLUE}https://console.cloud.google.com/apis/credentials${NC}\n"
