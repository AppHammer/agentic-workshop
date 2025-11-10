# Technology Stack

## Project Type
Web Application - Marketplace Platform (Single-Page Application)

The Tasker Platform is a marketplace to connect local workers (taskers) with customers who need work done. It's a full-stack web application built as a minimum viable product (MVP) with a React frontend and FastAPI backend.

## Core Technologies

### Backend Application

#### Primary Language(s)

- **Language**: Python 3.11 or higher
- **Runtime**: CPython (standard Python interpreter)
- **Package Manager**: pip (Python package installer)

#### Key Dependencies/Libraries

- **FastAPI 0.104.1**: Modern, high-performance web framework for building APIs with Python
- **SQLAlchemy 2.0.23**: SQL toolkit and Object-Relational Mapping (ORM) library for database operations
- **Pydantic 2.5.0**: Data validation and settings management using Python type annotations
- **python-jose[cryptography] 3.3.0**: JavaScript Object Signing and Encryption (JOSE) implementation for JWT tokens
- **bcrypt 4.3.0**: Password hashing library (specific version required - see Technical Decisions)
- **passlib[bcrypt] 1.7.4**: Password hashing and verification framework
- **python-multipart 0.0.6**: Streaming multipart parser for Python
- **Uvicorn 0.24.0**: ASGI web server implementation for running FastAPI
- **pytest 7.4.3**: Testing framework for Python
- **pytest-asyncio 0.21.1**: Pytest support for asyncio

#### Application Architecture

- **Pattern**: Layered Architecture with REST API
  - **Data Layer**: SQLAlchemy ORM models define database schema
  - **Validation Layer**: Pydantic schemas validate request/response data
  - **API Layer**: FastAPI endpoints handle HTTP requests/responses
  - **Authentication Layer**: JWT-based authentication with OAuth2 password flow
- **API Style**: RESTful API endpoints
- **Dependency Injection**: FastAPI's built-in dependency injection system

### Frontend Application

#### Primary Language(s)

- **Language**: JavaScript (ES6+)
- **Runtime**: Node.js (via browser)
- **Package Manager**: npm (Node Package Manager)

#### Key Dependencies/Libraries

- **React 18.2.0**: JavaScript library for building user interfaces
- **react-dom 18.2.0**: React package for working with the DOM
- **react-router-dom 6.20.0**: Declarative routing for React applications
- **axios 1.6.2**: Promise-based HTTP client for making API requests
- **react-scripts 5.0.1**: Configuration and scripts for Create React App

#### Application Architecture

- **Pattern**: Component-Based Architecture
  - **UI Layer**: React components render user interface
  - **Service Layer**: Centralized API service (`api.js`) for HTTP calls
  - **Routing Layer**: React Router for client-side navigation
  - **State Management**: Local component state using React hooks (useState, useEffect)
- **Authentication**: JWT token stored in localStorage, axios interceptor adds to requests

### Data Storage

- **Primary Storage**: SQLite database (`tasker.db`)
- **ORM**: SQLAlchemy 2.0.23 for database operations
- **Schema Management**: Automatic table creation via `Base.metadata.create_all()`
- **Data Formats**: JSON for API request/response payloads

### External Integrations

- **APIs**: None currently (self-contained application)
- **Protocols**: HTTP/REST for client-server communication
- **Authentication**: 
  - OAuth2 password flow for login
  - JWT (JSON Web Tokens) for API authentication
  - Bearer token in Authorization header

### Monitoring & Dashboard Technologies

- **Dashboard Framework**: React 18.2.0 with component-based UI
- **Real-time Communication**: Standard HTTP requests (no WebSocket yet)
- **State Management**: React hooks (useState, useEffect) for local state
- **Client-Server Communication**: Axios with request/response interceptors

## Development Environment

### Build & Development Tools

#### Backend

