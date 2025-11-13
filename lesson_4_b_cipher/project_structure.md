# Tasker Marketplace - Project Structure Guidelines

## Directory Organization

This project is organized as a full-stack application with separate backend (FastAPI/Python) and frontend (HTML) components. The structure follows a clear separation of concerns with dedicated directories for source code, tests, documentation, and configuration.

```
/home/nick/agentic-workshop/lesson_4_memory/
├── backend/                # FastAPI backend application
│   ├── main.py            # API endpoints and application initialization
│   ├── models.py          # SQLAlchemy database models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── database.py        # Database configuration and session management
│   ├── auth.py            # Authentication and authorization logic
│   ├── test_auth.py       # Authentication unit tests
│   ├── test_profile.py    # User profile endpoint tests
│   ├── requirements.txt   # Python dependencies
│   ├── run.sh             # Unix startup script
│   ├── run.bat            # Windows startup script
│   └── tasker.db          # SQLite database file (auto-generated)
│
├── frontend/              # Frontend application
│   └── index.html         # Main HTML entry point
│
├── docs/                  # Project documentation
│   ├── tasker.md          # Requirements documentation
│   ├── v0.0.1/           # Version 0.0.1 documentation
│   └── v0.0.2/           # Version 0.0.2 documentation
│
├── .roo/                  # Roo AI assistant configuration
│   ├── commands/          # Custom command definitions
│   ├── rules-*/           # Mode-specific rules and guidelines
│   └── templates/         # Document templates
│
├── .playwright/           # Playwright test artifacts
├── PROJECT_SUMMARY.md     # High-level project overview
├── QUICKSTART.md          # Quick start guide
└── .gitignore            # Git ignore patterns

```

## Naming Conventions

### Backend (Python) Files
- **Models**: `models.py` (single file with all model definitions)
- **Schemas**: `schemas.py` (single file with all Pydantic schemas)
- **Utilities**: `auth.py`, `database.py` (descriptive snake_case names)
- **Tests**: `test_<feature>.py` (e.g., `test_auth.py`, `test_profile.py`)
- **Main Application**: `main.py`

### Frontend Files
- **HTML**: `index.html`
- **Configuration**: lowercase with extensions (e.g., `package.json`, `vite.config.js`)

### Documentation Files
- **Markdown**: `UPPERCASE.md` for root-level docs (e.g., `README.md`, `QUICKSTART.md`)
- **Markdown**: `lowercase.md` for feature docs (e.g., `tasker.md`)

