import requests
import json

url = "http://localhost:8000/register"
data = {
    "email": "jane.smith@example.com",
    "password": "password123",
    "full_name": "Jane Smith",
    "role": "tasker",
    "phone": "555-5678",
    "location": "Brooklyn, NY",
    "skills": "Plumbing, Electrical, Carpentry",
    "hourly_rate": 45.50,
    "bio": "Licensed professional with 10 years of experience.\nSpecializing in residential repairs and installations."
}

response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")