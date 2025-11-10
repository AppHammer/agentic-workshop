# Tasker Platform - Project Structure Guidelines

## Directory Organization

The Tasker Platform is a full-stack marketplace application connecting local workers (taskers) with customers who need work done. The project is organized into distinct backend and frontend directories to maintain clear separation of concerns.

```
agentic-workshop/
├── app/                    # Primary source code for the application
│   ├── backend/            # Python/FastAPI backend application
│   │   ├── main.py         # FastAPI app with all API endpoints
│   │   ├── database.py     # SQLAlchemy models and database configuration
│   │   ├── schemas.py      # Pydantic schemas for request/response validation
│   │   ├── auth.py         # JWT authentication and password hashing
│   │   ├── requirements.txt # Python dependencies
│   │   └── tasker.db       # SQLite database file (gitignored)
│   └── frontend/           # React frontend application
│       ├── public/         # Static assets and index.html
│       ├── src/            # React source code
│       │   ├── components/ # React components
│       │   ├── App.js      # Main app component with routing
│       │   ├── api.js      # Axios API service layer
│       │   ├── index.js    # React entry point
│       │   └── index.css   # Global styles
│       ├── package.json    # Node.js dependencies and scripts
│       └── package-lock.json
├── tests/                  # All test files (unit, integration, e2e)
├── docs/                   # Project documentation
│   └── tasker.md           # Platform specification and requirements
├── prerequisites/          # Installation and setup scripts
│   └── install-using-winget.sh
├── .roo/                   # Roo AI configuration and templates
├── .gitignore              # Git ignore patterns
└── README.md               # Project overview and setup instructions
```

## Naming Conventions

### Backend (Python) Files
- **Modules**: `lowercase_with_underscores.py` (e.g., `database.py`, `auth.py`)
- **Database Models**: Defined in `database.py`
- **API Schemas**: Defined in `schemas.py`
- **Tests**: `test_*.py` (e.g., `test_auth.py`)

### Frontend (React/JavaScript) Files
- **Components**: `PascalCase.js` (e.g., `Login.js`, `CustomerDashboard.js`, `TaskList.js`)
- **Services**: `camelCase.js` (e.g., `api.js`)
- **Utilities**: `camelCase.js`
- **Styles**: `camelCase.css` (e.g., `index.css`)

### Code
- **Classes/Types/Enums**: `PascalCase`
  - Backend: `User`, `Task`, `UserRole`, `TaskStatus`
  - Frontend: React component names
- **Functions/Methods**: `camelCase`
  - Backend: `get_password_hash()`, `create_access_token()`, `get_current_user()`
  - Frontend: `handleSubmit()`, `loadTasks()`, `getCurrentUser()`
