#!/usr/bin/env python3
"""
Comprehensive test script for the registration flow improvements
Tests all the enhanced functionality added to the registration page
"""

import requests
import json
import random
import string
import time

def generate_test_user():
    """Generate random test user data"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "first_name": f"Test{random_str.capitalize()}",
        "last_name": f"User{random_str.capitalize()}",
        "username": f"testuser_{random_str}",
        "email": f"test_{random_str}@example.com",
        "phone": f"+123456789{random.randint(0, 9999):04d}",
        "address": f"123 Test Street, Test City, TC {random.randint(10000, 99999)}",
        "password": "TestPassword123!"
    }

def test_registration_flow():
    """Test the complete registration flow with OTP"""
    base_url = "http://localhost:5000/api/auth"
    
    print("🧪 Testing Registration Flow Improvements")
    print("=" * 50)
    
    # Generate test user
    user_data = generate_test_user()
    print(f"📋 Generated test user: {user_data['username']}")
    
    try:
        # Step 1: Send OTP
        print("\n1️⃣ Testing OTP sending...")
        otp_response = requests.post(
            f"{base_url}/send-otp",
            json={"email": user_data["email"]},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {otp_response.status_code}")
        if otp_response.status_code == 200:
            otp_data = otp_response.json()
            print(f"   ✅ OTP sent successfully")
            print(f"   Response: {otp_data}")
            
            # Extract OTP from response (for testing)
            if 'otp_code' in otp_data:
                otp_code = otp_data['otp_code']
                print(f"   📧 OTP Code (for testing): {otp_code}")
            else:
                print("   ⚠️  OTP code not found in response")
                return False
        else:
            print(f"   ❌ Failed to send OTP: {otp_response.text}")
            return False
        
        # Step 2: Register user with OTP
        print("\n2️⃣ Testing user registration with OTP...")
        user_data["otp_code"] = otp_code
        
        register_response = requests.post(
            f"{base_url}/register-with-otp",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {register_response.status_code}")
        if register_response.status_code == 201:
            register_data = register_response.json()
            print(f"   ✅ User registered successfully")
            print(f"   Access token: {register_data.get('access_token', 'Not provided')[:20]}...")
            print(f"   User ID: {register_data.get('user', {}).get('id', 'Not provided')}")
            
            # Store token for login test
            access_token = register_data.get('access_token')
        else:
            print(f"   ❌ Registration failed: {register_response.text}")
            return False
        
        # Step 3: Test login with new credentials
        print("\n3️⃣ Testing login with new account...")
        login_response = requests.post(
            f"{base_url}/login",
            json={
                "username": user_data["email"],  # Can use email as username
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {login_response.status_code}")
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f"   ✅ Login successful")
            print(f"   New access token: {login_data.get('access_token', 'Not provided')[:20]}...")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
        
        # Step 4: Test OTP resend functionality
        print("\n4️⃣ Testing OTP resend functionality...")
        time.sleep(1)  # Small delay before resend
        
        resend_response = requests.post(
            f"{base_url}/resend-otp",
            json={"email": user_data["email"]},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {resend_response.status_code}")
        if resend_response.status_code == 200:
            resend_data = resend_response.json()
            print(f"   ✅ OTP resent successfully")
            print(f"   Response: {resend_data}")
        else:
            print(f"   ⚠️  Resend failed (expected for existing user): {resend_response.text}")
        
        print("\n🎉 All registration flow tests passed!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def test_validation_scenarios():
    """Test various validation scenarios"""
    print("\n\n🔍 Testing Validation Scenarios")
    print("=" * 50)
    
    base_url = "http://localhost:5000/api/auth"
    
    # Test invalid email
    print("\n1️⃣ Testing invalid email validation...")
    response = requests.post(
        f"{base_url}/send-otp",
        json={"email": "invalid-email"},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        print(f"   ✅ Invalid email properly rejected")
    else:
        print(f"   ⚠️  Invalid email accepted (unexpected)")
    
    # Test weak password
    print("\n2️⃣ Testing weak password validation...")
    test_user = generate_test_user()
    test_user["password"] = "123"  # Weak password
    test_user["otp_code"] = "123456"
    
    response = requests.post(
        f"{base_url}/register-with-otp",
        json=test_user,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        print(f"   ✅ Weak password properly rejected")
    else:
        print(f"   ⚠️  Weak password accepted (unexpected)")
    
    print("\n✅ Validation tests completed!")

if __name__ == "__main__":
    print("🚀 Starting Registration Flow Tests")
    print("Make sure the Flask server is running on localhost:5000")
    print()
    
    # Test main registration flow
    success = test_registration_flow()
    
    # Test validation scenarios
    test_validation_scenarios()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above.")