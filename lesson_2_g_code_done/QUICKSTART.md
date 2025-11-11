# Quick Start Guide - Tasker Marketplace

Follow these steps to get the Tasker Marketplace platform running on your local machine.

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ Node.js 16 or higher installed
- ✅ A terminal/command prompt

## Step 1: Start the Backend Server

### Option A: Windows
```bash
cd backend
run.bat
```

### Option B: macOS/Linux
```bash
cd backend
chmod +x run.sh
./run.sh
```

### Option C: Manual Start
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✅ Backend is now running at http://localhost:8000
📚 API docs available at http://localhost:8000/docs

## Step 2: Start the Frontend (New Terminal)

Open a **new terminal window** and run:

```bash
cd frontend
npm install
npm run dev
```

**Expected Output:**
```
VITE ready in XXX ms
➜  Local:   http://localhost:3000/
```

✅ Frontend is now running at http://localhost:3000

## Step 3: Test the Application

1. **Open your browser** to http://localhost:3000

2. **Register a Customer Account:**
   - Click "Register"
   - Fill in the form:
     - Email: customer@test.com
     - Username: customer1
     - Password: password123
     - User Type: Customer
   - Click "Register"

3. **Login as Customer:**
   - Username: customer1
   - Password: password123

4. **Create a Task:**
   - Click "Create Task"
   - Fill in task details:
     - Title: "Help moving furniture"
     - Description: "Need help moving a sofa and dining table"
     - Location: "123 Main St, New York"
     - Date: Select a future date/time
     - Budget: 100
   - Click "Create Task"

5. **Logout and Register a Tasker:**
   - Click "Logout"
   - Click "Register"
   - Fill in the form:
     - Email: tasker@test.com
     - Username: tasker1
     - Password: password123
     - User Type: Tasker
     - Skills: "Moving, Furniture Assembly"
     - Hourly Rate: 25
   - Click "Register"

6. **Login as Tasker:**
   - Username: tasker1
   - Password: password123

7. **Browse and Bid on Tasks:**
   - Click "Tasks" to see available tasks
   - Click on the task you created
   - Submit a bid:
     - Bid Amount: 90
     - Message: "I have 5 years of experience with furniture moving!"
   - Click "Submit Bid"

8. **Switch to Customer and Accept Bid:**
   - Logout
   - Login as customer1
   - Click "Tasks"
   - Click on your task
   - You should see the tasker's bid
   - Click "Accept Bid"

9. **Complete the Transaction:**
   - Mark task as completed
   - Go to "Agreements"
   - Click "Mark as Paid"

10. **Test Messaging:**
    - Go to "Messages"
    - Send a message to the other user
    - Enter their User ID (you can find this in the task/bid details)

## Common Issues & Solutions

### Backend Issues

**Port 8000 already in use:**
```bash
# Kill the process using port 8000, then restart
```

**Module not found errors:**
```bash
cd backend
pip install -r requirements.txt --force-reinstall
```

**Database errors:**
```bash
# Delete the database and restart (it will be recreated)
cd backend
del tasker.db    # Windows
rm tasker.db     # macOS/Linux
```

### Frontend Issues

**Port 3000 already in use:**
- The Vite dev server will automatically use an alternative port
- Check the terminal output for the actual port

**Dependencies not installing:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Blank page or errors:**
- Check browser console for errors
- Ensure backend is running on port 8000
- Clear browser cache and reload

## Stopping the Application

1. **Stop Frontend:**
   - Press `Ctrl + C` in the frontend terminal

2. **Stop Backend:**
   - Press `Ctrl + C` in the backend terminal

## Next Steps

- Explore the API documentation at http://localhost:8000/docs
- Try creating multiple tasks and bids
- Test the messaging system
- Review the code to understand how it works
- Read the full README.md for more details

## API Testing with Swagger UI

The backend provides an interactive API documentation:

1. Visit http://localhost:8000/docs
2. Click "Authorize" and enter your token (get it from login)
3. Test all API endpoints directly from the browser

## Project Structure Overview

```
lesson_1/
├── backend/          # FastAPI backend
│   ├── main.py      # API endpoints
│   ├── models.py    # Database models
│   ├── schemas.py   # Request/response schemas
│   └── auth.py      # Authentication
│
└── frontend/        # React frontend
    └── src/
        ├── pages/   # Page components
        ├── App.jsx  # Main app
        └── api.js   # API client
```

## Tips for Development

- Keep both terminals open while developing
- Backend auto-reloads on file changes (--reload flag)
- Frontend auto-reloads on file changes (Vite HMR)
- Check browser DevTools for frontend errors
- Check terminal output for backend errors

Happy coding! 🚀