#!/usr/bin/env python3
"""
Quick OTP Test - Shows OTP codes in console while email is being fixed
"""

import requests
import random
import string

def test_otp_console():
    """Test OTP generation and show console codes"""
    
    # Generate random email for testing
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f'test_{random_str}@example.com'
    
    print(f"🧪 Testing OTP with email: {test_email}")
    print("=" * 50)
    
    # Request OTP
    response = requests.post('http://localhost:5000/api/auth/send-otp', json={'email': test_email})
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ OTP Generated Successfully!")
        print(f"📧 Response: {data}")
        
        if 'otp_code' in data:
            otp_code = data['otp_code']
            print(f"\n🎉 YOUR OTP CODE: {otp_code}")
            print("=" * 50)
            print("✅ Copy this code and use it to complete registration!")
            print("📋 Code expires at:", data.get('expires_at', 'Unknown'))
            return otp_code, test_email
        else:
            print("❌ OTP code not found in response")
            return None, test_email
    else:
        print(f"❌ Error: {response.text}")
        return None, test_email

def complete_registration(email, otp_code):
    """Complete registration with the OTP code"""
    print(f"\n📝 Completing registration for {email}...")
    
    register_data = {
        "email": email,
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
        "otp_code": otp_code
    }
    
    response = requests.post('http://localhost:5000/api/auth/register-with-otp', json=register_data)
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Registration completed successfully!")
        print(f"🎉 User ID: {data['user']['id']}")
        print(f"🔑 Access Token: {data['access_token'][:20]}...")
        return True
    else:
        print(f"❌ Registration failed: {response.text}")
        return False

if __name__ == "__main__":
    print("🔑 Quick OTP Test - Console Mode")
    print("This test shows OTP codes directly in console")
    print("while email configuration is being fixed.\n")
    
    # Test OTP generation
    otp_code, email = test_otp_console()
    
    if otp_code:
        print(f"\n🚀 Ready to complete registration!")
        print(f"Email: {email}")
        print(f"OTP: {otp_code}")
        print(f"Password: TestPassword123")
        
        # Uncomment the line below to automatically complete registration
        # complete_registration(email, otp_code)
        
        print("\n💡 To complete registration:")
        print("1. Go to: http://localhost:5000/register")
        print(f"2. Use email: {email}")
        print(f"3. Use OTP: {otp_code}")
        print("4. Password: TestPassword123")
    else:
        print("❌ OTP generation failed!")
    
    print("\n📧 To fix email delivery:")
    print("1. Generate Gmail App Password")
    print("2. Update MAIL_PASSWORD in .env file")
    print("3. Restart the server")