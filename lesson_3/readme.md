# Tasker Marketplace Platform

A full-stack marketplace application that connects local workers (taskers) with customers who need help with various tasks.

## Features

### For Customers
- Post tasks with descriptions, budgets, and deadlines
- Review and accept bids from taskers
- Make offers directly to taskers
- Secure payment processing
- Rate and review completed tasks
- Message system for communication

### For Taskers
- Browse available tasks
- Submit competitive bids
- Accept offers from customers
- Build reputation through reviews
- Set hourly rates and showcase skills

### Core Functionality
- User authentication and authorization
- Task creation and management
- Bidding system
- Agreement creation and management
- Review and rating system
- Secure messaging between users
- Task status tracking (open, in progress, completed, archived)

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database
- **JWT** - Authentication
- **Pydantic** - Data validation

### Frontend
- **React** - UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Vite** - Build tool and dev server

## Project Structure

```
lesson_1/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database configuration
│   ├── auth.py           # Authentication utilities
│   └── requirements.txt  # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/   # Reusable components
│   │   ├── App.jsx       # Main application
│   │   ├── AuthContext.jsx # Authentication context
│   │   ├── api.js        # API client
│   │   └── main.jsx      # Application entry point
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
└── docs/
    └── tasker.md         # Requirements documentation
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:3000`

## Usage Guide

### Getting Started

1. **Register an Account**
   - Choose between Customer or Tasker account type
   - For Tasker accounts, add your skills and hourly rate
   - Complete the registration form

2. **Login**
   - Use your username and password to login

### For Customers

1. **Create a Task**
   - Click "Create Task" in the navigation
   - Fill in task details (title, description, location, date, budget)
   - Submit the task

2. **Review Bids**
   - Visit the task detail page to see all bids
   - Review tasker proposals
   - Accept the best bid to create an agreement

3. **Complete Transaction**
   - Mark the task as completed once work is done
   - Mark the agreement as paid
   - Leave a review for the tasker

### For Taskers

1. **Browse Tasks**
   - View all available open tasks
   - Click on tasks to see details

2. **Submit Bids**
   - Enter your bid amount
   - Add a message explaining why you're the best fit
   - Submit your bid

3. **Complete Work**
   - Once a bid is accepted, complete the task
   - Wait for customer to mark as paid
   - Receive positive reviews to build reputation

### Messaging

- Use the Messages page to communicate
- Enter the recipient's user ID
- Optionally link messages to specific tasks
- Click unread messages to mark them as read

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /token` - Login and get access token
- `GET /users/me` - Get current user info

### Tasks
- `POST /tasks` - Create a new task (customers only)
- `GET /tasks` - List tasks
- `GET /tasks/{id}` - Get task details
- `PUT /tasks/{id}/status` - Update task status

### Bids
- `POST /bids` - Submit a bid (taskers only)
- `GET /bids/my-bids` - Get tasker's bids
- `PUT /bids/{id}/accept` - Accept a bid (customers only)

### Agreements
- `GET /agreements` - List user's agreements
- `PUT /agreements/{id}/pay` - Mark agreement as paid

### Reviews
- `POST /reviews` - Create a review
- `GET /reviews/tasker/{id}` - Get tasker reviews

### Messages
- `POST /messages` - Send a message
- `GET /messages` - List user's messages
- `PUT /messages/{id}/read` - Mark message as read

## Database Schema

The application uses SQLite with the following main tables:
- **users** - User accounts (customers and taskers)
- **tasks** - Posted tasks
- **bids** - Tasker bids on tasks
- **agreements** - Accepted bids creating work agreements
- **reviews** - Task completion reviews
- **messages** - User-to-user messages

## Security Features

- Password hashing using bcrypt
- JWT-based authentication
- Protected API endpoints
- User type authorization (customer vs tasker)
- CORS configuration for frontend

## Development Notes

- The backend runs on port 8000
- The frontend runs on port 3000
- API requests from frontend are proxied to backend
- SQLite database file `tasker.db` is created automatically
- Authentication tokens expire after 30 minutes

## Future Enhancements

- Email notifications
- Payment gateway integration
- Advanced search and filtering
- Real-time messaging with WebSockets
- File upload for task images
- Geolocation-based task matching
- In-app calendar integration
- Mobile responsive design improvements
- Admin dashboard for platform management

## Troubleshooting

**Backend won't start:**
- Ensure all dependencies are installed
- Check if port 8000 is already in use
- Verify Python version is 3.8+

**Frontend won't start:**
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check if port 3000 is already in use
- Verify Node.js version is 16+

**Can't login:**
- Verify backend is running
- Check browser console for errors
- Ensure you're using the correct username (not email)

**Database errors:**
- Delete `tasker.db` and restart backend to recreate tables
- Check database.py configuration

## Contributing

This is an MVP (Minimum Viable Product) built for learning purposes. Feel free to fork and enhance!

## License

This project is for educational purposes.
