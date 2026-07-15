#!/usr/bin/env python3
"""
Fix user verification status for existing users
"""

from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Get all users
    users = User.query.all()
    
    for user in users:
        print(f"User: {user.username}, Verified: {user.is_verified}")
        if not user.is_verified:
            user.is_verified = True
            print(f"  -> Marked {user.username} as verified")
    
    db.session.commit()
    print("✅ All users are now verified!")