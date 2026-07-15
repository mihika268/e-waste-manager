#!/usr/bin/env python3
"""
Simple login test with existing user
"""

import requests
import json

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_login_with_existing_user():
    """Test login with a known existing user"""
    
    # Test with various password combinations
    test_credentials = [
        {"username": "testuser_171516", "password": "testpassword123"},
        {"username": "testuser_171516", "password": "Test123456!"},
        {"username": "testuser_171516", "password": "Test123!"},
        {"username": "testuser_171516", "password": "password123"},
        {"username": "testuser_171516", "password": "password"},
        {"username": "testuser_171516", "password": "123456"},
    ]
    
    print("=== Testing Login with Existing User ===\n")
    
    for i, creds in enumerate(test_credentials):
        print(f"{i+1}. Testing: username='{creds['username']}', password='{creds['password']}'")
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json=creds,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS! Login worked!")
                print(f"   Message: {result.get('message', 'No message')}")
                print(f"   User: {result.get('user', {}).get('username', 'No username')}")
                print(f"   Token: {result.get('access_token', 'No token')[:20]}...")
                return True
            else:
                result = response.json()
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   Exception: {e}")
        
        print()  # Empty line for readability
    
    return False

def test_with_admin_user():
    """Test with admin user if exists"""
    
    # Check for admin users
    print("=== Checking for Admin Users ===")
    
    # Try common admin credentials
    admin_creds = [
        {"username": "admin", "password": "admin123"},
        {"username": "admin", "password": "password"},
        {"username": "admin", "password": "admin"},
        {"username": "administrator", "password": "admin123"},
    ]
    
    for creds in admin_creds:
        print(f"Testing admin: username='{creds['username']}', password='{creds['password']}'")
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json=creds,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Admin login successful!")
                print(f"   Message: {result.get('message', 'No message')}")
                print(f"   User: {result.get('user', {}).get('username', 'No username')}")
                return True
            else:
                result = response.json()
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   Exception: {e}")
        
        print()
    
    return False

if __name__ == "__main__":
    print("🚀 Testing Login Functionality")
    print("=" * 50)
    
    # Test with existing user
    success = test_login_with_existing_user()
    
    if not success:
        # Test with admin user
        success = test_with_admin_user()
    
    if success:
        print("🎉 Login test successful!")
    else:
        print("❌ All login tests failed!")
        print("\n🔧 Troubleshooting suggestions:")
        print("   1. Check if users exist in database")
        print("   2. Verify user passwords in database")
        print("   3. Check if users are active and verified")
        print("   4. Try creating a new user with registration flow")