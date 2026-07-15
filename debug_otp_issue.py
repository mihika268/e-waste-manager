#!/usr/bin/env python3
"""
Debug and fix OTP registration issues
"""

import requests
import json
import sqlite3
import os
from datetime import datetime, timedelta

def check_otp_status():
    """Check current OTP status in database"""
    print("🔍 Checking OTP Status")
    print("=" * 40)
    
    try:
        db_path = os.path.join('backend', 'instance', 'ewaste.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check OTP table structure
        cursor.execute("PRAGMA table_info(otp)")
        columns = cursor.fetchall()
        print("📋 OTP Table Structure:")
        for col in columns:
            print(f"  - {col[1]}: {col[2]}")
        
        # Check recent OTPs
        print(f"\n📊 Recent OTPs (last 24 hours):")
        cursor.execute("""
            SELECT id, email, otp_code, purpose, is_used, expires_at, created_at 
            FROM otp 
            WHERE created_at > datetime('now', '-1 day')
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        recent_otps = cursor.fetchall()
        if recent_otps:
            for otp in recent_otps:
                print(f"  - ID: {otp[0]}, Email: {otp[1]}, Code: {otp[2]}, Purpose: {otp[3]}")
                print(f"    Used: {'Yes' if otp[4] else 'No'}, Expires: {otp[5]}, Created: {otp[6]}")
        else:
            print("  No recent OTPs found")
        
        # Check expired OTPs
        print(f"\n🗑️  Expired OTPs:")
        cursor.execute("""
            SELECT COUNT(*) FROM otp 
            WHERE expires_at < datetime('now') AND is_used = 0
        """)
        expired_count = cursor.fetchone()[0]
        print(f"  {expired_count} expired OTPs found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking OTP status: {str(e)}")
        return False

def test_otp_flow():
    """Test the complete OTP flow step by step"""
    print("\n🧪 Testing Complete OTP Flow")
    print("=" * 40)
    
    test_email = "testuser@example.com"
    
    try:
        # Step 1: Send OTP
        print(f"📧 Sending OTP to {test_email}...")
        send_response = requests.post(
            'http://localhost:5000/api/auth/send-otp',
            json={'email': test_email},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Send OTP Response: {send_response.status_code}")
        send_data = send_response.json()
        print(f"Send OTP Data: {json.dumps(send_data, indent=2)}")
        
        if send_response.status_code != 200 or not send_data.get('success'):
            print(f"❌ Failed to send OTP: {send_data.get('error', 'Unknown error')}")
            return False
        
        # Extract OTP code from response (for development)
        otp_code = send_data.get('otp_code')
        if not otp_code:
            print("❌ No OTP code received in response")
            return False
        
        print(f"✅ OTP sent successfully: {otp_code}")
        
        # Step 2: Verify OTP
        print(f"\n🔐 Verifying OTP: {otp_code}")
        verify_response = requests.post(
            'http://localhost:5000/api/auth/verify-otp',
            json={
                'email': test_email,
                'otp_code': otp_code
            },
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Verify OTP Response: {verify_response.status_code}")
        verify_data = verify_response.json()
        print(f"Verify OTP Data: {json.dumps(verify_data, indent=2)}")
        
        if verify_response.status_code != 200 or not verify_data.get('success'):
            print(f"❌ OTP verification failed: {verify_data.get('error', 'Unknown error')}")
            return False
        
        print("✅ OTP verified successfully!")
        
        # Step 3: Register with verified OTP
        print(f"\n📝 Registering user...")
        register_response = requests.post(
            'http://localhost:5000/api/auth/register-with-otp',
            json={
                'username': 'testuser_new',
                'password': 'Test@123',
                'first_name': 'Test',
                'last_name': 'User',
                'email': test_email,
                'phone': '1234567890',
                'otp_code': otp_code
            },
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Register Response: {register_response.status_code}")
        register_data = register_response.json()
        print(f"Register Data: {json.dumps(register_data, indent=2)}")
        
        if register_response.status_code != 201:
            print(f"❌ Registration failed: {register_data.get('error', 'Unknown error')}")
            return False
        
        print("✅ Registration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing OTP flow: {str(e)}")
        return False

def check_email_configuration():
    """Check if email service is properly configured"""
    print("\n📧 Checking Email Configuration")
    print("=" * 40)
    
    try:
        # Check .env file
        env_path = os.path.join('backend', '.env')
        if not os.path.exists(env_path):
            print("❌ .env file not found")
            return False
        
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        # Check for required email settings
        required_vars = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)
            else:
                # Extract value (safely)
                for line in env_content.split('\n'):
                    if line.startswith(f'{var}='):
                        value = line.split('=', 1)[1]
                        if var == 'MAIL_PASSWORD':
                            print(f"{var}: {'*' * len(value)} (hidden)")
                        else:
                            print(f"{var}: {value}")
        
        if missing_vars:
            print(f"❌ Missing email configuration: {', '.join(missing_vars)}")
            return False
        
        print("✅ Email configuration found")
        return True
        
    except Exception as e:
        print(f"❌ Error checking email configuration: {str(e)}")
        return False

def test_with_manual_otp():
    """Test registration with manually created OTP"""
    print("\n🔧 Testing with Manual OTP Creation")
    print("=" * 40)
    
    try:
        db_path = os.path.join('backend', 'instance', 'ewaste.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a manual OTP
        test_email = "manual_test@example.com"
        manual_otp = "123456"
        expires_at = datetime.now() + timedelta(minutes=10)
        
        # Insert manual OTP
        cursor.execute("""
            INSERT INTO otp (email, otp_code, purpose, is_used, expires_at, created_at)
            VALUES (?, ?, 'registration', 0, ?, datetime('now'))
        """, (test_email, manual_otp, expires_at))
        
        conn.commit()
        print(f"✅ Manual OTP created: {manual_otp} for {test_email}")
        
        # Test verification
        print(f"\n🔐 Testing manual OTP verification...")
        verify_response = requests.post(
            'http://localhost:5000/api/auth/verify-otp',
            json={
                'email': test_email,
                'otp_code': manual_otp
            },
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Manual OTP Verify Response: {verify_response.status_code}")
        verify_data = verify_response.json()
        print(f"Manual OTP Verify Data: {json.dumps(verify_data, indent=2)}")
        
        if verify_response.status_code == 200 and verify_data.get('success'):
            print("✅ Manual OTP verification successful!")
            
            # Test registration with manual OTP
            print(f"\n📝 Testing registration with manual OTP...")
            register_response = requests.post(
                'http://localhost:5000/api/auth/register-with-otp',
                json={
                    'username': 'manual_test_user',
                    'password': 'Test@123',
                    'first_name': 'Manual',
                    'last_name': 'Test',
                    'email': test_email,
                    'phone': '1234567890',
                    'otp_code': manual_otp
                },
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Manual Register Response: {register_response.status_code}")
            register_data = register_response.json()
            print(f"Manual Register Data: {json.dumps(register_data, indent=2)}")
            
            if register_response.status_code == 201:
                print("✅ Manual registration successful!")
                return True
            else:
                print(f"❌ Manual registration failed: {register_data.get('error')}")
                return False
        else:
            print(f"❌ Manual OTP verification failed: {verify_data.get('error')}")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error with manual OTP test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 OTP Registration Issue Debug Tool")
    print("=" * 50)
    
    # Run all diagnostic tests
    tests = [
        ("Email Configuration", check_email_configuration),
        ("OTP Status Check", check_otp_status),
        ("Complete OTP Flow Test", test_otp_flow),
        ("Manual OTP Test", test_with_manual_otp),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        result = test_func()
        results.append((test_name, result))
        print(f"{'='*50}")
    
    # Summary
    print("\n📋 DIAGNOSTIC RESULTS")
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
        print("\n🎉 All OTP systems are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the details above.")
        print("\n💡 Common solutions:")
        print("1. Ensure Gmail App Password is set correctly in backend/.env")
        print("2. Check that 2FA is enabled on your Gmail account")
        print("3. Verify email settings in backend/.env")
        print("4. Check server logs for detailed error messages")