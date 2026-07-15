#!/usr/bin/env python3
"""
Test script to verify login functionality with a real user
"""

import requests
import json

def create_test_user():
    """Create a test user for login testing"""
    try:
        # Register a test user
        register_data = {
            'username': 'testuser',
            'password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '1234567890'
        }
        
        response = requests.post(
            'http://localhost:5000/api/auth/register',
            json=register_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"User registration - Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Test user created successfully")
            return True
        elif response.status_code == 400:
            result = response.json()
            if 'already exists' in result.get('error', ''):
                print("ℹ️  Test user already exists")
                return True
            else:
                print(f"❌ Registration failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")
        return False

def test_successful_login():
    """Test successful login with valid credentials"""
    try:
        login_data = {
            'username': 'testuser',
            'password': 'Test@123'
        }
        
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Successful login test - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successful login works!")
            print(f"  - Token received: {result.get('access_token') is not None}")
            print(f"  - User data: {result.get('user', {}).get('username')}")
            return True
        else:
            result = response.json()
            print(f"❌ Login failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing successful login: {str(e)}")
        return False

def test_invalid_login():
    """Test login with invalid credentials"""
    test_cases = [
        {'username': 'wronguser', 'password': 'wrongpass'},
        {'username': 'testuser', 'password': 'wrongpass'},
        {'username': '', 'password': ''},
        {'username': 'testuser'}  # Missing password
    ]
    
    print("\n🔍 Testing invalid login scenarios:")
    
    for i, test_data in enumerate(test_cases):
        try:
            response = requests.post(
                'http://localhost:5000/api/auth/login',
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"  Test {i+1}: {response.status_code} - {response.json().get('error', 'No error message')}")
            
        except Exception as e:
            print(f"  Test {i+1}: ERROR - {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing Login with Real User")
    print("=" * 40)
    
    # Create test user
    user_created = create_test_user()
    
    if user_created:
        # Test successful login
        login_works = test_successful_login()
        
        # Test invalid login scenarios
        test_invalid_login()
        
        print("\n" + "=" * 40)
        print("📋 Test Results:")
        print(f"Test User: {'✅ Created/Exists' if user_created else '❌ Failed'}")
        print(f"Login Functionality: {'✅ Working' if login_works else '❌ Issues found'}")
        
        if user_created and login_works:
            print("\n🎉 Login system is working perfectly!")
            print("\n💡 You can now test the login page manually:")
            print("   - Username: testuser")
            print("   - Password: Test@123")
        else:
            print("\n⚠️  Some issues detected. Check the details above.")
    else:
        print("\n❌ Could not create test user. Login testing aborted.")