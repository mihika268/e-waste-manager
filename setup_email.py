#!/usr/bin/env python3
"""
Email Setup Script for E-Waste Management System

This script helps you configure email settings for sending OTP codes.

Usage:
    python setup_email.py

It will:
1. Create a .env file in the backend directory
2. Guide you through Gmail app password setup
3. Save your email configuration securely
"""

import os
import sys

def print_banner():
    """Print a banner for the email setup"""
    print("=" * 60)
    print("🌱 E-Waste Management System - Email Configuration")
    print("=" * 60)
    print()

def print_instructions():
    """Print Gmail setup instructions"""
    print("📧 Gmail Setup Instructions:")
    print("-" * 60)
    print()
    print("To use Gmail for sending OTP emails, you need to:")
    print()
    print("1. Enable 2-Factor Authentication on your Google Account")
    print("   - Go to: https://myaccount.google.com/security")
    print("   - Turn on '2-Step Verification'")
    print()
    print("2. Generate an App Password")
    print("   - Go to: https://myaccount.google.com/apppasswords")
    print("   - Select 'Mail' as the app")
    print("   - Select 'Windows Computer' as the device")
    print("   - Click 'Generate'")
    print("   - Copy the 16-character password (it looks like: xxxx xxxx xxxx xxxx)")
    print()
    print("-" * 60)
    print()

def collect_email_info():
    """Collect email configuration from user"""
    print("📝 Email Configuration:")
    print()
    
    email = input("Enter your Gmail address: ").strip()
    
    if not email or '@' not in email:
        print("❌ Invalid email address!")
        return None, None
    
    password = input("Enter your Gmail App Password (16 characters): ").strip().replace(' ', '')
    
    if not password or len(password) < 16:
        print("❌ App Password should be at least 16 characters!")
        return None, None
    
    return email, password

def create_env_file(email, password):
    """Create .env file with email configuration"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    env_file = os.path.join(backend_dir, '.env')
    
    # Check if .env already exists
    if os.path.exists(env_file):
        response = input(f"\n⚠️  .env file already exists. Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Cancelled. Exiting.")
            return False
    
    # Create .env content
    env_content = f"""# Flask Configuration
SECRET_KEY=ewaste-management-secret-key-2024-dev
JWT_SECRET_KEY=jwt-secret-string-development-key

# Database Configuration (Optional - will use default if not set)
# DATABASE_URL=sqlite:///ewaste.db

# Email Configuration (for OTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME={email}
MAIL_PASSWORD={password}
MAIL_DEFAULT_SENDER={email}

# OTP Configuration
OTP_EXPIRY_MINUTES=10
OTP_LENGTH=6

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print()
        print("✅ Email configuration saved successfully!")
        print(f"📁 Config file: {env_file}")
        print()
        print("🔄 Next steps:")
        print("   1. Restart the Flask server (Ctrl+C, then run: python start.py)")
        print("   2. Try registering a new account")
        print("   3. Check your email for OTP code")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {str(e)}")
        return False

def main():
    """Main function"""
    print_banner()
    print_instructions()
    
    # Ask if user wants to proceed
    proceed = input("Do you want to proceed with email setup? (y/n): ").strip().lower()
    if proceed != 'y':
        print("❌ Setup cancelled.")
        return
    
    print()
    email, password = collect_email_info()
    
    if email and password:
        create_env_file(email, password)
    else:
        print("❌ Setup failed. Please try again.")
        sys.exit(1)

if __name__ == '__main__':
    main()



