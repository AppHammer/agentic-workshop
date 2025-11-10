#!/bin/bash
echo "Starting Tasker Backend Server..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "Starting server at http://localhost:8000"
echo "API Documentation available at http://localhost:8000/docs"
echo ""
uvicorn main:app --reload