# Technology Stack

## Project Type
Full-stack web application - A marketplace platform connecting local workers (taskers) with customers who need help with various tasks. Built as a Minimum Viable Product (MVP) for educational purposes.

## Core Technologies

### Backend Application

#### Primary Language(s)
- **Language**: Python 3.8+
- **Runtime/Compiler**: CPython (standard Python interpreter)
- **Language-specific tools**: 
  - pip (package manager)
  - venv (virtual environment)
  - uvicorn (ASGI server)

#### Key Dependencies/Libraries
- **FastAPI 0.104.1**: Modern, high-performance web framework for building REST APIs with automatic OpenAPI documentation
- **SQLAlchemy 2.0.23**: SQL toolkit and Object-Relational Mapping (ORM) for database operations
- **Pydantic 2.5.0**: Data validation and settings management using Python type annotations
- **Uvicorn 0.24.0**: Lightning-fast ASGI server implementation for serving FastAPI applications
- **python-jose[cryptography] 3.3.0**: JavaScript Object Signing and Encryption (JOSE) implementation for JWT handling
- **bcrypt 4.3.0**: Password hashing library using the bcrypt algorithm
- **passlib[bcrypt] 1.7.4**: Comprehensive password hashing framework
- **python-multipart 0.0.6**: Streaming multipart parser for handling file uploads and form data
- **pytest 7.4.3**: Testing framework for unit and integration tests
- **pytest-asyncio 0.21.1**: Pytest plugin for testing asyncio code
- **pytest-benchmark 4.0.0**: Pytest plugin for benchmarking
- **pytest-cov 4.1.0**: Pytest plugin for measuring code coverage

#### Application Architecture
**Monolithic REST API** with layered architecture:
- **API Layer** ([`main.py`](backend/main.py:1)): RESTful endpoints with route handlers
- **Data Access Layer** ([`models.py`](backend/models.py:1)): SQLAlchemy ORM models
- **Business Logic Layer**: Integrated within route handlers and authentication utilities
- **Validation Layer** ([`schemas.py`](backend/schemas.py:1)): Pydantic schemas for request/response validation
- **Authentication Layer** ([`auth.py`](backend/auth.py:1)): JWT-based authentication and password hashing

Key patterns:
- Dependency injection for database sessions and authentication
- Schema-based validation for all API endpoints
- Automatic API documentation via OpenAPI/Swagger

#### Data Storage
- **Primary storage**: SQLite 3 (file-based relational database: [`tasker.db`](backend/tasker.db:1))
- **Caching**: None (in-memory only during request lifecycle)
- **Data formats**: JSON for API requests/responses
- **Database Schema**: 6 tables
  - [`users`](backend/models.py:22): User accounts (customers and taskers)
  - [`tasks`](backend/models.py:42): Posted tasks
  - [`bids`](backend/models.py:1): Tasker bids on tasks
  - [`agreements`](backend/models.py:1): Accepted bids creating work agreements
  - [`reviews`](backend/models.py:1): Task completion reviews
  - [`messages`](backend/models.py:1): User-to-user messaging

#### External Integrations
- **APIs**: None (self-contained application)
- **Protocols**: HTTP/REST for all API communication
- **Authentication**: JWT (JSON Web Tokens) with OAuth2 password flow
  - Token expiration: 30 minutes
  - Algorithm: HS256
  - Secret key: Configurable (default placeholder for development)

### Frontend Application

#### Primary Language(s)
- **Language**: JavaScript (ES6+) / JSX
- **Runtime**: Node.js 16+ (for build tooling)
- **Language-specific tools**:
  - npm (package manager)
  - Vite (build tool and dev server)

#### Key Dependencies/Libraries
- **React 18.2.0**: UI library for building component-based user interfaces
- **React DOM 18.2.0**: React renderer for web applications
- **React Router DOM 6.20.0**: Declarative routing for React applications
- **Axios 1.6.2**: Promise-based HTTP client for API communication
- **Vite 7.2.2**: Next-generation frontend build tool with hot module replacement
- **@vitejs/plugin-react 4.2.1**: Official Vite plugin for React with Fast Refresh

