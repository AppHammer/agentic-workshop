# Technology Stack

## Project Type
Full-stack web application - A marketplace platform connecting local workers (taskers) with customers who need help with various tasks. Built as a minimum viable product (MVP) focusing on core marketplace functionality including task posting, bidding, agreements, and reviews.

## Core Technologies

### Backend Application

#### Primary Language(s)
- **Language**: Python 3.8+
- **Runtime**: CPython (standard Python interpreter)
- **Package Manager**: pip
- **Virtual Environment**: venv (recommended for development)

#### Key Dependencies/Libraries
- **FastAPI 0.121.1**: Modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints
- **SQLAlchemy 2.0.44**: SQL toolkit and Object-Relational Mapping (ORM) library for database operations
- **Pydantic 2.12.4**: Data validation library using Python type annotations (with email validation support)
- **Uvicorn 0.24.0**: Lightning-fast ASGI server implementation for running FastAPI applications
- **python-jose[cryptography] 3.3.0**: JavaScript Object Signing and Encryption (JOSE) implementation for JWT token handling
- **bcrypt 4.3.0**: Password hashing library using the bcrypt algorithm
- **python-multipart 0.0.6**: Support for parsing multipart/form-data (file uploads and form submissions)

#### Testing Dependencies
- **pytest 7.4.3**: Testing framework for Python
- **pytest-asyncio 0.21.1**: Pytest plugin for testing asyncio code
- **pytest-benchmark 4.0.0**: Pytest plugin for benchmarking code performance
- **pytest-cov 4.1.0**: Pytest plugin for code coverage reporting

### Frontend Application

#### Primary Language(s)
- **Language**: HTML5
- **Type**: Minimal static frontend (entry point only)
- **Structure**: Single-page application (SPA) architecture ready for framework integration

### Application Architecture

**Backend Architecture Pattern**: Monolithic REST API with layered architecture
- **API Layer** ([`main.py`](backend/main.py:1)): FastAPI endpoints organized by resource type (auth, tasks, bids, agreements, reviews, messages)
- **Data Access Layer** ([`models.py`](backend/models.py:1)): SQLAlchemy ORM models with relationship definitions
- **Validation Layer** ([`schemas.py`](backend/schemas.py:1)): Pydantic schemas for request/response validation
- **Security Layer** ([`auth.py`](backend/auth.py:1)): JWT-based authentication and authorization
- **Database Layer** ([`database.py`](backend/database.py:1)): SQLAlchemy session management and configuration