- **Constants/Enums**: `UPPER_SNAKE_CASE`
  - Backend: `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
  - Frontend: `API_URL`
- **Variables**: `camelCase` (Frontend) / `snake_case` (Backend)
  - Backend: `db_user`, `hashed_password`, `access_token`
  - Frontend: `formData`, `currentUser`, `showCreateForm`

## Import Patterns

### Backend (Python)

#### Import Order
1. Standard library imports (e.g., `from datetime import datetime`)
2. Third-party library imports (e.g., `from fastapi import FastAPI`)
3. Local application imports (e.g., `import database`, `import schemas`, `import auth`)

#### Import Style
- Use explicit imports from local modules: `from database import User, Task`
- Import entire local modules when multiple items needed: `import database`, `import schemas`
- Use relative imports within the same directory only when appropriate

### Frontend (React/JavaScript)

#### Import Order
1. External dependencies (e.g., `import React from 'react'`)
2. Internal absolute imports (e.g., `import { getCurrentUser } from './api'`)
3. Internal relative imports (e.g., `import Login from './components/Login'`)
4. Style imports (e.g., `import './index.css'`)

#### Import Style
- Use relative imports for components within the same feature: `'./components/Login'`
- API functions imported from centralized service: `import { login, register } from './api'`
- React Router components use named imports: `import { BrowserRouter as Router, Routes, Route }`

## Code Structure Patterns

### Backend Module/File Organization
1. Imports
2. Constants and configuration
3. Application/database initialization
4. Model/schema definitions (if applicable)
5. Helper functions
6. Main endpoint/route handlers
7. Main execution block (if applicable)

Example from [`main.py`](app/backend/main.py):
1. Imports (lines 1-10)
2. FastAPI app initialization (line 12)
3. Middleware configuration (lines 14-21)
4. Startup event handlers (lines 23-26)
5. API endpoint definitions (lines 28-413)
6. Main execution (lines 415-417)

### Frontend Component Organization
1. Imports
2. Component function definition with props
3. State declarations (useState hooks)
4. Effect hooks (useEffect)
5. Helper functions
6. Event handlers
7. JSX return statement

Example from [`Login.js`](app/frontend/src/components/Login.js):
1. Imports (lines 1-3)
2. Component function (line 5)
3. State declarations (lines 6-9)
4. Event handlers (lines 11-22)
5. JSX return (lines 24-57)

### Guiding Principles
- **Clarity**: Code is organized top-to-bottom in logical execution flow
- **Consistency**: Similar files follow the same structure (all API endpoints, all React components)
- **Single Responsibility**: Each file has one primary purpose
  - Backend: Each model in `database.py`, schemas in `schemas.py`, auth in `auth.py`
  - Frontend: One component per file, centralized API calls in `api.js`

## Code Organization Principles

1. **Modularity**: Code is organized into independent modules with clear boundaries
   - Backend: Separate modules for database, schemas, auth, and main API
   - Frontend: Separate components for each UI view, centralized API service

2. **Separation of Concerns**: 
   - Backend: Database models (SQLAlchemy) separate from API schemas (Pydantic)
   - Frontend: UI components separate from API logic, routing separate from components
   - Authentication logic isolated in dedicated module

3. **Layered Architecture**:
   - **Data Layer**: SQLAlchemy models define database structure
   - **API Layer**: FastAPI endpoints handle HTTP requests/responses
   - **Validation Layer**: Pydantic schemas validate data
   - **Auth Layer**: JWT-based authentication protects endpoints
   - **UI Layer**: React components render user interface
   - **Service Layer**: API service module abstracts HTTP calls

4. **Testability**: Structure designed for straightforward testing
   - Backend: Dependency injection with `Depends()` for easy mocking
   - Frontend: Component-based architecture allows isolated testing
   - Separate test directory for all test files

5. **Consistency**: Follow established patterns throughout the codebase
   - All API endpoints follow same pattern: validation → business logic → response
   - All React components follow hooks pattern with consistent structure
   - All database operations use SQLAlchemy ORM consistently

## Module Boundaries

### Backend

- **Public API**: All HTTP endpoints in [`main.py`](app/backend/main.py) are public APIs
- **Internal Implementation**: Database models, auth functions, and utility functions are internal
- **Dependency Direction**: 
  - `main.py` depends on `database.py`, `schemas.py`, and `auth.py`
  - `auth.py` depends on `database.py`
  - `schemas.py` depends on `database.py` (for enums only)
  - No circular dependencies allowed

### Frontend

- **Public API**: Component exports are the public API
- **Internal Implementation**: Component state and helper functions are internal
- **Dependency Direction**:
  - Components depend on `api.js` service layer
  - Components depend on React Router for navigation
  - `api.js` is the single point of contact with backend
  - Components should not make direct axios calls (use `api.js`)

### Cross-Cutting Concerns

- **Authentication**: Frontend stores JWT token, backend validates on each request
- **Data Flow**: Frontend → API Service → Backend Endpoints → Database Models
- **State Management**: Currently local component state; consider global state if complexity grows
- **Error Handling**: Backend returns structured errors, frontend displays to user

## Code Size Guidelines

### Backend (Python)
- **File Size**: < 500 lines (current [`main.py`](app/backend/main.py) is 417 lines - acceptable for MVP)
- **Function/Method Size**: < 50 lines
- **Class Complexity**: < 10 methods per class
- **Nesting Depth**: Maximum of 3 levels

### Frontend (React)
- **File Size**: < 400 lines
- **Component Size**: < 200 lines (consider splitting if larger)
- **Function Size**: < 50 lines
- **Nesting Depth**: Maximum of 3 levels in JSX

### When to Refactor
- If a file exceeds size guidelines, consider splitting by responsibility
- If a function has too many parameters (>5), consider using an object
- If components share logic, extract to custom hooks
- If API endpoints become too numerous, consider grouping into routers

## Documentation Standards

### Backend (Python)

- **Module Docstrings**: Each Python file should have a module-level docstring explaining its purpose
- **Function Docstrings**: All public functions must have docstrings following Google style
  ```python
  def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
      """Creates a JWT access token for authentication.
      
      Args:
          data: Dictionary containing user information to encode
          expires_delta: Optional custom expiration time
          
      Returns:
          Encoded JWT token as string
      """
  ```
- **Type Hints**: All function signatures must include type hints
- **Complex Logic**: Add inline comments for business logic and non-obvious operations

### Frontend (React/JavaScript)

- **Component Documentation**: JSDoc comments for complex components
  ```javascript
  /**
   * CustomerDashboard - Main dashboard for customers to manage tasks
   * @param {Object} user - Current authenticated user object
   */
  ```
- **Function Comments**: Document non-obvious logic and business rules
- **PropTypes**: Consider adding PropTypes or TypeScript for better type safety
- **API Documentation**: Each API function in `api.js` should have comment explaining endpoint

### Project Documentation

- **README.md**: Setup instructions, prerequisites, and getting started guide
- **docs/tasker.md**: Complete platform specification and business requirements
- **API Documentation**: Consider adding Swagger/OpenAPI docs for backend
- **Component Documentation**: Consider Storybook for component library documentation

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.5.0
- **Authentication**: python-jose 3.3.0 (JWT), bcrypt/passlib for passwords
- **Database**: SQLite (Development/MVP)
- **Server**: Uvicorn 0.24.0
- **Testing**: pytest 7.4.3, pytest-asyncio

### Frontend
- **Framework**: React 18.2.0
- **Routing**: react-router-dom 6.20.0
- **HTTP Client**: axios 1.6.2
- **Build Tool**: react-scripts 5.0.1 (Create React App)
- **Proxy**: Configured to proxy API requests to `http://localhost:8000`

