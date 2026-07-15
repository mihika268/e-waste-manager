#!/usr/bin/env python3
"""
Test script to verify user and test login after verification
"""

import requests
import json
import sqlite3
import os

def check_user_verification():
    """Check if test user is verified"""
    try:
        # Connect to the database
        db_path = os.path.join('backend', 'instance', 'ewaste.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check user verification status
        cursor.execute("SELECT username, email, is_verified, is_active FROM user WHERE username = ?", ('testuser',))
        user = cursor.fetchone()
        
        if user:
            username, email, is_verified, is_active = user
            print(f"User found:")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            print(f"  Verified: {'✅' if is_verified else '❌'}")
            print(f"  Active: {'✅' if is_active else '❌'}")
            
            conn.close()
            return is_verified == 1
        else:
            print("❌ Test user not found in database")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error checking user verification: {str(e)}")
        return False

def verify_user_manually():
    """Manually verify the test user"""
    try:
        # Connect to the database
        db_path = os.path.join('backend', 'instance', 'ewaste.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update user to be verified
        cursor.execute("UPDATE user SET is_verified = 1 WHERE username = ?", ('testuser',))
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT is_verified FROM user WHERE username = ?", ('testuser',))
        is_verified = cursor.fetchone()[0]
        
        conn.close()
        
        if is_verified == 1:
            print("✅ User manually verified successfully")
            return True
        else:
            print("❌ Failed to verify user")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying user: {str(e)}")
        return False

def test_login_after_verification():
    """Test login after user verification"""
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
        
        print(f"Login after verification - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful after verification!")
            print(f"  - Access token received: {result.get('access_token') is not None}")
            print(f"  - User: {result.get('user', {}).get('username')}")
            return True
        else:
            result = response.json()
            print(f"❌ Login still failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login after verification: {str(e)}")
        return False

def test_with_new_user():
    """Create a new user using the OTP flow"""
    try:
        # Step 1: Send OTP
        email = "testuser2@example.com"
        
        print(f"\n📧 Sending OTP to {email}...")
        otp_response = requests.post(
            'http://localhost:5000/api/auth/send-otp',
            json={'email': email},
            headers={'Content-Type': 'application/json'}
        )
        
        if otp_response.status_code != 200:
            print(f"❌ Failed to send OTP: {otp_response.json().get('error')}")
            return False
            
        otp_data = otp_response.json()
        print(f"✅ OTP sent successfully")
        
        # Use the OTP from response (for development)
        otp_code = otp_data.get('otp_code', '123456')  # Fallback for testing
        
        # Step 2: Register with OTP
        register_data = {
            'username': 'testuser2',
            'password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'User2',
            'email': email,
            'phone': '1234567890',
            'otp_code': otp_code
        }
        
        print(f"\n📝 Registering user with OTP...")
        register_response = requests.post(
            'http://localhost:5000/api/auth/register-with-otp',
            json=register_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if register_response.status_code == 201:
            result = register_response.json()
            print("✅ User registered successfully with OTP!")
            print(f"  - Access token: {result.get('access_token') is not None}")
            print(f"  - User: {result.get('user', {}).get('username')}")
            return True
        else:
            print(f"❌ Registration failed: {register_response.json().get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error with OTP flow: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Verifying User and Testing Login")
    print("=" * 40)
    
    # Check current user verification status
    is_verified = check_user_verification()
    
    if not is_verified:
        # Try to verify manually
        print("\n🔧 Attempting to verify user manually...")
        verified = verify_user_manually()
        
        if verified:
            # Test login after verification
            print("\n🔑 Testing login after verification...")
            login_success = test_login_after_verification()
    else:
        print("\n🔑 User is already verified, testing login...")
        login_success = test_login_after_verification()
    
    # Test with new user using OTP flow
    print("\n🔄 Testing with new user using OTP flow...")
    otp_success = test_with_new_user()
    
    print("\n" + "=" * 40)
    print("📋 Final Results:")
    print(f"User Verification: {'✅' if is_verified else '❌'}")
    if not is_verified:
        print(f"Manual Verification: {'✅' if 'verified' in locals() and verified else '❌'}")
    print(f"Login After Verification: {'✅' if 'login_success' in locals() and login_success else '❌'}")
    print(f"OTP Flow: {'✅' if otp_success else '❌'}")
    
    if (is_verified or ('verified' in locals() and verified)) and ('login_success' in locals() and login_success) and otp_success:
        print("\n🎉 All login systems are working correctly!")
    else:
        print("\n⚠️  Some issues remain. Check the details above.")