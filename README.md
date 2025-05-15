# Immigration Advisor Application

A comprehensive application to help users manage their immigration status, documents, and compliance, with an initial focus on H1-B visa holders.

## Project Overview

The Immigration Advisor helps users with:

- Securely storing and managing immigration documents
- Tracking visa status, expiration dates, and compliance requirements
- Managing travel, address, and employment history
- Receiving notifications for important deadlines and check-ins
- Getting assistance through an AI-powered chat interface

## Project Status

This project is currently in early development (Phase 0-1). The focus is on setting up the core infrastructure and implementing the basic user authentication and profile management functionality.

### Completed Features
- Core technical infrastructure setup
- Database schema design
- API endpoint definition
- Development environment configuration
- CI/CD setup with GitHub Actions
- Security controls implementation

### In Progress
- User authentication system
- Profile management functionality
- Document storage and management

## Tech Stack

### Backend
- **Framework**: Python with FastAPI
- **Database**: PostgreSQL (structured data) and MongoDB (document storage)
- **Caching/Queues**: Redis
- **Authentication**: JWT with OAuth2
- **AI Integration**: LangChain with vector search capabilities

### Frontend
- **Framework**: React with TypeScript
- **State Management**: Redux Toolkit
- **UI Components**: Material UI
- **Forms**: Formik with Yup validation
- **API Client**: Axios

### DevOps
- **Containerization**: Docker and Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: Pytest (backend) and Vitest (frontend)

## Project Structure

```
immigration_app/
├── .github/workflows/        # GitHub Actions workflow configurations
├── backend/                  # Python FastAPI backend
│   ├── app/                  # Application code
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core functionality and security
│   │   ├── db/               # Database models and connections
│   │   ├── schemas/          # Pydantic schemas for validation
│   │   ├── services/         # Business logic
│   │   └── ai/               # AI integration
│   ├── scripts/              # Utility scripts
│   ├── tests/                # Test suite
│   ├── Dockerfile            # Docker configuration
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React frontend
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Application pages
│   │   ├── store/            # Redux state management
│   │   ├── api/              # API integration
│   │   └── utils/            # Utility functions
│   ├── Dockerfile            # Docker configuration
│   └── package.json          # NPM dependencies
├── scripts/                  # Development and utility scripts
├── docs/                     # Documentation files
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # Project documentation
```

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend)
- Git

### Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/immigration_app.git
   cd immigration_app
   ```

2. Make setup scripts executable:
   ```bash
   sh make_scripts_executable.sh
   ```

3. Set up the development environment:
   ```bash
   ./scripts/setup_dev.sh
   ```
   This will:
   - Check for required dependencies
   - Set up Python virtual environment
   - Install dependencies
   - Create necessary configuration files
   - Start Docker containers

4. Run the application:
   ```bash
   ./run_app.sh
   ```
   This will:
   - Start the database containers
   - Initialize the database if needed
   - Start the backend server

5. Access the application:
   - Backend API: [http://localhost:8000/](http://localhost:8000/)
   - API Documentation: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
   - Health Check: [http://localhost:8000/health](http://localhost:8000/health)

6. To run the frontend (in a separate terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Frontend: [http://localhost:3000/](http://localhost:3000/)

### Testing

To run the automated tests:

```bash
# Run backend tests
cd backend
python -m pytest

# Run frontend tests
cd frontend
npm test
```

To check the overall application functionality:
```bash
./test_app.sh
```

### Security Scanning

To run a security scan of the codebase:
```bash
./scripts/security_scan.sh
```

## Development Plan

The development follows a phased approach:

1. **Phase 0**: Planning and Foundation (current phase)
   - System architecture and database design
   - Development environment setup
   - Security controls implementation

2. **Phase 1**: User Authentication & Profile
   - User registration and login
   - Profile creation and management
   - Role-based access control

3. **Phase 2**: Document Management
   - Secure document upload and storage
   - Document categorization and metadata
   - Document expiration tracking

4. **Phase 3**: Core Data Tracking
   - Travel history management
   - Address and employment history
   - Compliance validation

5. **Phase 4**: Chat Interface & Notifications
   - AI-powered chat assistance
   - Deadline notifications
   - Monthly check-ins

6. **Phase 5**: MVP Integration & Polish
   - Integrated timeline view
   - Dashboard with compliance indicators
   - Final testing and refinement

## Database Schema

The application uses a hybrid database approach:

- **PostgreSQL**: Stores structured data like user profiles, immigration statuses, travel history, and document metadata
- **MongoDB**: Stores document contents and unstructured data
- **Vector Database**: Planned for semantic search capabilities with the AI assistant

The complete database schema is available in the `immigration-advisor-schema.md` document.

## Contributing

Please read the development plan and schema documents before contributing. The `immigration-advisor-mvp-plan.md` and `immigration-advisor-user-stories.md` files provide detailed information about the project goals and requirements.

## License

[Specify your license here]