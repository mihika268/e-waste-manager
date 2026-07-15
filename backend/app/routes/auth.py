from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.otp import OTP
from app.utils.otp_service import OTPService
from app.utils.email_service import EmailService
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP for email verification"""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists (for registration flow)
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Generate and send OTP
        otp_service = OTPService()
        result = otp_service.generate_and_send_otp(email, 'registration')
        
        if result['success']:
            response_data = {
                'message': 'OTP sent successfully',
                'expires_at': result['expires_at']
            }
            # Include OTP code in response for development purposes
            if 'otp_code' in result:
                response_data['otp_code'] = result['otp_code']
            return jsonify(response_data), 200
        else:
            return jsonify({'error': result['message']}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint - disabled, use register-with-otp instead"""
    return jsonify({'error': 'Please use the registration form with email verification'}), 400

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP for email verification"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('otp_code'):
            return jsonify({'error': 'Email and OTP code are required'}), 400
        
        email = data['email'].lower().strip()
        otp_code = data['otp_code'].strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Verify OTP
        otp_service = OTPService()
        result = otp_service.verify_otp(email, otp_code, 'registration')
        
        if result['success']:
            return jsonify({
                'message': 'OTP verified successfully',
                'verified': True
            }), 200
        else:
            return jsonify({
                'error': result['message'],
                'verified': False
            }), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP for email verification"""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Resend OTP
        otp_service = OTPService()
        result = otp_service.resend_otp(email, 'registration')
        
        if result['success']:
            response_data = {
                'message': 'OTP resent successfully',
                'expires_at': result['expires_at']
            }
            # Include OTP code in response for development purposes
            if 'otp_code' in result:
                response_data['otp_code'] = result['otp_code']
            return jsonify(response_data), 200
        else:
            return jsonify({'error': result['message']}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        if not user.is_verified:
            return jsonify({'error': 'Email not verified. Please verify your email before logging in.'}), 401
        
        # Create access token
        access_token = user.get_token()
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'address']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-otp-only', methods=['POST'])
def verify_otp_only():
    """Verify OTP only without completing registration"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('otp_code'):
            return jsonify({'error': 'Email and OTP code are required'}), 400
        
        email = data['email'].lower().strip()
        otp_code = data['otp_code'].strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Verify OTP
        otp_service = OTPService()
        result = otp_service.verify_otp(email, otp_code, 'registration')
        
        if result['success']:
            return jsonify({
                'message': 'OTP verified successfully',
                'verified': True,
                'email': email
            }), 200
        else:
            return jsonify({
                'error': result['message'],
                'verified': False
            }), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register-with-otp', methods=['POST'])
def register_with_otp():
    """Complete user registration after OTP verification"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'otp_code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        otp_code = data['otp_code'].strip()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Verify OTP first
        otp_service = OTPService()
        otp_result = otp_service.verify_otp(email, otp_code, 'registration')
        
        if not otp_result['success']:
            return jsonify({'error': 'Invalid or expired OTP code'}), 400
        
        # Create new user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_verified=True,  # Mark as verified since OTP was successful
            is_active=True
        )
        user.set_password(password)
        
        # Generate username from email
        username_base = email.split('@')[0]
        username = username_base
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{username_base}{counter}"
            counter += 1
        user.username = username
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        try:
            email_service = EmailService()
            email_service.send_welcome_email(user.email, user.first_name)
        except Exception as email_error:
            print(f"Failed to send welcome email: {email_error}")
        
        # Create access token
        access_token = user.get_token()
        
        return jsonify({
            'message': 'Registration completed successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(data['new_password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
