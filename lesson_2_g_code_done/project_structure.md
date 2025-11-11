# Tasker Marketplace Platform - Project Structure Guidelines

## Directory Organization

The project follows a clear separation between frontend and backend applications, organized as follows:

```
lesson_2/
├── backend/                # Python FastAPI backend application
│   ├── main.py            # FastAPI app initialization and route definitions
│   ├── models.py          # SQLAlchemy database models (User, Task, Bid, etc.)
│   ├── schemas.py         # Pydantic schemas for request/response validation
│   ├── database.py        # Database configuration and session management
│   ├── auth.py            # JWT authentication and password hashing utilities
│   ├── test_auth.py       # Authentication tests
│   ├── requirements.txt   # Python dependencies
│   ├── run.bat           # Windows startup script
│   ├── run.sh            # Unix/Linux startup script
│   └── tasker.db         # SQLite database file (auto-generated)
│
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── pages/        # Page-level components (Dashboard, Login, TaskList, etc.)
│   │   ├── components/   # Reusable UI components (Navigation)
│   │   ├── App.jsx       # Main application component with routing
│   │   ├── AuthContext.jsx # Authentication context provider
│   │   ├── api.js        # Axios API client and endpoints
│   │   ├── App.css       # Application styles
│   │   └── main.jsx      # Application entry point
│   ├── index.html        # HTML template
│   ├── vite.config.js    # Vite build configuration
│   ├── package.json      # Node.js dependencies and scripts
│   └── package-lock.json # Locked dependency versions
│
├── docs/                  # Project documentation
│   └── tasker.md         # Requirements and specifications
│
├── .roo/                  # Development templates and commands
│   ├── templates/        # Document templates
│   └── commands/         # Custom commands
│
├── readme.md             # Project overview and setup instructions
├── PROJECT_SUMMARY.md    # Project summary
├── QUICKSTART.md         # Quick start guide
└── .gitignore           # Git ignore patterns
```

## Naming Conventions

### Files

**Frontend (React/JavaScript):**
- **Components**: `PascalCase.jsx` (e.g., `Navigation.jsx`, `Dashboard.jsx`)
- **Pages**: `PascalCase.jsx` (e.g., `Login.jsx`, `TaskList.jsx`, `CreateTask.jsx`)
- **Utilities/Services**: `camelCase.js` (e.g., `api.js`)
- **Context Providers**: `PascalCase.jsx` (e.g., `AuthContext.jsx`)
- **Styles**: `PascalCase.css` (e.g., `App.css`)

**Backend (Python/FastAPI):**
- **Modules**: `snake_case.py` (e.g., `main.py`, `auth.py`, `database.py`)
- **Tests**: `test_name.py` (e.g., `test_auth.py`)
- **Configuration**: `snake_case.txt` or `.bat/.sh` (e.g., `requirements.txt`, `run.sh`)

### Code