### Development Tools
- **Version Control**: Git with comprehensive `.gitignore`
- **Code Formatting**: Follow language-specific standards (PEP 8 for Python, Prettier for JS)
- **AI Assistant**: Roo AI configuration in `.roo/` directory

## Running the Application

### Backend
```bash
cd app/backend
pip install -r requirements.txt
python main.py
# Server runs on http://localhost:8000
```

### Frontend
```bash
cd app/frontend
npm install
npm start
# Development server runs on http://localhost:3000
```

### Database
- SQLite database (`tasker.db`) is automatically created on first run
- Database schema defined in [`database.py`](app/backend/database.py)
- Migrations: Currently handled by SQLAlchemy's `create_all()` (consider Alembic for production)

## Future Considerations

### Planned Enhancements
- Add comprehensive test coverage
- Implement proper logging
- Add API documentation (Swagger/OpenAPI)
- Consider migrating to PostgreSQL for production
- Add environment-based configuration
- Implement proper secrets management (move away from hardcoded `SECRET_KEY`)
- Add rate limiting and request validation
- Consider state management library (Redux/Zustand) if frontend complexity grows
- Add WebSocket support for real-time messaging
- Implement file upload for task attachments
- Add payment integration

### Security Considerations
- Move `SECRET_KEY` to environment variables
- Implement CORS more restrictively for production
- Add request rate limiting
- Implement HTTPS in production
- Add input sanitization
- Consider implementing refresh tokens
- Add password complexity requirements
- Implement account lockout after failed attempts

### Scalability Considerations
- Consider breaking [`main.py`](app/backend/main.py) into multiple router modules
- Implement caching layer (Redis) for frequently accessed data
- Add database connection pooling
- Consider microservices architecture if feature set expands
- Implement CDN for frontend static assets
- Add database indexing for performance
- Consider message queue for background tasks