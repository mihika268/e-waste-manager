#!/usr/bin/env python3
"""
Test script to demonstrate OTP functionality with console logging
This will show you the OTP codes in the console while email is being configured
"""

import requests
import json
import time

def test_otp_with_console_logging():
    """Test OTP registration flow with console logging"""
    base_url = "http://localhost:5000/api/auth"
    
    print("🧪 Testing OTP Registration Flow (Console Logging Mode)")
    print("=" * 60)
    
    # Test email
    test_email = "test@example.com"
    test_password = "TestPassword123"
    
    try:
        # Step 1: Send OTP (will be logged to console)
        print(f"\n1️⃣ Requesting OTP for {test_email}...")
        response = requests.post(
            f"{base_url}/send-otp",
            json={"email": test_email}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OTP generated successfully")
            print(f"📧 Response: {data}")
            
            # The OTP code will be in the response for development
            if 'otp_code' in data:
                otp_code = data['otp_code']
                print(f"🔑 OTP Code: {otp_code}")
                print("⚠️  Note: Check the backend console logs for the actual OTP")
            else:
                print("❌ OTP code not found in response")
                return False
        else:
            print(f"❌ Failed: {response.text}")
            return False
        
        # Step 2: Verify OTP
        print(f"\n2️⃣ Verifying OTP {otp_code}...")
        response = requests.post(
            f"{base_url}/verify-otp",
            json={"email": test_email, "otp_code": otp_code}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ OTP verified successfully")
        else:
            print(f"❌ OTP verification failed: {response.text}")
            return False
        
        # Step 3: Complete registration
        print(f"\n3️⃣ Completing registration...")
        register_data = {
            "email": test_email,
            "password": test_password,
            "first_name": "Test",
            "last_name": "User",
            "otp_code": otp_code
        }
        
        response = requests.post(
            f"{base_url}/register-with-otp",
            json=register_data
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Registration completed!")
            print(f"🎉 User ID: {data['user']['id']}")
            print(f"🔑 Access Token: {data['access_token'][:20]}...")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_console_otp_example():
    """Show what the console OTP logging looks like"""
    print("\n📋 Example of Console OTP Logging")
    print("=" * 40)
    print("When you register, you'll see something like:")
    print("""
Failed to send OTP email to test@example.com: (535, b'5.7.8 Username and Password not accepted')
OTP generated but email failed for test@example.com
OTP for test@example.com: 123456  ← This is your OTP code!
""")
    print("Use the 6-digit code shown in the console log!")

if __name__ == "__main__":
    print("🚀 OTP Registration Test (Console Mode)")
    print("This test shows how to use OTP codes from console logs")
    print("while email configuration is being fixed.\n")
    
    show_console_otp_example()
    
    print("\n" + "=" * 60)
    success = test_otp_with_console_logging()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("The OTP system works - just check console for codes.")
    else:
        print("\n❌ Test failed. Check the error messages above.")
    
    print("\n💡 To fix email delivery:")
    print("1. Follow the guide in: email_fix_guide.md")
    print("2. Generate Gmail App Password")
    print("3. Update your .env file")
    print("4. Restart the server")