**Design Patterns:**
- Repository Pattern (via SQLAlchemy ORM)
- Dependency Injection (FastAPI's `Depends` mechanism)
- Schema/DTO Pattern (Pydantic models separate from database models)
- Middleware Pattern (CORS middleware for cross-origin requests)

**API Design:**
- RESTful resource-based endpoints
- OAuth2 password flow for authentication
- JWT bearer token authorization
- Consistent response models via Pydantic schemas

### Data Storage

- **Primary Storage**: SQLite ([`tasker.db`](backend/tasker.db:1))
  - File-based relational database
  - Auto-created on first application startup
  - Schema managed by SQLAlchemy ORM
  
- **Database Models**:
  - `users` - User accounts with role-based access (customer/tasker)
  - `tasks` - Task postings with lifecycle management
  - `bids` - Tasker bids on tasks
  - `agreements` - Accepted bids creating work agreements
  - `reviews` - Customer reviews of completed work
  - `messages` - User-to-user messaging system

- **Data Formats**: 
  - JSON for API request/response payloads
  - SQLite native types for database storage
  - Datetime objects in UTC (SQLAlchemy DateTime columns)

### External Integrations

- **APIs**: None (self-contained application)
- **Protocols**: 
  - HTTP/REST for API communication
  - OAuth2 password flow for authentication
- **Authentication**: 
  - JWT (JSON Web Tokens) for session management
  - bcrypt for password hashing
  - 30-minute token expiration (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

## Development Environment

### Build & Development Tools

- **Build System**: Python setuptools (implicit via pip)
- **Package Management**: 
  - pip for Python dependencies
  - requirements.txt for dependency specification
- **Development Workflow**: 
  - Hot reload enabled via Uvicorn's `--reload` flag
  - Automatic API documentation generation (FastAPI/Swagger)
  - Shell scripts for easy startup ([`run.sh`](backend/run.sh:1) / [`run.bat`](backend/run.bat:1))

### Code Quality Tools

- **Testing Framework**: 
  - pytest for unit and integration tests
  - pytest-asyncio for testing async endpoints
  - pytest-cov for coverage reporting
  - pytest-benchmark for performance testing
  
- **Type Checking**: Python type hints throughout codebase (validated by Pydantic)
- **Code Organization**: Modular architecture with clear separation of concerns
- **Documentation**: 
  - Inline docstrings for functions and classes
  - Auto-generated API documentation via FastAPI (Swagger UI at `/docs`)
  - Comprehensive README and QUICKSTART guides

### Version Control & Collaboration

- **VCS**: Git (evidenced by [`.gitignore`](.gitignore:1))
- **Branching Strategy**: Not specified (flexible for team preferences)
- **Code Review Process**: Not specified (flexible for team preferences)
- **Ignored Files**: Python artifacts, virtual environments, IDE files, logs, node_modules

### Development Server Configuration

- **Backend Server**: 
  - Default port: 8000
  - Auto-reload on code changes
  - CORS enabled for all origins (development mode)
  
- **API Documentation**: 
  - Interactive Swagger UI at `http://localhost:8000/docs`
  - ReDoc alternative at `http://localhost:8000/redoc`

## Deployment & Distribution

- **Target Platform(s)**: 
  - Development: Local development servers (Windows, macOS, Linux)
  - Production: Flexible - can deploy to any platform supporting Python ASGI applications
  
- **Distribution Method**: 
  - Source code distribution
  - Manual setup via requirements.txt
  
- **Installation Requirements**: 
  - Python 3.8 or higher
  - pip package manager
  - 50MB+ disk space for dependencies
  
- **Startup Scripts**:
  - [`backend/run.sh`](backend/run.sh:1) for Unix-like systems (macOS, Linux)
  - [`backend/run.bat`](backend/run.bat:1) for Windows
  - Manual: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`

- **Database Initialization**: 
  - Database and tables auto-created on first startup via SQLAlchemy
  - No manual migration required for initial setup

- **Update Mechanism**: Manual git pull and dependency updates

## Technical Requirements & Constraints

### Performance Requirements
- Lightweight SQLite database suitable for development and small-scale deployments
- FastAPI provides high-performance async request handling
- Target response time: < 200ms for most API endpoints (no specific benchmarks defined)
- Minimal resource footprint suitable for local development

### Compatibility Requirements  
- **Platform Support**: 
  - Cross-platform (Windows, macOS, Linux)
  - Requires Python 3.8+ runtime
  - SQLite bundled with Python (no external database installation)
  
- **Dependency Versions**: 
  - Python 3.8 minimum (recommended 3.10+)
  - All dependencies pinned in requirements.txt for reproducibility
  
- **Standards Compliance**: 
  - REST API design principles
  - OAuth2 authentication standard
  - JWT token standard (RFC 7519)
  - OpenAPI 3.0 specification (via FastAPI)

### Security & Compliance
- **Security Requirements**: 
  - Password hashing using bcrypt (industry standard)
  - JWT token-based authentication
  - HTTPS recommended for production (not enforced in development)
  - SQL injection prevention via SQLAlchemy ORM
  - Input validation via Pydantic schemas
  
- **Compliance Standards**: Not specified - standard web security practices
  
- **Threat Model**: 
  - Protection against common web vulnerabilities (SQL injection, XSS via API)
  - Secure password storage (bcrypt hashing)
  - Token expiration to limit session hijacking risk
  - CORS configuration required for production

### Scalability & Reliability
- **Expected Load**: 
  - Designed for MVP/development scale
  - SQLite suitable for single-server deployments with moderate traffic
  - Consider PostgreSQL migration for production scale
  
- **Availability Requirements**: Not specified - designed for development/testing
  
- **Growth Projections**: 
  - Current architecture supports migration to production-grade database
  - Stateless API design allows horizontal scaling
  - Database migration path available via SQLAlchemy

## Technical Decisions & Rationale

### Decision Log

1. **FastAPI over Flask/Django**: 
   - Modern async support for better performance
   - Automatic OpenAPI documentation generation
   - Built-in data validation via Pydantic
   - Type hints provide better IDE support and code quality
   - Lighter weight than Django, more batteries-included than Flask

2. **SQLite for Database**: 
   - Zero-configuration setup (bundled with Python)
   - Perfect for MVP and local development
   - File-based simplifies deployment and backups
   - Easy migration path to PostgreSQL/MySQL for production
   - Trade-off: Not suitable for high-concurrency production workloads

3. **JWT Authentication**: 
   - Stateless authentication enables horizontal scaling
   - Industry-standard approach for REST APIs
   - Works well with SPA frontends
   - Token-based reduces database lookups
   - Trade-off: Cannot invalidate tokens before expiration

4. **Monolithic Architecture**: 
   - Simpler development and deployment for MVP
   - Single codebase easier to understand and maintain
   - Lower operational complexity
   - Can be split into microservices later if needed
   - Trade-off: All components scale together

5. **Pydantic for Validation**: 
   - Type-safe data validation
   - Automatic JSON serialization/deserialization
   - Clear error messages for invalid input
   - Perfect integration with FastAPI
   - Reduces boilerplate validation code

6. **SQLAlchemy ORM**: 
   - Database-agnostic abstraction
   - Protection against SQL injection
   - Relationship management simplifies queries
   - Migration path to production databases
   - Trade-off: Learning curve for complex queries

## Known Limitations

- **SQLite Concurrent Write Limitations**: SQLite has limited concurrent write capability. For production deployments with multiple users, migration to PostgreSQL or MySQL is recommended.
  - **Impact**: May cause lock timeouts under heavy concurrent write load
  - **Future Solution**: Database migration guide and configuration for PostgreSQL

- **No Database Migrations**: Currently deletes and recreates database on schema changes during development.
  - **Impact**: Data loss on schema changes in development
  - **Future Solution**: Implement Alembic for proper database migrations before production deployment

- **CORS Fully Open in Development**: Current CORS middleware allows all origins (`allow_origins=["*"]`)
  - **Impact**: Security risk if accidentally deployed to production
  - **Future Solution**: Environment-based CORS configuration with restricted origins for production

- **Hardcoded Secret Key**: JWT secret key is hardcoded in [`auth.py`](backend/auth.py:11)
  - **Impact**: Security vulnerability if code is exposed
  - **Future Solution**: Move to environment variables before production deployment

- **No Rate Limiting**: API endpoints have no rate limiting
  - **Impact**: Vulnerable to abuse and denial-of-service attacks
  - **Future Solution**: Implement rate limiting middleware (e.g., slowapi) before production

- **Limited Error Handling**: Some edge cases may not have comprehensive error handling
  - **Impact**: Generic error messages or unhandled exceptions in some scenarios
  - **Future Solution**: Comprehensive error handling and custom exception classes

- **No Email Functionality**: User registration accepts email but doesn't verify or send notifications
  - **Impact**: Cannot confirm user identity or send important notifications
  - **Future Solution**: Integrate email service (SendGrid, AWS SES) for verification and notifications

- **Single File Structure**: All endpoints in single [`main.py`](backend/main.py:1) file
  - **Impact**: File approaching 350 lines; may become harder to maintain
  - **Future Solution**: Split into routers (tasks.py, bids.py, etc.) using FastAPI's APIRouter
