#!/usr/bin/env python3
"""
Test script for registration functionality
"""

import requests
import json
import random
import string

def generate_test_user():
    """Generate test user data"""
    username = f"testuser_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
    email = f"{username}@example.com"
    
    return {
        "username": username,
        "email": email,
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "1234567890",
        "address": "123 Test Street, Test City"
    }

def test_registration_flow():
    """Test the complete registration flow"""
    base_url = "http://localhost:5000"
    
    # Generate test user data
    user_data = generate_test_user()
    print(f"Testing registration with user: {user_data['username']}")
    print(f"Email: {user_data['email']}")
    
    # Step 1: Send OTP
    print("\n1. Sending OTP...")
    otp_response = requests.post(
        f"{base_url}/api/auth/send-otp",
        json={"email": user_data["email"]}
    )
    
    print(f"OTP Response Status: {otp_response.status_code}")
    print(f"OTP Response: {otp_response.text}")
    
    if otp_response.status_code != 200:
        print("❌ Failed to send OTP")
        return False
    
    otp_data = otp_response.json()
    otp_code = otp_data.get('otp_code')
    
    if not otp_code:
        print("❌ No OTP code in response")
        return False
    
    print(f"✅ OTP sent successfully: {otp_code}")
    
    # Step 2: Verify OTP and register
    print("\n2. Verifying OTP and registering...")
    user_data["otp_code"] = otp_code
    
    register_response = requests.post(
        f"{base_url}/api/auth/verify-otp",
        json=user_data
    )
    
    print(f"Register Response Status: {register_response.status_code}")
    print(f"Register Response: {register_response.text}")
    
    if register_response.status_code != 201:
        print("❌ Registration failed")
        return False
    
    print("✅ Registration successful!")
    
    # Step 3: Test login
    print("\n3. Testing login...")
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"]
        }
    )
    
    print(f"Login Response Status: {login_response.status_code}")
    print(f"Login Response: {login_response.text}")
    
    if login_response.status_code == 200:
        print("✅ Login successful!")
        login_data = login_response.json()
        return login_data.get('access_token')
    else:
        print("❌ Login failed")
        return False

if __name__ == "__main__":
    print("Testing registration functionality...")
    token = test_registration_flow()
    
    if token:
        print(f"\n🎉 Registration test completed successfully!")
        print(f"Access token: {token[:20]}...")
    else:
        print("\n❌ Registration test failed!")