- **Package Management**: pip with `requirements.txt`
- **Development Server**: Uvicorn ASGI server
- **Database**: SQLite (file-based, no separate server required)
- **Development Workflow**: Manual server restart for code changes

#### Frontend

- **Build System**: Create React App (react-scripts)
- **Package Management**: npm with `package.json` and `package-lock.json`
- **Development Server**: webpack-dev-server (via react-scripts)
- **Development Workflow**: Hot module replacement for automatic code updates
- **Proxy Configuration**: API requests proxied to `http://localhost:8000`

### Code Quality Tools

- **Static Analysis**: Not currently configured (future consideration)
- **Formatting**: Not currently configured (future consideration)
- **Testing Framework**: 
  - Backend: pytest 7.4.3 with pytest-asyncio for async tests
  - Frontend: Jest (included with react-scripts) - not actively used yet
- **Documentation**: Inline code comments and docstrings

### Version Control & Collaboration

- **VCS**: Git
- **Branching Strategy**: Not formally defined (MVP development phase)
- **Code Review Process**: Not formally defined (MVP development phase)
- **Repository Structure**: Monorepo with separate backend and frontend directories

### Dashboard Development

- **Live Reload**: Hot module replacement via webpack-dev-server
- **Port Management**: 
  - Frontend: `http://localhost:3000` (default Create React App)
  - Backend: `http://localhost:8000` (Uvicorn default)
- **CORS Configuration**: Backend configured to allow requests from localhost:3000 and localhost:8000

## Deployment & Distribution

- **Target Platform(s)**: Local development only (MVP phase)
- **Distribution Method**: Not yet defined - currently manual setup
- **Installation Requirements**: 
  - Python 3.11 or higher
  - Node.js and npm
  - Operating System: Cross-platform (Windows, macOS, Linux)
- **Update Mechanism**: Manual git pull and dependency updates

## Technical Requirements & Constraints

### Performance Requirements

- Response time: Not formally defined (acceptable for local development)
- Database performance: SQLite suitable for MVP/development with single-user access
- Frontend: React renders efficiently for MVP scale
- API: FastAPI provides high performance for asynchronous operations

### Compatibility Requirements  

- **Platform Support**: 
  - Backend: Cross-platform (Windows, macOS, Linux via Python)
  - Frontend: Modern browsers (Chrome, Firefox, Safari - last 1-2 versions)
- **Dependency Versions**: 
  - Python: 3.11 or higher (specified in prerequisites)
  - Node.js: Compatible with react-scripts 5.0.1
  - bcrypt: Must be version 4.3.0 (see Technical Decisions)
- **Standards Compliance**: 
  - REST API conventions
  - OAuth2 for authentication
  - JWT for token-based auth

### Security & Compliance

- **Security Requirements**: 
  - Password hashing with bcrypt
  - JWT token-based authentication
  - CORS middleware for cross-origin requests
- **Compliance Standards**: Not applicable (MVP/development phase)
- **Current Limitations**:
  - Hardcoded `SECRET_KEY` (needs environment variable in production)
  - Permissive CORS policy (needs restriction in production)
  - No HTTPS (acceptable for local development)
  - No rate limiting (future consideration)

### Scalability & Reliability

- **Expected Load**: Single user/developer (MVP development)
- **Availability Requirements**: Not defined (local development)
- **Database Constraints**: SQLite is single-writer, suitable for MVP but will need migration to PostgreSQL for production
- **Growth Projections**: Post-MVP will require:
  - Migration to PostgreSQL or similar multi-user database
  - Proper environment-based configuration
  - Production-grade secrets management
  - Deployment to cloud infrastructure

## Technical Decisions & Rationale

### Decision Log

1. **FastAPI for Backend**: 
   - **Rationale**: Modern, fast, automatic API documentation, excellent async support, type hints integration with Pydantic
   - **Alternatives Considered**: Django REST Framework (more heavyweight), Flask (less modern)
   - **Trade-offs**: Smaller ecosystem than Django, but better performance and developer experience for APIs

