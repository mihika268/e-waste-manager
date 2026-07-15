#!/usr/bin/env python3
"""
Test script to verify login functionality and identify issues
"""

import requests
import json

def test_login_page():
    """Test if login page loads correctly"""
    try:
        response = requests.get('http://localhost:5000/login')
        
        if response.status_code == 200:
            print("✅ Login page loads successfully")
            return True
        else:
            print(f"❌ Login page failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing login page: {str(e)}")
        return False

def test_login_api():
    """Test the login API endpoint"""
    try:
        # Test with invalid credentials first
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Login API test - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Login API correctly rejects invalid credentials")
            return True
        else:
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login API: {str(e)}")
        return False

def test_api_endpoints():
    """Test all authentication endpoints"""
    endpoints = [
        '/api/auth/login',
        '/api/auth/send-otp',
        '/api/auth/verify-otp',
        '/api/auth/register'
    ]
    
    print("\n🔍 Testing API endpoints:")
    
    for endpoint in endpoints:
        try:
            response = requests.options(f'http://localhost:5000{endpoint}')
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: ERROR - {str(e)}")

def check_login_page_elements():
    """Check if login page has all required elements"""
    try:
        response = requests.get('http://localhost:5000/login')
        content = response.text
        
        required_elements = [
            'loginForm',
            'username',
            'password', 
            'loginBtn',
            'togglePassword'
        ]
        
        print("\n🔍 Checking login page elements:")
        
        for element in required_elements:
            if element in content:
                print(f"  ✅ {element} found")
            else:
                print(f"  ❌ {element} missing")
                
        # Check for JavaScript errors
        js_issues = []
        
        if 'getElementById' not in content:
            js_issues.append("No getElementById usage found")
            
        if 'addEventListener' not in content:
            js_issues.append("No event listeners found")
            
        if 'fetch(' not in content:
            js_issues.append("No fetch API usage found")
            
        if js_issues:
            print("  ⚠️  JavaScript concerns:")
            for issue in js_issues:
                print(f"    - {issue}")
        else:
            print("  ✅ JavaScript structure looks good")
            
    except Exception as e:
        print(f"❌ Error checking page elements: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing Login Functionality")
    print("=" * 40)
    
    # Test login page loading
    page_ok = test_login_page()
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test login API
    api_ok = test_login_api()
    
    # Check page elements
    check_login_page_elements()
    
    print("\n" + "=" * 40)
    print("📋 Test Results:")
    print(f"Login Page: {'✅ Working' if page_ok else '❌ Issues found'}")
    print(f"Login API: {'✅ Working' if api_ok else '❌ Issues found'}")
    
    if page_ok and api_ok:
        print("\n🎉 Login functionality appears to be working correctly!")
    else:
        print("\n⚠️  Some issues detected. Check the details above.")