#### Application Architecture
**Single Page Application (SPA)** with component-based architecture:
- **Routing Layer** ([`App.jsx`](frontend/src/App.jsx:1)): React Router for client-side navigation
- **State Management**: React Context API for global authentication state ([`AuthContext.jsx`](frontend/src/AuthContext.jsx:1))
- **API Client Layer** ([`api.js`](frontend/src/api.js:1)): Axios instance with JWT token injection
- **Component Structure**:
  - 9 page components in [`src/pages/`](frontend/src/pages/)
  - Shared components in [`src/components/`](frontend/src/components/)
  - Protected routes requiring authentication

Key patterns:
- Context API for authentication state sharing
- Axios interceptors for automatic JWT token attachment
- Component-based UI with functional components and hooks
- Form handling with local state management

#### Monitoring & Dashboard Technologies
- **Dashboard Framework**: React 18 with functional components
- **Real-time Communication**: HTTP polling (no WebSocket implementation)
- **Visualization Libraries**: Native CSS for UI styling (no charting libraries)
- **State Management**: React Context API for global state, local component state with useState/useEffect hooks

## Development Environment

### Build & Development Tools

#### Backend
- **Build System**: None (interpreted Python)
- **Package Management**: pip with [`requirements.txt`](backend/requirements.txt:1)
- **Development workflow**: 
  - Hot reload via uvicorn `--reload` flag
  - Auto-reload on code changes
- **Startup Scripts**:
  - Windows: [`run.bat`](backend/run.bat:1)
  - Unix/macOS: [`run.sh`](backend/run.sh:1)

#### Frontend
- **Build System**: Vite with ES modules
- **Package Management**: npm with [`package.json`](frontend/package.json:1)
- **Development workflow**:
  - Hot Module Replacement (HMR) via Vite
  - Fast Refresh for React components
  - Instant server start
- **Build Commands**:
  - Development: `npm run dev`
  - Production build: `npm run build`
  - Preview production build: `npm run preview`

### Code Quality Tools

#### Backend
- **Static Analysis**: None configured (potential: pylint, mypy)
- **Formatting**: None configured (potential: black, autopep8)
- **Testing Framework**: pytest with async support
  - Unit testing: pytest
  - Async testing: pytest-asyncio
  - Coverage reporting: pytest-cov
  - Performance benchmarking: pytest-benchmark
- **Test Files**: [`test_auth.py`](backend/test_auth.py:1)
- **Documentation**: Auto-generated OpenAPI/Swagger docs via FastAPI

#### Frontend
- **Static Analysis**: None configured (potential: ESLint)
- **Formatting**: None configured (potential: Prettier)
- **Testing Framework**: None configured (potential: Vitest, React Testing Library)
- **Documentation**: Markdown documentation in [`README.md`](readme.md:1), [`QUICKSTART.md`](QUICKSTART.md:1)

### Version Control & Collaboration
- **VCS**: Git
- **Branching Strategy**: Not formally defined (educational/MVP project)
- **Code Review Process**: Not formally defined (single developer/learning project)
- **Repository Configuration**: [`.gitignore`](.gitignore:1) for Python and Node.js

### Dashboard Development
- **Live Reload**: Vite HMR with instant updates
- **Port Management**: 
  - Frontend: Configurable (default 3000) via [`vite.config.js`](frontend/vite.config.js:6)
  - Backend: Default 8000 (uvicorn)
- **Multi-Instance Support**: Possible with different port configurations
- **Proxy Configuration**: Frontend proxies `/api` requests to backend at `http://localhost:8000`

## Deployment & Distribution

**Current Status**: Local development and educational use only

