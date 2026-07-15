#!/usr/bin/env python3
"""
Final comprehensive test for the login page functionality
"""

import requests
import json
import time

def test_login_page_elements():
    """Test that all login page elements are working"""
    print("🔍 Testing Login Page Elements")
    print("=" * 40)
    
    try:
        # Test page loading
        response = requests.get('http://localhost:5000/login')
        
        if response.status_code == 200:
            print("✅ Login page loads successfully")
            
            # Check for essential elements in the HTML
            html_content = response.text
            
            # Check for form elements
            checks = [
                ('Login form', '<form id="loginForm"'),
                ('Username input', 'name="username"'),
                ('Password input', 'name="password"'),
                ('Login button', 'id="loginBtn"'),
                ('Password toggle', 'id="togglePassword"'),
                ('Remember me checkbox', 'id="rememberMe"'),
                ('Register link', 'href="/register"'),
            ]
            
            all_found = True
            for element_name, search_pattern in checks:
                if search_pattern in html_content:
                    print(f"  ✅ {element_name} found")
                else:
                    print(f"  ❌ {element_name} missing")
                    all_found = False
            
            return all_found
        else:
            print(f"❌ Login page failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login page: {str(e)}")
        return False

def test_login_form_submission():
    """Test the login form submission functionality"""
    print("\n🔍 Testing Login Form Submission")
    print("=" * 40)
    
    try:
        # Test successful login with testuser (verified)
        login_data = {
            'username': 'testuser',
            'password': 'Test@123'
        }
        
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful")
            print(f"  - Access token received: {result.get('access_token') is not None}")
            print(f"  - User info: {result.get('user', {}).get('username')}")
            print(f"  - Email verified: {result.get('user', {}).get('is_verified')}")
            return True
        else:
            result = response.json()
            print(f"❌ Login failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login form: {str(e)}")
        return False

def test_invalid_login_scenarios():
    """Test various invalid login scenarios"""
    print("\n🔍 Testing Invalid Login Scenarios")
    print("=" * 40)
    
    test_cases = [
        {
            'name': 'Wrong password',
            'data': {'username': 'testuser', 'password': 'wrongpassword'},
            'expected_status': 401
        },
        {
            'name': 'Non-existent user',
            'data': {'username': 'nonexistent', 'password': 'password123'},
            'expected_status': 401
        },
        {
            'name': 'Empty username',
            'data': {'username': '', 'password': 'password123'},
            'expected_status': 400
        },
        {
            'name': 'Empty password',
            'data': {'username': 'testuser', 'password': ''},
            'expected_status': 400
        },
        {
            'name': 'Missing username',
            'data': {'password': 'password123'},
            'expected_status': 400
        },
        {
            'name': 'Missing password',
            'data': {'username': 'testuser'},
            'expected_status': 400
        }
    ]
    
    all_passed = True
    for test_case in test_cases:
        try:
            response = requests.post(
                'http://localhost:5000/api/auth/login',
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == test_case['expected_status']:
                print(f"  ✅ {test_case['name']} - Correctly rejected")
            else:
                print(f"  ❌ {test_case['name']} - Expected {test_case['expected_status']}, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"  ❌ {test_case['name']} - Error: {str(e)}")
            all_passed = False
    
    return all_passed

def test_session_management():
    """Test session management and token handling"""
    print("\n🔍 Testing Session Management")
    print("=" * 40)
    
    try:
        # Login and get token
        login_data = {
            'username': 'testuser',
            'password': 'Test@123'
        }
        
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            
            if token:
                print("✅ Access token received")
                
                # Test profile access with token
                profile_response = requests.get(
                    'http://localhost:5000/api/auth/profile',
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("✅ Profile access with token successful")
                    print(f"  - User: {profile_data.get('username')}")
                    print(f"  - Email: {profile_data.get('email')}")
                    return True
                else:
                    print(f"❌ Profile access failed: {profile_response.status_code}")
                    return False
            else:
                print("❌ No access token received")
                return False
        else:
            print("❌ Login failed, cannot test session management")
            return False
            
    except Exception as e:
        print(f"❌ Error testing session management: {str(e)}")
        return False

def test_registration_link():
    """Test the registration page link"""
    print("\n🔍 Testing Registration Link")
    print("=" * 40)
    
    try:
        response = requests.get('http://localhost:5000/register')
        
        if response.status_code == 200:
            print("✅ Registration page loads successfully")
            return True
        else:
            print(f"❌ Registration page failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing registration link: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Final Login System Test Suite")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Login Page Elements", test_login_page_elements),
        ("Login Form Submission", test_login_form_submission),
        ("Invalid Login Scenarios", test_invalid_login_scenarios),
        ("Session Management", test_session_management),
        ("Registration Link", test_registration_link),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 FINAL TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Login system is working correctly.")
        print("\n✅ The login page has been successfully corrected and is fully functional!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the issues above.")
    
    print("\n" + "=" * 50)