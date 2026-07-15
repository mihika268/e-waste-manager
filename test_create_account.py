#!/usr/bin/env python3
"""
Test the create account functionality comprehensively
"""

import requests
import json
import random
import string
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/auth"

def generate_test_email():
    """Generate a unique test email"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"testuser_{timestamp}@example.com"

def test_create_account_flow():
    """Test the complete account creation flow"""
    print("🚀 Testing Create Account Functionality")
    print("=" * 50)
    
    # Generate unique test data
    test_email = generate_test_email()
    test_username = f"testuser_{datetime.now().strftime('%H%M%S')}"
    test_password = "Test123456!"
    test_first_name = "Test"
    test_last_name = "User"
    test_phone = "1234567890"
    
    print(f"Test Email: {test_email}")
    print(f"Test Username: {test_username}")
    print()
    
    success_count = 0
    total_tests = 4
    
    # Step 1: Send OTP
    print("1️⃣ Testing OTP Sending...")
    try:
        response = requests.post(
            f"{API_BASE}/send-otp",
            json={"email": test_email},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            otp_code = result.get('otp_code', 'UNKNOWN')
            print(f"   ✅ OTP sent successfully: {otp_code}")
            success_count += 1
        else:
            print(f"   ❌ Failed to send OTP: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error sending OTP: {e}")
        return False
    
    # Step 2: Verify OTP
    print("\n2️⃣ Testing OTP Verification...")
    try:
        response = requests.post(
            f"{API_BASE}/verify-otp-only",
            json={"email": test_email, "otp_code": otp_code},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("   ✅ OTP verified successfully")
            success_count += 1
        else:
            print(f"   ❌ OTP verification failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying OTP: {e}")
        return False
    
    # Step 3: Create Account
    print("\n3️⃣ Testing Account Creation...")
    account_data = {
        "email": test_email,
        "otp_code": otp_code,
        "username": test_username,
        "first_name": test_first_name,
        "last_name": test_last_name,
        "phone": test_phone,
        "password": test_password,
        "confirm_password": test_password
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/register-with-otp",
            json=account_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            access_token = result.get('access_token')
            user_data = result.get('user', {})
            print("   ✅ Account created successfully!")
            print(f"   User ID: {user_data.get('id', 'Unknown')}")
            print(f"   Username: {user_data.get('username', 'Unknown')}")
            print(f"   Access Token: {access_token[:20]}..." if access_token else "   No access token received")
            success_count += 1
        else:
            print(f"   ❌ Account creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error creating account: {e}")
        return False
    
    # Step 4: Test Login with New Account
    print("\n4️⃣ Testing Login with New Account...")
    try:
        response = requests.post(
            f"{API_BASE}/login",
            json={"username": test_username, "password": test_password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Login successful!")
            print(f"   Welcome {result.get('user', {}).get('username', 'Unknown')}")
            success_count += 1
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error logging in: {e}")
    
    # Summary
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Create account functionality is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

def test_validation_errors():
    """Test validation and error handling"""
    print("\n🔍 Testing Validation and Error Handling")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Invalid email format
    print("1️⃣ Testing Invalid Email Format...")
    try:
        response = requests.post(
            f"{API_BASE}/send-otp",
            json={"email": "invalid-email"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("   ✅ Correctly rejected invalid email format")
            success_count += 1
        else:
            print(f"   ❌ Should reject invalid email format: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Weak password
    print("\n2️⃣ Testing Weak Password...")
    test_email = generate_test_email()
    try:
        # Send OTP
        response = requests.post(
            f"{API_BASE}/send-otp",
            json={"email": test_email},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            otp_code = result.get('otp_code', 'UNKNOWN')
            
            # Try to create account with weak password
            account_data = {
                "email": test_email,
                "otp_code": otp_code,
                "username": f"weakuser_{datetime.now().strftime('%H%M%S')}",
                "first_name": "Test",
                "last_name": "User",
                "phone": "1234567890",
                "password": "123",
                "confirm_password": "123"
            }
            
            response = requests.post(
                f"{API_BASE}/register-with-otp",
                json=account_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                print("   ✅ Correctly rejected weak password")
                success_count += 1
            else:
                print(f"   ❌ Should reject weak password: {response.status_code}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Password mismatch
    print("\n3️⃣ Testing Password Mismatch...")
    try:
        # Try to create account with mismatched passwords
        account_data = {
            "email": generate_test_email(),
            "otp_code": "123456",
            "username": f"mismatchuser_{datetime.now().strftime('%H%M%S')}",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890",
            "password": "password123",
            "confirm_password": "different123"
        }
        
        response = requests.post(
            f"{API_BASE}/register-with-otp",
            json=account_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("   ✅ Correctly rejected password mismatch")
            success_count += 1
        else:
            print(f"   ❌ Should reject password mismatch: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Validation Tests: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

if __name__ == "__main__":
    print("Starting Create Account Functionality Tests...")
    print("Make sure the server is running on http://localhost:5000")
    print()
    
    # Test main functionality
    main_tests_passed = test_create_account_flow()
    
    # Test validation
    validation_tests_passed = test_validation_errors()
    
    print(f"\n🎯 Overall Results:")
    print(f"   Main Functionality: {'✅ PASSED' if main_tests_passed else '❌ FAILED'}")
    print(f"   Validation Tests: {'✅ PASSED' if validation_tests_passed else '❌ FAILED'}")
    
    if main_tests_passed and validation_tests_passed:
        print("\n🎉 All tests passed! The create account section is working properly.")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")