### Planned/Potential Deployment
- **Target Platform(s)**: 
  - Development: Local machine (Windows/macOS/Linux)
  - Production (future): Cloud platforms (Render, Railway, Heroku, AWS, etc.)
- **Distribution Method**: 
  - Current: Git clone with manual setup
  - Future: Containerized deployment (Docker), Platform-as-a-Service
- **Installation Requirements**:
  - Python 3.8+ with pip
  - Node.js 16+ with npm
  - ~100MB disk space for dependencies
  - SQLite support (included in Python)
- **Update Mechanism**: Manual git pull and dependency updates

## Technical Requirements & Constraints

### Performance Requirements
**Current (MVP/Educational)**:
- No specific performance benchmarks
- Single-threaded SQLite suitable for development/learning
- Response times not formally measured
- No load testing or stress testing

**Future Considerations**:
- Target response time: < 500ms for API endpoints
- Support for 10-100 concurrent users
- Database migration to PostgreSQL for production scalability
- Consider caching layer (Redis) for improved performance

### Compatibility Requirements  
- **Platform Support**: 
  - Windows 10/11
  - macOS 10.15+
  - Linux (Ubuntu 20.04+, Debian, RHEL-based)
- **Browser Support**:
  - Modern browsers: Chrome, Firefox, Safari, Edge (ES6+ support required)
  - Mobile browsers: iOS Safari, Chrome Mobile
- **Dependency Versions**:
  - Python: 3.8+ (typed features used)
  - Node.js: 16+ (ES module support)
  - SQLite: 3.x (bundled with Python)
- **Standards Compliance**: REST API design, OAuth2 password flow, JSON data format

### Security & Compliance

**Implemented Security**:
- JWT-based authentication with configurable expiration (30 minutes)
- Password hashing using bcrypt (cost factor 12)
- CORS middleware configured for local development
- SQL injection protection via SQLAlchemy ORM
- OAuth2 password flow for token-based authentication

**Security Considerations**:
- Secret key must be changed for production deployment
- HTTPS required for production (JWT tokens transmitted in headers)
- CORS origins must be restricted in production
- Rate limiting not implemented (recommended for production)
- No input sanitization beyond Pydantic validation

**Compliance Standards**: Not applicable (educational project)

**Threat Model**:
- Development/educational environment assumed trusted
- Production deployment would require:
  - HTTPS/TLS encryption
  - Environment-based configuration management
  - Secure secret management (environment variables, vaults)
  - Rate limiting to prevent abuse
  - Input validation and sanitization
  - CSRF protection for non-API routes

### Scalability & Reliability

**Current State (MVP)**:
- **Expected Load**: 1-5 concurrent users (development/testing)
- **Database**: SQLite with single-writer limitation
- **Availability**: No redundancy, single point of failure
- **Backup Strategy**: Manual file-based backup of `tasker.db`

**Growth Projections (Future)**:
- Migrate to PostgreSQL for multi-user concurrency
- Implement connection pooling
- Add caching layer (Redis) for session management
- Consider horizontal scaling with load balancer
- Implement database replication for reliability
- Add health check endpoints for monitoring

## Technical Decisions & Rationale

### Decision Log

1. **FastAPI over Flask/Django**
   - **Rationale**: Modern async support, automatic OpenAPI documentation, excellent performance, strong typing with Pydantic
   - **Trade-offs**: Smaller ecosystem than Django, newer framework with less community resources
   - **Alternative Considered**: Django REST Framework (more mature but heavier)

2. **SQLite over PostgreSQL**
   - **Rationale**: Zero configuration for MVP/educational purposes, file-based simplicity, perfect for learning and development
   - **Trade-offs**: Single writer limitation, not suitable for production with multiple concurrent users
   - **Migration Path**: Switch to PostgreSQL for production deployment (minimal SQLAlchemy changes)

