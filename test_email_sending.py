#!/usr/bin/env python3
"""
Test script to verify email sending functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.app.utils.email_service import EmailService

def test_email_sending():
    """Test sending an email with OTP"""
    app = create_app()
    
    with app.app_context():
        email_service = EmailService()
        
        # Test email configuration
        print("Testing email configuration...")
        print(f"SMTP Server: {app.config.get('MAIL_SERVER')}")
        print(f"SMTP Port: {app.config.get('MAIL_PORT')}")
        print(f"Use TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"Username: {app.config.get('MAIL_USERNAME')}")
        print(f"Default Sender: {app.config.get('MAIL_DEFAULT_SENDER')}")
        
        # Test sending OTP email
        test_email = "test@example.com"
        test_otp = "123456"
        
        print(f"\nSending test OTP email to {test_email}...")
        
        try:
            success = email_service.send_otp_email(test_email, test_otp, 'registration')
            
            if success:
                print("✅ OTP email sent successfully!")
                return True
            else:
                print("❌ Failed to send OTP email")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False

def test_email_credentials():
    """Test if email credentials are properly configured"""
    app = create_app()
    
    with app.app_context():
        email_service = EmailService()
        
        print("\nTesting email credentials...")
        
        # Check if credentials are available
        if not email_service.username or not email_service.password:
            print("⚠️  Email credentials not configured. Emails will be logged to console.")
            return False
        else:
            print("✅ Email credentials are configured")
            return True

if __name__ == "__main__":
    print("🔍 Testing Email Service")
    print("=" * 40)
    
    # Test credentials
    credentials_ok = test_email_credentials()
    
    # Test email sending
    email_sent = test_email_sending()
    
    print("\n" + "=" * 40)
    print("📋 Test Results:")
    print(f"Credentials Configured: {'✅' if credentials_ok else '❌'}")
    print(f"Email Sent Successfully: {'✅' if email_sent else '❌'}")
    
    if not credentials_ok:
        print("\n💡 Tip: Check your .env file for email configuration.")
        print("For Gmail, you need to:")
        print("1. Enable 2FA on your Google account")
        print("2. Generate an app password at: https://myaccount.google.com/apppasswords")
        print("3. Use the 16-character app password in your MAIL_PASSWORD config")