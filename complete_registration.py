#!/usr/bin/env python3
"""
Complete registration with generated OTP code
"""

import requests

def complete_registration(email, otp_code):
    """Complete registration with OTP code"""
    
    register_data = {
        'email': email,
        'password': 'TestPassword123',
        'first_name': 'Test',
        'last_name': 'User',
        'otp_code': otp_code
    }
    
    print(f"Completing registration for {email}...")
    response = requests.post('http://localhost:5000/api/auth/register-with-otp', json=register_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print("✅ Registration successful!")
        print(f"User ID: {data['user']['id']}")
        print(f"Access Token: {data['access_token'][:20]}...")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_login(email):
    """Test login with the new account"""
    
    login_data = {
        'username': email,  # Use 'username' field but pass email as value
        'password': 'TestPassword123'
    }
    
    print(f"\nTesting login for {email}...")
    response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"Access Token: {data['access_token'][:20]}...")
        return True
    else:
        print(f"❌ Login failed: {response.text}")
        return False

if __name__ == "__main__":
    # Use the email and OTP from our previous test
    email = "test_fqn3fjce@example.com"
    otp_code = "288353"
    
    print("🚀 Completing Registration Test")
    print("=" * 40)
    
    # Complete registration
    success = complete_registration(email, otp_code)
    
    if success:
        # Test login
        login_success = test_login(email)
        
        if login_success:
            print("\n🎉 COMPLETE SUCCESS!")
            print("✅ OTP Generation: Working")
            print("✅ Registration: Working") 
            print("✅ Login: Working")
            print("\nThe only issue is email delivery!")
        else:
            print("\n❌ Login test failed")
    else:
        print("\n❌ Registration failed")