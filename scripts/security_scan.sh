#!/bin/bash

# Security scanning script for Immigration Advisor app

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print section header
print_header() {
    echo -e "\n${YELLOW}====== $1 ======${NC}\n"
}

# Print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $3${NC}"
    fi
}

# Check Python dependencies for security issues
print_header "Checking Python dependencies for security issues"

if command -v safety >/dev/null 2>&1; then
    safety check -r backend/requirements.txt
    print_status $? "No known security issues in Python dependencies" "Security issues found in Python dependencies"
else
    echo "Installing safety..."
    pip install safety
    safety check -r backend/requirements.txt
    print_status $? "No known security issues in Python dependencies" "Security issues found in Python dependencies"
fi

# Check JavaScript dependencies for security issues
print_header "Checking JavaScript dependencies for security issues"

if [ -d "frontend/node_modules" ]; then
    cd frontend && npm audit
    print_status $? "No known security issues in npm dependencies" "Security issues found in npm dependencies"
else
    echo -e "${YELLOW}! Frontend dependencies not installed, skipping npm audit${NC}"
fi

# Check for environment variables in .env file
print_header "Checking environment variables"

if [ -f "backend/.env" ]; then
    # Check for default/weak values
    if grep -q "SECRET_KEY=your-secret-key-here" backend/.env; then
        echo -e "${RED}✗ Default SECRET_KEY found in .env${NC}"
    else
        echo -e "${GREEN}✓ SECRET_KEY has been changed from default${NC}"
    fi
else
    echo -e "${YELLOW}! No .env file found, create one from .env.example${NC}"
fi

# Check Docker configuration
print_header "Checking Docker configuration"

# Check if running as non-root user
if grep -q "USER " backend/Dockerfile && grep -q "USER " frontend/Dockerfile; then
    echo -e "${GREEN}✓ Docker containers configured to run as non-root user${NC}"
else
    echo -e "${YELLOW}! Consider adding 'USER' directive to Dockerfiles to run as non-root${NC}"
fi

# Check Python code for security issues with bandit
print_header "Scanning Python code for security issues"

if command -v bandit >/dev/null 2>&1; then
    bandit -r backend/app/ -f txt
    print_status $? "No security issues found in Python code" "Security issues found in Python code"
else
    echo "Installing bandit..."
    pip install bandit
    bandit -r backend/app/ -f txt
    print_status $? "No security issues found in Python code" "Security issues found in Python code"
fi

# Check for credentials in git history
print_header "Checking git history for credentials"

if command -v trufflehog >/dev/null 2>&1; then
    trufflehog .
    print_status $? "No credentials found in git history" "Potential credentials found in git history"
else
    echo -e "${YELLOW}! trufflehog not installed, skipping git history check${NC}"
    echo "Consider installing trufflehog: pip install trufflehog"
fi

# SSL/TLS recommendations
print_header "SSL/TLS Recommendations"

echo -e "${YELLOW}! Remember to configure SSL/TLS in production:${NC}"
echo "- Use HTTPS for all communications"
echo "- Implement HSTS headers"
echo "- Use modern TLS protocols (TLS 1.2+)"
echo "- Configure secure ciphers"
echo "- Obtain valid SSL certificate from a trusted CA"

# General security recommendations
print_header "General Security Recommendations"

echo "1. Implement rate limiting for all API endpoints"
echo "2. Set up proper CORS configuration for production"
echo "3. Use the principle of least privilege for all accounts"
echo "4. Regularly update all dependencies"
echo "5. Enable security headers (CSP, X-Frame-Options, etc.)"
echo "6. Implement multi-factor authentication"
echo "7. Set up regular security scanning and monitoring"
echo "8. Review and test file upload security"
echo "9. Encrypt sensitive data at rest and in transit"
echo "10. Implement secure session management"

echo -e "\n${YELLOW}This scan provides basic security checks. For a comprehensive security assessment, consider professional penetration testing.${NC}"