### Code (Python Backend)
- **Classes/Types/Models**: `PascalCase` (e.g., `User`, `Task`, `UserType`)
- **Functions/Methods**: `snake_case` (e.g., `get_current_user`, `create_access_token`)
- **Constants/Enums**: `UPPER_SNAKE_CASE` (e.g., `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Variables**: `snake_case` (e.g., `db_user`, `hashed_password`)
- **Database Tables**: `lowercase_plural` (e.g., `users`, `tasks`, `bids`)

## Import Patterns

### Import Order (Python)
The project follows this consistent order for import statements:

1. Standard library imports (e.g., `from datetime import datetime`)
2. Third-party package imports (e.g., `from fastapi import FastAPI`, `from sqlalchemy import Column`)
3. Local application imports (e.g., `import models`, `import schemas`)

### Import Style
- **Rule**: Use absolute imports from the module root (e.g., `import models`, `from database import get_db`)
- **Rule**: Group related imports together
- **Rule**: Imports should be at the top of the file, after the module docstring

Example from `main.py`:
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

import models
import schemas
from database import engine, get_db
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
```

## Code Structure Patterns

### Module/File Organization (Python)
Each Python file follows this standard structure:

1. Module docstring (if applicable)
2. Imports (grouped as specified above)
3. Constants and configuration
4. Type/Enum definitions
5. Class definitions
6. Function definitions
7. Main execution code (if applicable)

### API Endpoint Organization (main.py)
Endpoints are organized by feature/resource:

1. Application initialization and middleware
2. Authentication endpoints (`/register`, `/token`, `/users/me`)
3. Task endpoints (`/tasks`, `/tasks/{id}`)
4. Bid endpoints (`/bids`)
5. Agreement endpoints (`/agreements`)
6. Review endpoints (`/reviews`)
7. Message endpoints (`/messages`)

### Database Model Organization (models.py)
Models are organized in logical dependency order:

1. Enum definitions (UserType, TaskStatus, BidStatus)
2. Core models (User)
3. Dependent models (Task, Bid, Agreement, Review, Message)

Each model includes:
- Table name declaration
- Column definitions
- Relationships with proper foreign keys and back references

### Schema Organization (schemas.py)
Schemas are grouped by resource type:

1. Base schemas (UserBase, TaskBase, etc.)
2. Create schemas (UserCreate, TaskCreate, etc.)
3. Response schemas (User, Task, etc.)
4. Special purpose schemas (Token, UserProfile, etc.)

### Guiding Principles
- **Clarity**: Code should read like documentation, with clear variable and function names
- **Consistency**: Similar functionality should follow the same patterns
- **Single Responsibility**: Each file, function, and class should have one clear purpose
- **Documentation**: All public functions and complex logic must be documented

## Code Organization Principles

1. **Modularity**: Backend code is organized into focused modules (models, schemas, auth, database)
2. **Separation of Concerns**: 
   - **models.py**: Database structure and relationships only
   - **schemas.py**: Request/response validation and serialization
   - **auth.py**: Authentication and authorization logic
   - **main.py**: API endpoints and business logic
   - **database.py**: Database configuration and session management
3. **Testability**: 
   - Each module has corresponding test files
   - Tests use mocking to isolate functionality
   - Comprehensive test coverage for critical paths
4. **Consistency**: All endpoints follow FastAPI best practices with dependency injection

## Module Boundaries

### Backend Module Dependencies
- **main.py** depends on: `models`, `schemas`, `database`, `auth`
- **auth.py** depends on: `models`, `database`
- **models.py** depends on: `database` (for Base)
- **schemas.py** depends on: `models` (for enums)
- **database.py** has no internal dependencies

### Dependency Direction
- Authentication logic (`auth.py`) can be imported by endpoints (`main.py`)
- Database models (`models.py`) can be imported by all modules
- Schemas (`schemas.py`) should only be used by endpoint handlers
- Tests (`test_*.py`) can import any module for testing but are never imported

### Cross-Module Communication
- API endpoints use dependency injection for database sessions and authentication
- Models define relationships using SQLAlchemy's relationship() function
- Schemas reference model enums for validation consistency

## Code Size Guidelines

These guidelines help maintain code quality and readability:

- **File Size**: < 500 lines (main.py is at the limit; consider splitting if adding major features)
- **Function/Method Size**: < 50 lines (most functions are 10-30 lines)
- **Class Complexity**: Models should have < 15 fields; consider normalization if exceeded
- **Nesting Depth**: Maximum of 3 levels of nesting (use early returns to reduce nesting)
- **Endpoint Function**: < 30 lines (extract complex logic into helper functions)

## Documentation Standards

### Code Documentation (Python)

- **Public APIs/Endpoints**: All FastAPI endpoints must have docstrings explaining:
  - Purpose of the endpoint
  - Required parameters
  - Return value structure
  - Possible exceptions/status codes
  
  Example from `main.py`:
  ```python
  @app.get("/users/me/profile", response_model=schemas.UserProfile)
  def get_user_profile(current_user: models.User = Depends(get_current_user)):
      """
      Get the complete profile of the currently authenticated user.
      
      Returns:
          UserProfile: Complete user profile including tasker-specific fields if applicable
      
      Raises:
          HTTPException: 401 if authentication fails
      """
      return current_user
  ```

- **Functions with Complex Logic**: Functions in `auth.py` include detailed docstrings:
  ```python
  def verify_password(plain_password, hashed_password):
      """
      Verify a plaintext password against a bcrypt hash.
      
      Args:
          plain_password: The plaintext password to verify
          hashed_password: The bcrypt hash to verify against
      
      Returns:
          bool: True if password matches, False otherwise
      """
  ```

- **Models**: Each model should have a class docstring if the purpose isn't obvious from the name

- **Complex Algorithms**: Use inline comments to explain the 'why', not just the 'what'

### Project Documentation

- **Root README**: Comprehensive setup and usage instructions (see `README.md` reference in PROJECT_SUMMARY.md)
- **QUICKSTART.md**: Step-by-step guide for running the application
- **PROJECT_SUMMARY.md**: High-level overview of implementation and features
- **Feature Requirements**: Version-specific documentation in `docs/v*.*.*` directories

### Test Documentation

All test classes and methods should have descriptive docstrings:

```python
class TestPasswordHashing:
    """Test suite for password hashing and verification functions."""
    
    def test_get_password_hash_returns_string(self):
        """Test that get_password_hash returns a string."""
```

## Backend-Specific Guidelines

### FastAPI Endpoint Patterns

**Authentication Required:**
```python
@app.get("/endpoint", response_model=schemas.ResponseSchema)
def endpoint_name(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Endpoint logic
```

**Public Endpoints:**
```python
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Registration logic
```

**Authorization Checks:**
```python
if current_user.user_type != models.UserType.CUSTOMER:
    raise HTTPException(status_code=403, detail="Only customers can create tasks")
```

### Database Patterns

**Creating Records:**
```python
db_object = models.ModelName(**data.dict(), additional_field=value)
db.add(db_object)
db.commit()
db.refresh(db_object)
return db_object
```

**Querying Records:**
```python
query = db.query(models.ModelName)
query = query.filter(models.ModelName.field == value)
results = query.all()  # or .first()
```

**Relationship Access:**
Models use SQLAlchemy relationships with back_populates for bidirectional navigation:
```python
# In User model
posted_tasks = relationship("Task", back_populates="customer", foreign_keys="Task.customer_id")

# In Task model 
customer = relationship("User", back_populates="posted_tasks", foreign_keys=[customer_id])
```

### Error Handling

**Not Found:**
```python
if not object:
    raise HTTPException(status_code=404, detail="Resource not found")
```

**Unauthorized:**
```python
if object.owner_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

**Validation Errors:**
Pydantic schemas handle validation automatically with descriptive error messages.

### Testing Patterns

**Unit Tests (with mocking):**
```python
def test_function_name(self):
    """Test description."""
    mock_db = Mock(spec=Session)
    # Setup mocks
    result = function_under_test(mock_db)
    # Assertions
    assert result == expected
    mock_db.method.assert_called_once()
```

**Testing Endpoints:**
```python
def test_endpoint_requires_authentication(self):
    """Test that the endpoint requires authentication."""
    response = client.put("/users/me", json={})
    assert response.status_code == 401
```

## Security Guidelines

1. **Password Hashing**: Always use bcrypt for password hashing (implemented in `auth.py`)
2. **JWT Tokens**: Use secure token generation with configurable expiration
3. **Authentication**: All protected endpoints must use `Depends(get_current_user)`
4. **Authorization**: Check user permissions before allowing resource access
5. **Input Validation**: Use Pydantic schemas for all request data validation
6. **SQL Injection**: Use SQLAlchemy ORM (never build raw SQL strings)
7. **CORS**: Configure CORS appropriately for deployment environment

## Performance Considerations

1. **Database Queries**: Use SQLAlchemy relationships efficiently; avoid N+1 queries
2. **Session Management**: Database sessions are automatically handled by FastAPI dependencies
3. **Connection Pooling**: SQLite connection pooling is handled by SQLAlchemy
4. **Query Optimization**: Use `.filter()` before `.all()` to limit results at database level

## Development Workflow

1. **Adding New Features**:
   - Define database models in `models.py`
   - Create Pydantic schemas in `schemas.py`
   - Implement API endpoints in `main.py`
   - Write comprehensive tests in `test_<feature>.py`
   - Update documentation

2. **Database Changes**:
   - Modify models in `models.py`
   - Delete `tasker.db` for development (auto-recreated)
   - For production, implement proper migrations (currently not configured)

3. **Testing**:
   - Run tests: `pytest`
   - Check coverage: `pytest --cov=. --cov-report=html`
   - All tests must pass before deployment

## Deployment Considerations

1. **Environment Variables**: Secret key and database URL should be environment variables in production
2. **Database**: Consider PostgreSQL for production instead of SQLite
3. **CORS**: Restrict allowed origins in production
4. **HTTPS**: Always use HTTPS in production
5. **Token Expiration**: Review and adjust token expiration times for production