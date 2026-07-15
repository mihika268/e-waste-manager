#!/usr/bin/env python3
"""
Create a fresh test user using proper registration flow
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def create_fresh_test_user():
    """Create a fresh test user using proper OTP registration"""
    
    test_email = "freshtest@example.com"
    
    print("=== Creating Fresh Test User ===\n")
    
    # Step 1: Send OTP
    print("1. Sending OTP...")
    try:
        response = requests.post(
            f"{API_BASE}/auth/send-otp",
            json={"email": test_email},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('message', 'No message')}")
            otp_code = result.get('otp_code')
            if otp_code:
                print(f"   OTP Code: {otp_code}")
            else:
                print("   ❌ No OTP code in response")
                return None
        else:
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   Exception: {e}")
        return None
    
    # Step 2: Complete registration
    print(f"\n2. Completing registration with OTP: {otp_code}")
    registration_data = {
        "email": test_email,
        "otp_code": otp_code,
        "first_name": "Fresh",
        "last_name": "Test",
        "password": "testpass123",
        "confirm_password": "testpass123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register-with-otp",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"   Success: {result.get('message', 'No message')}")
            print(f"   Username: {result.get('user', {}).get('username', 'No username')}")
            print(f"   Access Token: {result.get('access_token', 'No token')}")
            return {
                'username': result.get('user', {}).get('username'),
                'email': test_email,
                'password': 'testpass123',
                'token': result.get('access_token')
            }
        else:
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   Exception: {e}")
        return None

def test_login_with_fresh_user(user_data):
    """Test login with the fresh user"""
    
    print(f"\n3. Testing login with fresh user: {user_data['username']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": user_data['username'], "password": user_data['password']},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login successful!")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   User: {result.get('user', {}).get('username', 'No username')}")
            return True
        else:
            print(f"   ❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating Fresh Test User and Testing Login")
    print("=" * 50)
    
    # Create fresh user
    user_data = create_fresh_test_user()
    
    if user_data:
        # Test login with fresh user
        if test_login_with_fresh_user(user_data):
            print(f"\n🎉 SUCCESS! Fresh user created and login works!")
            print(f"📋 Test Account Details:")
            print(f"   Username: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"\n🔧 You can now use these credentials to test the login system!")
        else:
            print(f"\n❌ Login failed even with fresh user!")
    else:
        print(f"\n❌ Failed to create fresh test user!")