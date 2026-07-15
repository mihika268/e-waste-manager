#!/usr/bin/env python3
"""
Simple test to debug registration OTP issue
"""

import requests
import json

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_registration_endpoints():
    """Test all registration endpoints individually"""
    
    test_email = "newuser@example.com"
    
    print("=== Testing Registration Endpoints ===\n")
    
    # Test 1: Send OTP
    print("1. Testing /api/auth/send-otp")
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
            if result.get('otp_code'):
                print(f"   OTP Code: {result['otp_code']}")
                return result['otp_code']
        else:
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   Exception: {e}")
        return None

def test_otp_verification(email, otp_code):
    """Test OTP verification"""
    print(f"\n2. Testing /api/auth/verify-otp-only with OTP: {otp_code}")
    try:
        response = requests.post(
            f"{API_BASE}/auth/verify-otp-only",
            json={"email": email, "otp_code": otp_code},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('message', 'No message')}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def test_registration_completion(email, otp_code):
    """Test registration completion"""
    print(f"\n3. Testing /api/auth/register-with-otp")
    registration_data = {
        "email": email,
        "otp_code": otp_code,
        "username": "testuser123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "1234567890",
        "password": "testpassword123",
        "confirm_password": "testpassword123"
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
            print(f"   Access Token: {result.get('access_token', 'No token')}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def main():
    print("🚀 Testing Registration Flow")
    print("=" * 40)
    
    # Test send OTP
    otp_code = test_registration_endpoints()
    
    if otp_code:
        # Test OTP verification
        if test_otp_verification("testuser@example.com", otp_code):
            # Test registration completion
            test_registration_completion("testuser@example.com", otp_code)
        else:
            print("\n❌ OTP verification failed - checking common issues...")
            
            # Check if OTP is expired
            print("\n💡 Common OTP issues:")
            print("   - OTP expired (valid for 5 minutes)")
            print("   - Wrong email/OTP combination")
            print("   - OTP already used")
            print("   - Email service not configured properly")
            print("\n🔧 Try using the manual OTP method in test_registration_flow.py")
    else:
        print("\n❌ Could not get OTP - check server logs for email sending issues")

if __name__ == "__main__":
    main()