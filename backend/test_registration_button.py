#!/usr/bin/env python3
"""
Test the registration button functionality by simulating the frontend behavior
"""

import requests
import json

def test_registration_button():
    """Test the registration button functionality"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Registration Button Functionality")
    print("=" * 60)
    
    # Test 1: Check if the registration page loads
    print("\n1. Testing page load...")
    try:
        response = requests.get(f"{base_url}/register")
        print(f"   Page status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Registration page loads successfully")
            
            # Check if required elements exist
            html_content = response.text
            required_elements = [
                'id="registerForm"',
                'id="registerBtn"',
                'id="registerBtnText"',
                'id="registerSpinner"'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in html_content:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"   ❌ Missing elements: {missing_elements}")
            else:
                print("   ✅ All required elements found in HTML")
        else:
            print(f"   ❌ Registration page failed to load")
            return
            
    except Exception as e:
        print(f"   ❌ Error loading page: {e}")
        return
    
    # Test 2: Test the registration API endpoints
    print("\n2. Testing registration API endpoints...")
    
    # Test data
    test_data = {
        "first_name": "TestButton",
        "last_name": "User",
        "email": "testbutton@example.com",
        "username": "testbutton",
        "password": "testpass123"
    }
    
    # Step 2a: Send OTP
    print("\n   2a. Testing OTP sending...")
    try:
        response = requests.post(f"{base_url}/api/auth/send-otp", 
                               json={"email": test_data["email"]})
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            otp_data = response.json()
            otp_code = otp_data.get('otp_code')
            print(f"      ✅ OTP sent successfully: {otp_code}")
        else:
            print(f"      ❌ OTP sending failed: {response.json()}")
            return
            
    except Exception as e:
        print(f"      ❌ Error sending OTP: {e}")
        return
    
    # Step 2b: Complete registration
    print("\n   2b. Testing registration completion...")
    try:
        registration_data = {
            **test_data,
            "otp_code": otp_code
        }
        
        response = requests.post(f"{base_url}/api/auth/register-with-otp", 
                               json=registration_data)
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 201:
            print(f"      ✅ Registration completed successfully!")
            result_data = response.json()
            print(f"      Token: {result_data.get('access_token', 'No token')[:20]}...")
            print(f"      User: {result_data.get('user', {}).get('username')}")
            
            # Test login with new credentials
            print("\n   2c. Testing login with new credentials...")
            login_data = {
                "username": test_data["username"],
                "password": test_data["password"]
            }
            
            login_response = requests.post(f"{base_url}/api/auth/login", 
                                         json=login_data)
            print(f"      Login status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                print(f"      ✅ Login successful!")
            else:
                print(f"      ❌ Login failed: {login_response.json()}")
                
        else:
            print(f"      ❌ Registration failed: {response.json()}")
            
    except Exception as e:
        print(f"      ❌ Error completing registration: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Registration Button Test Complete!")
    print("\nIf all tests pass, the button functionality works.")
    print("If tests fail, check:")
    print("- Server logs for errors")
    print("- JavaScript console for errors")
    print("- Network tab for failed requests")

if __name__ == "__main__":
    test_registration_button()