from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

def require_auth(f):
    """Basic authentication middleware"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    
    return decorated_function

def check_email_verified(f):
    """Middleware to check if user's email is verified"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = kwargs.get('current_user')
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        if not current_user.is_verified:
            return jsonify({'error': 'Email not verified'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function