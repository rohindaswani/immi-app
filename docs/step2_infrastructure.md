# Step 2: Core Technical Infrastructure

This document outlines the core technical infrastructure set up for the Immigration Advisor application.

## Repository Structure

The repository follows a standard structure with separate directories for backend, frontend, and shared resources:

```
immigration_app/
├── backend/              # Python FastAPI backend
├── frontend/             # React frontend 
├── docker-compose.yml    # Docker Compose configuration
├── .github/              # GitHub Actions workflows
├── scripts/              # Development scripts
└── docs/                 # Documentation
```

## Development Environment

The development environment is configured using Docker Compose with the following services:

- **PostgreSQL**: Primary relational database for structured data
- **MongoDB**: Document storage for immigration documents
- **Redis**: Caching and task queue
- **API**: FastAPI backend service 
- **Web**: React frontend service (currently commented out)

## Continuous Integration/Continuous Deployment (CI/CD)

CI/CD is set up using GitHub Actions with the following workflows:

- **Backend CI**: Tests and builds the backend application
  - Runs on push to main/develop branches and pull requests
  - Tests with PostgreSQL and MongoDB services
  - Runs linting, tests, and Docker build

- **Frontend CI**: Tests and builds the frontend application
  - Runs on push to main/develop branches and pull requests
  - Lints and builds the React application
  - Builds Docker image on successful tests

## Security Controls

The following security controls have been implemented:

1. **Authentication & Authorization**:
   - JWT-based authentication with refresh tokens
   - Password hashing with bcrypt
   - Access token expiration (30 minutes)
   - Refresh token rotation (7 days)

2. **API Security**:
   - Security headers middleware (X-XSS-Protection, CSP, etc.)
   - CORS configuration for cross-origin requests
   - Request logging and monitoring
   - Rate limiting
   - Global exception handling

3. **Data Protection**:
   - Secure storage service for documents (S3-compatible)
   - Server-side encryption for stored files
   - Secure file access via presigned URLs
   - Database connection security

4. **Infrastructure Security**:
   - Docker container security settings
   - Environment-specific configuration
   - Security scanning scripts

## Database Foundation

The database foundation includes:

1. **PostgreSQL Schema**: 
   - User management (users, settings)
   - Immigration profiles and statuses
   - Travel and address history
   - Document metadata
   - Timeline events
   - Notifications

2. **MongoDB Collections**:
   - Document storage
   - Full-text search capabilities

3. **Database Migrations**:
   - Migration script for schema management
   - Seed data for development

## Environment Configuration

Environment-specific configuration is managed through:

1. **.env Files**: 
   - Environment variables for different environments
   - Sensitive information separation

2. **Configuration Classes**:
   - Settings for different components
   - Environment-specific overrides

## Security Scanning

Security scanning is implemented through:

1. **security_scan.sh Script**:
   - Dependency vulnerability scanning
   - Code security analysis
   - Docker configuration checks
   - Security recommendations

## Deployment Environments

The infrastructure is designed to support:

1. **Development**: Local development environment
2. **Staging**: Pre-production testing
3. **Production**: Live application environment

Each environment has its own configuration and security settings.