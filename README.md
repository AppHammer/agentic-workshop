# Agentic Workshop

This repository contains the Tasker Platform - a marketplace to connect local workers (taskers) with customers who need help with various tasks.

## Tasker Platform

The Tasker Platform is located in the [`app/`](app/) directory and consists of:
- **Backend**: FastAPI-based REST API with SQLite database
- **Frontend**: React single-page application

For full details about the platform features, see [`docs/tasker.md`](docs/tasker.md).

---

## Prerequisites

1. **Python 3.11 or higher** - For the FastAPI backend
2. **Node.js 16 or higher** - For the React frontend
3. **npm** - Comes with Node.js

---

## Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd app/backend
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd app/frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

---

## Running the Application

### Start the Backend Server

1. Make sure you're in the [`app/backend`](app/backend/) directory with the virtual environment activated

2. Run the FastAPI server:
   ```bash
   python main.py
   ```

   The backend API will start at: **http://localhost:8000**

   You can view the API documentation at: **http://localhost:8000/docs**

### Start the Frontend Application

1. In a separate terminal, navigate to the [`app/frontend`](app/frontend/) directory

2. Start the React development server:
   ```bash
   npm start
   ```

   The frontend will automatically open in your browser at: **http://localhost:3000**

---

## Using the Application

### First Time Setup

1. **Register an Account:**
   - Click "Register here" on the login page
   - Fill in your details
   - Choose your role:
     - **Customer** - To post tasks and hire taskers
     - **Tasker** - To find work and bid on tasks

2. **Login:**
   - Use your email and password to login
   - You'll be redirected to your role-specific dashboard

### Customer Workflow

1. **Post a Task:**
   - Click "Post New Task" on your dashboard
   - Fill in task details (title, description, location, date, budget)
   - Submit to create the task

2. **Review Bids:**
   - Click on a task to view details
   - See all bids from taskers
   - Accept a bid to create an agreement

3. **Make an Offer:**
   - Alternative to accepting bids
   - Select a tasker who bid on your task
   - Make a custom offer

4. **Complete Task:**
   - Once work is done, mark the task as complete
   - Submit a review and rating

### Tasker Workflow

1. **Browse Tasks:**
   - View available tasks on your dashboard or the "Browse Tasks" page
   - Filter by status (open, in_progress, completed)

2. **Place a Bid:**
   - Click on a task to view details
   - Enter your bid amount and message
   - Submit your bid

3. **Accept Offers:**
   - If a customer makes you an offer, you'll see it on the task page
   - Accept the offer to create an agreement

4. **Complete Work:**
   - Work on agreed tasks
   - Wait for customer to mark as complete
   - Submit a review and rating

### Messaging

- Navigate to the "Messages" page
- View conversations with other users
- Send and receive messages related to tasks

---

## Project Structure

```
app/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # SQLAlchemy models and database config
│   ├── auth.py              # Authentication and JWT handling
│   ├── schemas.py           # Pydantic schemas for validation
│   ├── requirements.txt     # Python dependencies
│   └── tasker.db           # SQLite database (created on first run)
│
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── components/      # React components
    │   │   ├── Login.js
    │   │   ├── Register.js
    │   │   ├── CustomerDashboard.js
    │   │   ├── TaskerDashboard.js
    │   │   ├── TaskList.js
    │   │   ├── TaskDetail.js
    │   │   ├── Messages.js
    │   │   └── Navbar.js
    │   ├── App.js          # Main React component
    │   ├── api.js          # API client functions
    │   ├── index.js        # React entry point
    │   └── index.css       # Global styles
    └── package.json        # Node.js dependencies
```

---

## Features

- ✅ **User Authentication** - Secure JWT-based authentication
- ✅ **Task Management** - Create, view, and manage tasks
- ✅ **Bidding System** - Taskers can bid on tasks
- ✅ **Offer System** - Customers can make offers to taskers
- ✅ **Agreement System** - Track accepted bids/offers
- ✅ **Messaging** - Secure communication between users
- ✅ **Reviews & Ratings** - Rate and review completed tasks
- ✅ **Role-Based Dashboards** - Different interfaces for customers and taskers

---

## Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - SQL toolkit and ORM
- SQLite - Lightweight database
- JWT - Secure authentication
- Pydantic - Data validation

**Frontend:**
- React - UI framework
- React Router - Navigation
- Axios - HTTP client

---

## API Documentation

Once the backend is running, visit **http://localhost:8000/docs** to view the interactive API documentation (Swagger UI).

Key endpoints:
- `POST /register` - Register new user
- `POST /token` - Login and get access token
- `GET /tasks` - List all tasks
- `POST /tasks` - Create a new task
- `POST /bids` - Place a bid on a task
- `POST /offers` - Make an offer to a tasker
- `POST /messages` - Send a message
- `POST /reviews` - Submit a review

---

## Development Notes

- The backend runs on port **8000**
- The frontend runs on port **3000**
- The database is created automatically on first run
- Authentication tokens are stored in browser localStorage
- CORS is configured to allow frontend-backend communication

---

## Troubleshooting

**Backend won't start:**
- Ensure Python 3.11+ is installed: `python --version`
- Check that virtual environment is activated
- Verify all dependencies are installed: `pip list`

**Frontend won't start:**
- Ensure Node.js is installed: `node --version`
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Check that port 3000 is not in use

**Database errors:**
- Delete `tasker.db` and restart the backend to recreate the database

**CORS errors:**
- Ensure backend is running on port 8000
- Ensure frontend is running on port 3000

---

## License

This project is for educational purposes.