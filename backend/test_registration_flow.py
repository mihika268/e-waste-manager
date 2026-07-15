#!/usr/bin/env python3
"""
Test the complete registration flow to identify issues
"""

import requests
import json

def test_registration_flow():
    """Test the complete registration flow"""
    
    base_url = "http://localhost:5000"
    
    # Test data
    test_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testregister@example.com",
        "username": "testregister",
        "password": "testpass123"
    }
    
    print("🧪 Testing Registration Flow")
    print("=" * 50)
    
    # Step 1: Send OTP
    print("\n1. Sending OTP...")
    try:
        response = requests.post(f"{base_url}/api/auth/send-otp", 
                               json={"email": test_data["email"]})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            otp_data = response.json()
            otp_code = otp_data.get('otp_code')
            print(f"   ✅ OTP received: {otp_code}")
        else:
            print(f"   ❌ Failed to get OTP")
            return
            
    except Exception as e:
        print(f"   ❌ Error sending OTP: {e}")
        return
    
    # Step 2: Complete registration with OTP
    print("\n2. Completing registration...")
    try:
        registration_data = {
            **test_data,
            "otp_code": otp_code
        }
        
        response = requests.post(f"{base_url}/api/auth/register-with-otp", 
                               json=registration_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 201:
            print(f"   ✅ Registration successful!")
            result_data = response.json()
            print(f"   Token: {result_data.get('access_token', 'No token')[:20]}...")
            print(f"   User: {result_data.get('user', {}).get('username')}")
        else:
            print(f"   ❌ Registration failed")
            
    except Exception as e:
        print(f"   ❌ Error completing registration: {e}")
    
    # Step 3: Test login with new credentials
    print("\n3. Testing login...")
    try:
        login_data = {
            "username": test_data["username"],
            "password": test_data["password"]
        }
        
        response = requests.post(f"{base_url}/api/auth/login", 
                               json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Login successful!")
            login_result = response.json()
            print(f"   Token: {login_result.get('access_token', 'No token')[:20]}...")
        else:
            print(f"   ❌ Login failed")
            print(f"   Response: {response.json()}")
            
    except Exception as e:
        print(f"   ❌ Error testing login: {e}")

if __name__ == "__main__":
    test_registration_flow()