2. **React for Frontend**: 
   - **Rationale**: Component-based architecture, rich ecosystem, good developer tools, familiar to most developers
   - **Alternatives Considered**: Vue.js, Angular
   - **Trade-offs**: Requires more boilerplate than Vue, but more job market demand and resources

3. **SQLite for Database**:
   - **Rationale**: Zero-configuration, file-based, perfect for MVP and local development
   - **Alternatives Considered**: PostgreSQL (planned for production)
   - **Trade-offs**: Single-writer limitation, not suitable for production, but excellent for MVP development

4. **JWT Authentication**:
   - **Rationale**: Stateless authentication, scalable, standard approach for SPA applications
   - **Alternatives Considered**: Session-based auth
   - **Trade-offs**: Token management complexity, but better for API-first applications

5. **bcrypt 4.3.0 for Password Hashing**:
   - **Rationale**: Critical bug fix - newer versions of bcrypt (4.4.0+) have compatibility issues with passlib causing authentication failures
   - **Issue**: `ValueError: password cannot contain null characters` with newer bcrypt versions
   - **Solution**: Pinned to bcrypt 4.3.0 which works correctly with passlib 1.7.4
   - **Reference**: Documented in [`flow.md`](flow.md:17) - issue discovered during user registration testing
   - **Trade-offs**: Using not-latest version, but stability is critical for authentication

6. **Monorepo Structure**:
   - **Rationale**: Single repository for frontend and backend simplifies development and coordination
   - **Alternatives Considered**: Separate repositories for frontend/backend
   - **Trade-offs**: Larger repository size, but easier to maintain consistency and share documentation

7. **Create React App**:
   - **Rationale**: Quick setup, batteries-included, good for MVP, standard tooling
   - **Alternatives Considered**: Vite, Next.js
   - **Trade-offs**: Slower build times than Vite, but more mature and stable

## Known Limitations

- **Hardcoded Secret Key**: The JWT `SECRET_KEY` is hardcoded in [`auth.py`](app/backend/auth.py:10) instead of using environment variables. Impact: Security risk if code is exposed. Future solution: Move to environment variables before any deployment.

- **SQLite Database**: Single-writer database unsuitable for production with multiple concurrent users. Impact: Cannot handle concurrent writes, performance degrades with scale. Future solution: Migrate to PostgreSQL for production deployment.

- **No Code Quality Tools**: No linters, formatters, or static analysis tools configured. Impact: Potential code style inconsistencies, harder to catch bugs early. Future solution: Add Black/Flake8 for Python, ESLint/Prettier for JavaScript.

- **Limited Test Coverage**: Only basic auth tests exist, no comprehensive test suite. Impact: Higher risk of regressions, harder to refactor confidently. Future solution: Expand test coverage for both backend and frontend.

- **Permissive CORS Policy**: CORS allows all methods and headers from localhost. Impact: Acceptable for development, but needs restriction for production. Future solution: Configure specific origins, methods, and headers for production.

- **No Environment-Based Configuration**: No distinction between development and production settings. Impact: Cannot easily deploy to different environments. Future solution: Implement environment-based configuration system.

- **Missing Production Features**: No logging, monitoring, error tracking, or performance optimization. Impact: Difficult to debug and maintain in production. Future solution: Add comprehensive logging, monitoring, and observability tools.

- **No Database Migrations**: Database schema changes managed manually via `create_all()`. Impact: Cannot track schema evolution, difficult to manage in production. Future solution: Implement Alembic for database migrations.

- **Basic React State Management**: Using only local component state, no global state management. Impact: Props drilling, potential performance issues as app grows. Future solution: Consider Redux, Zustand, or Context API if complexity increases.

- **No Real-time Features**: Communication is request/response only, no WebSocket support. Impact: Cannot implement real-time messaging or notifications efficiently. Future solution: Add WebSocket support for messaging system when needed post-MVP.