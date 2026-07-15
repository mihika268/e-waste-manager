#!/usr/bin/env python3
"""
Test script to verify all dashboard features are working correctly
Run this after starting the Flask application to test functionality
"""

import requests
import json
import sys
import os

BASE_URL = "http://localhost:5000"

def test_login():
    """Test user authentication"""
    print("🔐 Testing login...")
    
    # Try to login with sample user
    login_data = {
        "username": "john_doe",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print("✅ Login successful")
        return token
    else:
        print("❌ Login failed - make sure sample data is initialized")
        print("Run: cd backend && python init_sample_data.py")
        return None

def test_items_api(token):
    """Test items management API"""
    print("\n📱 Testing Items API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get items
    response = requests.get(f"{BASE_URL}/api/ewaste/items", headers=headers)
    if response.status_code == 200:
        items = response.json().get('items', [])
        print(f"✅ Items API working - found {len(items)} items")
        return len(items) > 0
    else:
        print("❌ Items API failed")
        return False

def test_collections_api(token):
    """Test collections API"""
    print("\n🚛 Testing Collections API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get collections
    response = requests.get(f"{BASE_URL}/api/ewaste/collections", headers=headers)
    if response.status_code == 200:
        collections = response.json().get('collections', [])
        print(f"✅ Collections API working - found {len(collections)} collections")
        return True
    else:
        print("❌ Collections API failed")
        return False

def test_profile_api(token):
    """Test profile API"""
    print("\n👤 Testing Profile API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get profile
    response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
    if response.status_code == 200:
        user = response.json().get('user', {})
        print(f"✅ Profile API working - user: {user.get('username')}")
        return True
    else:
        print("❌ Profile API failed")
        return False

def test_scanner_api(token):
    """Test AI scanner API endpoints"""
    print("\n🤖 Testing AI Scanner API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test carbon footprint endpoint
    response = requests.get(f"{BASE_URL}/api/scanner/carbon-footprint", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ Carbon footprint API working")
        return True
    else:
        print("❌ Scanner API failed")
        return False

def test_community_api(token):
    """Test community API"""
    print("\n👥 Testing Community API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get posts
    response = requests.get(f"{BASE_URL}/api/community/posts", headers=headers)
    if response.status_code == 200:
        posts = response.json().get('posts', [])
        print(f"✅ Community API working - found {len(posts)} posts")
        return True
    else:
        print("❌ Community API failed")
        return False

def test_analytics_api(token):
    """Test analytics API"""
    print("\n📊 Testing Analytics API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get dashboard stats
    response = requests.get(f"{BASE_URL}/api/analytics/dashboard", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ Analytics API working")
        return True
    else:
        print("❌ Analytics API failed")
        return False

def test_feedback_api(token):
    """Test feedback/complaints API"""
    print("\n📝 Testing Feedback API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get complaint types
    response = requests.get(f"{BASE_URL}/api/feedback/complaint-types", headers=headers)
    if response.status_code == 200:
        types = response.json().get('complaint_types', [])
        print(f"✅ Feedback API working - {len(types)} complaint types available")
        return True
    else:
        print("❌ Feedback API failed")
        return False

def test_pages():
    """Test that all pages are accessible"""
    print("\n🌐 Testing Page Accessibility...")
    
    pages = [
        "/",
        "/dashboard", 
        "/items",
        "/collections", 
        "/profile",
        "/community",
        "/analytics"
    ]
    
    success_count = 0
    for page in pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            if response.status_code == 200:
                print(f"✅ {page} - accessible")
                success_count += 1
            else:
                print(f"❌ {page} - failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {page} - error: {e}")
    
    return success_count == len(pages)

def main():
    """Run all tests"""
    print("🧪 E-Waste Management System - Feature Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print("❌ Server not accessible. Make sure Flask app is running on http://localhost:5000")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure to start the Flask application first:")
        print("cd backend && python run.py")
        sys.exit(1)
    
    print("✅ Server is running")
    
    # Test pages
    pages_ok = test_pages()
    
    # Test authentication
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Test all APIs
    tests = [
        test_items_api(token),
        test_collections_api(token), 
        test_profile_api(token),
        test_scanner_api(token),
        test_community_api(token),
        test_analytics_api(token),
        test_feedback_api(token)
    ]
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(tests) + (1 if pages_ok else 0)
    total = len(tests) + 1
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n✨ Your E-Waste Management System is fully functional!")
        print("\n🚀 You can now use all dashboard features:")
        print("   • View All Items (/items)")
        print("   • Schedule Collection (/collections)")  
        print("   • Edit Profile (/profile)")
        print("   • AI Waste Scanner (dashboard modal)")
        print("   • Report Issue (dashboard modal)")
        print("   • Community Feed (/community)")
        print("   • Analytics Dashboard (/analytics)")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\nSome features may not work correctly.")
        print("Check the error messages above for details.")
    
    print(f"\n🌐 Access your app at: {BASE_URL}")

if __name__ == "__main__":
    main()
