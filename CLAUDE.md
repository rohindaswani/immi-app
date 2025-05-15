# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Immigration Advisor application designed to help users manage their immigration status, particularly focused on H1-B visa holders initially. The application provides document storage, status tracking, compliance checks, notifications, and an AI-powered chat interface for immigration assistance.

### Core Features

- User authentication and profile management
- Secure document storage and organization
- Immigration status tracking
- Travel, address, and employment history management
- Notification system for deadlines and compliance
- AI-powered chat assistance
- Analytics and reporting

## Tech Stack

### Backend
- Python with FastAPI
- PostgreSQL for structured data (users, profiles, statuses, etc.)
- MongoDB for document storage
- Redis for caching and background tasks
- Celery for background processing
- JWT with OAuth2 for authentication

### Frontend
- React with TypeScript
- Redux Toolkit for state management
- Material UI for components
- Axios for API integration

### AI Components
- Vector database (Pinecone) for semantic search
- LangChain for AI integration
- Document OCR capabilities

## Development Setup Commands

### Backend Setup (once implemented)
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (once implemented)
python -m scripts.db_migrations

# Start the backend server
uvicorn app.main:app --reload
```

### Frontend Setup (once implemented)
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

### Database Setup (once implemented)
```bash
# Local PostgreSQL setup
docker run --name immigration-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres

# Local MongoDB setup
docker run --name immigration-mongodb -p 27017:27017 -d mongo

# Local Redis setup
docker run --name immigration-redis -p 6379:6379 -d redis
```

## Testing Commands (once implemented)

### Backend Tests
```bash
# Run all backend tests
pytest

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Frontend Tests
```bash
# Run frontend tests
cd frontend
npm test

# Run tests with coverage
npm test -- --coverage
```

## Code Structure

The application follows a modular structure based on the MVP development plan:

### Backend
- `app/` - Main application package
  - `api/` - API endpoints organized by resource
  - `core/` - Core functionality (config, security)
  - `db/` - Database models and connections
  - `schemas/` - Pydantic schemas for validation
  - `services/` - Business logic
  - `ai/` - AI integration components

### Frontend
- `src/` - Source code
  - `components/` - UI components
  - `pages/` - Application pages
  - `store/` - Redux state management
  - `api/` - API integration
  - `utils/` - Utility functions

## Development Guidelines

- Follow the RESTful API design outlined in the schema document
- Implement proper validation for all endpoints
- Ensure security best practices are followed for handling sensitive immigration data
- Maintain comprehensive test coverage
- Document all new features and API endpoints

## Deployment (once implemented)

### Development
```bash
# Deploy to development environment
npm run deploy:dev
```

### Production
```bash
# Deploy to production environment
npm run deploy:prod
```

## Important Notes

- This is a new project under active development
- The MVP focuses on H1-B visa management as outlined in the planning documents
- Security and data privacy are critical priorities given the sensitive nature of immigration data