**Frontend:**
- **Components**: `PascalCase` (e.g., `Navigation`, `PrivateRoute`)
- **Functions/Hooks**: `camelCase` (e.g., `handleLogout`, `useAuth`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_URL`)
- **Variables**: `camelCase` (e.g., `user`, `loading`, `stats`)

**Backend:**
- **Classes/Models**: `PascalCase` (e.g., `User`, `Task`, `Bid`, `Agreement`)
- **Enums**: `PascalCase` (e.g., `UserType`, `TaskStatus`, `BidStatus`)
- **Functions**: `snake_case` (e.g., `get_db`, `create_access_token`, `verify_password`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Variables**: `snake_case` (e.g., `hashed_password`, `user_type`)

## Import Patterns

### Import Order

**Frontend (React):**
1. External dependencies (e.g., `import { BrowserRouter as Router } from 'react-router-dom'`)
2. Internal absolute imports from src (e.g., `import { useAuth } from './AuthContext'`)
3. Internal relative imports (e.g., `import { taskAPI } from '../api'`)
4. Style imports (e.g., `import './App.css'`)

**Backend (Python):**
1. Standard library imports (e.g., `from datetime import datetime, timedelta`)
2. Third-party package imports (e.g., `from fastapi import FastAPI, Depends`)
3. Local module imports (e.g., `import models`, `from database import get_db`)

### Import Style

**Frontend:**
- **Rule**: Use relative imports (`./` or `../`) for all internal modules
- **Rule**: Named imports for components and utilities (e.g., `import { useAuth } from './AuthContext'`)
- **Rule**: Default imports for page components (e.g., `import Dashboard from './pages/Dashboard'`)

**Backend:**
- **Rule**: Use relative imports for local modules in the same directory
- **Rule**: Group imports by category (standard lib, third-party, local) with blank lines between groups
- **Rule**: Use explicit imports for better IDE support (e.g., `from fastapi import FastAPI, Depends`)

## Code Structure Patterns

### Module/File Organization

**React Components (Frontend):**
1. Imports (external, then internal, then styles)
2. Component function definition
3. State declarations (`useState`)
4. Effect hooks (`useEffect`)
5. Event handler functions
6. Helper functions (if any)
7. Return statement with JSX
8. Default export

**FastAPI Routes (Backend):**
1. Imports (standard lib, third-party, local)
2. Constants and configuration
3. Database model initialization
4. FastAPI app configuration (CORS, middleware)
5. Route handler functions (grouped by resource)
6. Helper functions

**Database Models (Backend):**
1. Imports
2. Enum definitions
3. Model class definitions (inheriting from Base)
4. Column definitions
5. Relationship definitions

**Pydantic Schemas (Backend):**
1. Imports
2. Base schema classes
3. Request schemas (Create, Update)
4. Response schemas
5. Config classes

### Guiding Principles

- **Clarity**: Code should be organized to be read from top to bottom like a story
- **Consistency**: Similar files follow identical structure patterns
- **Single Responsibility**: Each file/module has one primary purpose
- **Separation of Concerns**: UI (frontend), API (FastAPI routes), data models (SQLAlchemy), validation (Pydantic) are kept separate

## Code Organization Principles

1. **Modularity**: Code is organized into independent, reusable modules with clear boundaries
   - Frontend pages are independent and interact through shared context/API
   - Backend separates database models, schemas, business logic, and authentication

2. **Separation of Concerns**: 
   - Frontend: UI components, routing, state management, API calls are separate
   - Backend: Data models, validation schemas, API routes, authentication logic are separate

3. **Testability**: Structure supports unit and integration testing
   - Backend has dedicated test files (e.g., `test_auth.py`)
   - Authentication and database logic are separated for easier testing

4. **Consistency**: Follow established patterns throughout the codebase
   - All pages follow same component structure
   - All API endpoints follow same authentication/validation patterns

## Module Boundaries

**Frontend:**
- **Public API vs. Internal**: 
  - Pages are the public-facing components
  - Components like Navigation are shared utilities
  - AuthContext and api.js provide shared services to all pages
  
- **Dependency Direction**: 
  - Pages can depend on components, contexts, and api.js
  - Components should not depend on pages
  - Context providers should not depend on pages or components
  
- **Cross-Feature Communication**: 
  - Pages communicate through AuthContext for user state
  - Pages use api.js for all backend communication
  - Direct page-to-page imports are not allowed

**Backend:**
- **Public API vs. Internal**: 
  - main.py defines the public API routes
  - auth.py, database.py are internal utilities
  - models.py and schemas.py define data contracts
  
- **Dependency Direction**: 
  - main.py can import from all other modules
  - auth.py depends on database.py and models.py
  - database.py has no dependencies on other local modules
  - models.py depends only on database.py
  
- **Module Communication**: 
  - All database access goes through SQLAlchemy ORM
  - All authentication goes through auth.py utilities
  - All routes in main.py use dependency injection for database and auth

## Code Size Guidelines

**Frontend:**
- **File Size**: < 300 lines per component/page
- **Function/Method Size**: < 50 lines
- **Component Complexity**: < 5 useState hooks, use custom hooks for complex state
- **Nesting Depth**: Maximum of 3 levels in JSX

**Backend:**
- **File Size**: < 400 lines per module
- **Function/Method Size**: < 50 lines
- **Class Complexity**: < 10 columns per model, < 5 methods per utility class
- **Nesting Depth**: Maximum of 3 levels in function logic

## Documentation Standards

**Frontend:**
- **Components**: Add JSDoc comments for reusable components explaining props and purpose
- **Complex Logic**: Add inline comments for non-obvious state management or business logic
- **API Functions**: Document expected parameters and return types in api.js

**Backend:**
- **Public APIs**: All FastAPI routes include docstrings with description, parameters, and return types
- **Models**: Add docstrings to model classes explaining their purpose and relationships
- **Complex Logic**: Authentication flows and database queries include explanatory comments
- **Pydantic Schemas**: Use descriptive field names and include examples in docstrings

**General:**
- **README Files**: Main readme.md provides setup, usage, and API documentation
- **Configuration**: Document environment variables and configuration options
- **Dependencies**: Keep requirements.txt and package.json up to date with comments for non-obvious packages