3. **React with Vite over Create React App**
   - **Rationale**: Faster development server, instant HMR, simpler configuration, better performance
   - **Trade-offs**: Less established than CRA, smaller plugin ecosystem
   - **Alternative Considered**: Next.js (overkill for simple SPA)

4. **JWT Authentication over Session-based**
   - **Rationale**: Stateless authentication, easier to scale, works well with SPA architecture
   - **Trade-offs**: Token size in headers, cannot invalidate tokens before expiry without additional infrastructure
   - **Enhancement**: Could add refresh tokens and token blacklist for production

5. **Context API over Redux**
   - **Rationale**: Built-in React solution, simpler for small state management needs, no additional dependencies
   - **Trade-offs**: Less powerful for complex state, no dev tools, no middleware
   - **Justification**: Authentication state is simple enough for Context API

6. **Monolithic Architecture over Microservices**
   - **Rationale**: Appropriate for MVP scope, simpler deployment, easier development and debugging
   - **Trade-offs**: Harder to scale specific components, all services share same deployment lifecycle
   - **Future**: Could extract messaging or payment services if needed

## Known Limitations

### Technical Debt & Areas for Improvement

1. **Database Scalability**
   - **Limitation**: SQLite single-writer constraint limits concurrent write operations
   - **Impact**: Not suitable for production with multiple simultaneous users
   - **Solution**: Migrate to PostgreSQL for production deployment

2. **Authentication Security**
   - **Limitation**: Secret key hardcoded in source, no refresh token mechanism, no token revocation
   - **Impact**: Security risk in production, tokens cannot be invalidated
   - **Solution**: Environment-based configuration, implement refresh tokens, add token blacklist/revocation

3. **Error Handling**
   - **Limitation**: Basic error handling, limited client-side error messages
   - **Impact**: Debugging difficulties, poor user experience on errors
   - **Solution**: Implement comprehensive error handling, user-friendly error messages, error logging

4. **Testing Coverage**
   - **Limitation**: Minimal test coverage (only [`test_auth.py`](backend/test_auth.py:1)), no frontend tests
   - **Impact**: Risk of regressions, harder to refactor with confidence
   - **Solution**: Comprehensive unit, integration, and E2E test suites

5. **Input Validation**
   - **Limitation**: Basic Pydantic validation, no comprehensive input sanitization
   - **Impact**: Potential for injection attacks, data integrity issues
   - **Solution**: Enhanced validation, sanitization middleware, rate limiting

6. **Real-time Features**
   - **Limitation**: No WebSocket support, polling required for real-time updates
   - **Impact**: Inefficient for messaging, poor user experience for notifications
   - **Solution**: Implement WebSocket support for messaging and notifications

7. **File Upload**
   - **Limitation**: No image/file upload capability for tasks
   - **Impact**: Limited task descriptions, no visual context
   - **Solution**: Implement file upload with cloud storage (S3, Cloudinary)

8. **Payment Processing**
   - **Limitation**: Manual payment tracking only, no actual payment processing
   - **Impact**: Not a complete marketplace solution
   - **Solution**: Integrate payment gateway (Stripe, PayPal)

9. **Production Configuration**
   - **Limitation**: No environment-based configuration, hardcoded values
   - **Impact**: Cannot deploy safely to production
   - **Solution**: Environment variables, configuration management, secrets management

10. **Monitoring & Observability**
    - **Limitation**: No logging, monitoring, or observability tools
    - **Impact**: Difficult to debug production issues, no performance metrics
    - **Solution**: Add structured logging, APM tools, error tracking (Sentry), metrics collection

11. **Mobile Responsiveness**
    - **Limitation**: Basic responsive design, not optimized for mobile
    - **Impact**: Suboptimal mobile user experience
    - **Solution**: Mobile-first design improvements, consider native apps

12. **Email Notifications**
    - **Limitation**: No email notification system
    - **Impact**: Users miss important updates (bid acceptance, messages)
    - **Solution**: Implement email service integration (SendGrid, AWS SES)