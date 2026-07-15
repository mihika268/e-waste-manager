#!/usr/bin/env python3
"""
Debug analytics API issues
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Login first
login_data = {
    "username": "john_doe",
    "password": "password123"
}

response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
token = response.json().get('access_token')

headers = {"Authorization": f"Bearer {token}"}

# Test analytics endpoint
response = requests.get(f"{BASE_URL}/api/analytics/dashboard", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")