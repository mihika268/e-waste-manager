#!/usr/bin/env python3
"""
Check existing user passwords and create a working test user
"""

from run import app
from app import db, bcrypt
from app.models.user import User

def check_existing_users():
    """Check existing users and their status"""
    
    with app.app_context():
        users = User.query.all()
        print(f"Total users found: {len(users)}")
        print("\nUser Details:")
        print("-" * 80)
        
        for user in users[:5]:  # Check first 5 users
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Active: {user.is_active}")
            print(f"Verified: {user.is_verified}")
            print(f"Password Hash: {user.password_hash[:20]}..." if user.password_hash else "No password hash")
            
            # Test some common passwords
            test_passwords = ["testpassword123", "Test123456!", "password123", "password", "123456", "admin"]
            for pwd in test_passwords:
                if user.password_hash and bcrypt.check_password_hash(user.password_hash, pwd):
                    print(f"✅ Password found: {pwd}")
                    break
            else:
                print("❌ No matching password found in common list")
            
            print("-" * 80)

def create_test_user_with_known_password():
    """Create a test user with a known password"""
    
    with app.app_context():
        # Check if test user already exists
        test_email = "testlogin@example.com"
        existing_user = User.query.filter_by(email=test_email).first()
        
        if existing_user:
            print(f"Test user already exists: {existing_user.username}")
            # Update password to known one
            existing_user.set_password("testpass123")
            db.session.commit()
            print("Updated password to: testpass123")
            return existing_user
        else:
            # Create new test user
            test_user = User(
                username="testuser_login",
                email=test_email,
                first_name="Test",
                last_name="User",
                role="user",
                is_active=True,
                is_verified=True
            )
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()
            print(f"Created new test user: {test_user.username}")
            return test_user

if __name__ == "__main__":
    print("🔍 Checking Existing Users")
    print("=" * 50)
    
    check_existing_users()
    
    print("\n🔧 Creating Test User with Known Password")
    print("=" * 50)
    
    test_user = create_test_user_with_known_password()
    
    if test_user:
        print(f"\n🎉 Test user created/updated!")
        print(f"Username: {test_user.username}")
        print(f"Email: {test_user.email}")
        print(f"Password: testpass123")
        print(f"Role: {test_user.role}")
        print(f"Active: {test_user.is_active}")
        print(f"Verified: {test_user.is_verified}")
        
        print(f"\n🔧 You can now test login with:")
        print(f"   Username: {test_user.username}")
        print(f"   Password: testpass123")