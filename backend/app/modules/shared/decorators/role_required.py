from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.user import User

def role_required(required_roles):
    """
    Decorator to require specific roles for accessing routes
    required_roles can be a string or list of strings
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            # Get current user from JWT token
            current_user_id = get_jwt_identity()
            
            # Find user in database
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Convert single role to list for consistent handling
            if isinstance(required_roles, str):
                roles = [required_roles]
            else:
                roles = required_roles
            
            # Check if user has required role
            if user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Add user to kwargs so the route can access it
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Shortcut decorator for admin-only routes"""
    return role_required('admin')(f)

def user_required(f):
    """Shortcut decorator for user-only routes"""
    return role_required('user')(f)

def collector_required(f):
    """Shortcut decorator for collector-only routes"""
    return role_required('collector')(f)

def admin_or_collector_required(f):
    """Shortcut decorator for admin or collector routes"""
    return role_required(['admin', 'collector'])(f)