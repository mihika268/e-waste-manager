from run import app
from app import db
from app.models.user import User

with app.app_context():
    users = User.query.all()
    print(f'Total users: {len(users)}')
    for user in users:
        print(f'User: {user.username}, Email: {user.email}, Active: {user.is_active}, Verified: {user.is_verified}, Role: {user.role}')