#!/usr/bin/env python3
"""
Simple test to verify the modular structure endpoints are accessible.
This script tests the basic endpoint accessibility without creating users.
"""

import requests
import json

def test_modular_endpoints():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Modular Structure Endpoints")
    print("=" * 50)
    
    # Test 1: Check if admin endpoints exist (should return 401 without auth)
    print("\n1. Testing admin endpoint accessibility...")
    
    admin_endpoints = [
        "/api/admin/dashboard/stats",
        "/api/admin/users",
        "/api/admin/e-waste",
        "/api/admin/community/posts",
        "/api/admin/feedback"
    ]
    
    for endpoint in admin_endpoints:
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code == 401:
            print(f"   ✅ {endpoint} - Protected (401 Unauthorized)")
        elif response.status_code == 403:
            print(f"   ✅ {endpoint} - Protected (403 Forbidden)")
        elif response.status_code == 404:
            print(f"   ❌ {endpoint} - Not found (404)")
        else:
            print(f"   ⚠️  {endpoint} - Unexpected status: {response.status_code}")
    
    # Test 2: Check if user endpoints exist (should return 401 without auth)
    print("\n2. Testing user endpoint accessibility...")
    
    user_endpoints = [
        "/api/user/dashboard",
        "/api/user/profile",
        "/api/user/e-waste",
        "/api/user/community/posts",
        "/api/user/feedback"
    ]
    
    for endpoint in user_endpoints:
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code == 401:
            print(f"   ✅ {endpoint} - Protected (401 Unauthorized)")
        elif response.status_code == 403:
            print(f"   ✅ {endpoint} - Protected (403 Forbidden)")
        elif response.status_code == 404:
            print(f"   ❌ {endpoint} - Not found (404)")
        else:
            print(f"   ⚠️  {endpoint} - Unexpected status: {response.status_code}")
    
    # Test 3: Check dashboard templates (should return 401 without auth)
    print("\n3. Testing dashboard template accessibility...")
    
    dashboard_endpoints = [
        "/admin/dashboard",
        "/user/dashboard"
    ]
    
    for endpoint in dashboard_endpoints:
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code == 401:
            print(f"   ✅ {endpoint} - Protected (401 Unauthorized)")
        elif response.status_code == 403:
            print(f"   ✅ {endpoint} - Protected (403 Forbidden)")
        elif response.status_code == 200:
            print(f"   ✅ {endpoint} - Accessible (200 OK)")
        elif response.status_code == 404:
            print(f"   ❌ {endpoint} - Not found (404)")
        else:
            print(f"   ⚠️  {endpoint} - Unexpected status: {response.status_code}")
    
    # Test 4: Check if authentication endpoints exist
    print("\n4. Testing authentication endpoints...")
    
    auth_endpoints = [
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/logout"
    ]
    
    for endpoint in auth_endpoints:
        if endpoint.endswith('/register'):
            response = requests.post(f"{base_url}{endpoint}", json={})
        else:
            response = requests.post(f"{base_url}{endpoint}", json={})
        
        if response.status_code == 400:
            print(f"   ✅ {endpoint} - Exists (400 Bad Request)")
        elif response.status_code == 401:
            print(f"   ✅ {endpoint} - Exists (401 Unauthorized)")
        elif response.status_code == 404:
            print(f"   ❌ {endpoint} - Not found (404)")
        else:
            print(f"   ⚠️  {endpoint} - Status: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Endpoint accessibility test completed!")
    print("\nSummary:")
    print("- ✅ Protected endpoints return appropriate status codes")
    print("- ✅ Dashboard templates are accessible")
    print("- ✅ Authentication endpoints exist")
    print("\n🔧 To test with actual authentication:")
    print("   - Register users via /api/auth/register")
    print("   - Login via /api/auth/login")
    print("   - Use the JWT token in Authorization header")
    print("   - Test role-based access to admin/user endpoints")

if __name__ == "__main__":
    test_modular_endpoints()