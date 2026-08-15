from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.otp import OTP
from app.utils.otp_service import OTPService
from app.utils.email_service import EmailService

import re


# ============================================================
# BLUEPRINT
# ============================================================

auth_bp = Blueprint(
    'auth',
    __name__
)


# ============================================================
# VALIDATION
# ============================================================

def validate_email(email):

    pattern = (
        r'^[a-zA-Z0-9._%+-]+'
        r'@[a-zA-Z0-9.-]+'
        r'\.[a-zA-Z]{2,}$'
    )

    return (
        bool(email)
        and re.match(pattern, email) is not None
    )


def clean_identifier(value):

    if not value:
        return ''

    return str(value).strip()


# ============================================================
# CHECK USERNAME AVAILABILITY
# ============================================================

@auth_bp.route(
    '/check-username',
    methods=['POST']
)
def check_username():

    try:

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                'available': False,
                'message': 'Request data is required'
            }), 400

        username = clean_identifier(
            data.get('username')
        )

        email = clean_identifier(
            data.get('email')
        ).lower()

        if not username:
            return jsonify({
                'available': False,
                'message': ''
            }), 200

        if not re.fullmatch(
            r'[A-Za-z0-9_.-]{3,80}',
            username
        ):
            return jsonify({
                'available': False,
                'message': (
                    'Username must be 3-80 characters and '
                    'contain only letters, numbers, underscore, '
                    'dot or hyphen.'
                )
            }), 200

        existing_username = None

        for candidate in User.query.all():
            candidate_username = (
                candidate.username or ''
            ).strip().lower()

            if candidate_username == username.lower():
                existing_username = candidate
                break

        if not existing_username:
            return jsonify({
                'available': True,
                'message': 'Username is available'
            }), 200

        same_deactivated_account = (
            bool(email)
            and bool(existing_username.email)
            and existing_username.email.strip().lower() == email
            and not existing_username.is_active
        )

        if same_deactivated_account:
            return jsonify({
                'available': True,
                'message': 'Username is available'
            }), 200

        return jsonify({
            'available': False,
            'message': 'Username already taken'
        }), 200

    except Exception as e:

        print(
            f'Username availability error: {e}'
        )

        return jsonify({
            'available': False,
            'message': 'Unable to check username'
        }), 500


# ============================================================
# SEND REGISTRATION OTP
# ============================================================

@auth_bp.route(
    '/send-otp',
    methods=['POST']
)
def send_otp():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                'error':
                    'Request data is required'
            }), 400

        email = clean_identifier(
            data.get('email')
        ).lower()

        if not email:

            return jsonify({
                'error':
                    'Email is required'
            }), 400

        if not validate_email(email):

            return jsonify({
                'error':
                    'Invalid email format'
            }), 400

        # ----------------------------------------------------
        # CHECK EXISTING USER
        # ----------------------------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()

        # ----------------------------------------------------
        # ACTIVE ACCOUNT
        #
        # Active users cannot register again.
        # ----------------------------------------------------

        if (
            existing_user
            and existing_user.is_active
        ):

            return jsonify({
                'error':
                    'Email already registered'
            }), 400

        # ----------------------------------------------------
        # DEACTIVATED ACCOUNT
        #
        # A deactivated account is allowed to receive a
        # registration OTP so it can be reactivated.
        # ----------------------------------------------------

        otp_service = OTPService()

        result = otp_service.generate_and_send_otp(
            email,
            'registration'
        )

        if not result.get('success'):

            return jsonify({
                'error': result.get(
                    'message',
                    'Unable to send verification email'
                )
            }), 500

        response = {
            'message':
                'Verification email sent successfully',

            'expires_at':
                result.get('expires_at')
        }

        # ----------------------------------------------------
        # DEVELOPMENT FALLBACK
        # ----------------------------------------------------

        if result.get('otp_code'):

            response['otp_code'] = (
                result.get('otp_code')
            )

        return jsonify(
            response
        ), 200

    except Exception as e:

        print(
            f'Send OTP error: {e}'
        )

        return jsonify({
            'error':
                'Unable to send verification email'
        }), 500


# ============================================================
# VERIFY REGISTRATION OTP
# ============================================================

@auth_bp.route(
    '/verify-otp',
    methods=['POST']
)
def verify_otp():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                'error':
                    'Request data is required'
            }), 400

        email = clean_identifier(
            data.get('email')
        ).lower()

        otp_code = clean_identifier(
            data.get('otp_code')
        )

        if not email or not otp_code:

            return jsonify({
                'error':
                    'Email and OTP code are required'
            }), 400

        if not validate_email(email):

            return jsonify({
                'error':
                    'Invalid email format'
            }), 400

        if not re.fullmatch(
            r'\d{6}',
            otp_code
        ):

            return jsonify({
                'error':
                    'OTP must be a 6-digit code'
            }), 400

        # ----------------------------------------------------
        # IMPORTANT
        #
        # This only checks the OTP.
        # It does NOT consume it.
        #
        # register-with-otp consumes the OTP.
        # ----------------------------------------------------

        otp = OTP.query.filter(
            OTP.email == email,
            OTP.otp_code == otp_code,
            OTP.purpose == 'registration',
            OTP.is_used.is_(False),
            OTP.expires_at > db.func.now()
        ).first()

        if not otp:

            return jsonify({

                'error':
                    'Invalid or expired OTP',

                'verified':
                    False

            }), 400

        return jsonify({

            'message':
                'OTP verified successfully',

            'verified':
                True,

            'email':
                email

        }), 200

    except Exception as e:

        print(
            f'OTP verification error: {e}'
        )

        return jsonify({
            'error':
                'Unable to verify verification code'
        }), 500


# ============================================================
# VERIFY OTP ONLY
# ============================================================

@auth_bp.route(
    '/verify-otp-only',
    methods=['POST']
)
def verify_otp_only():

    return verify_otp()


# ============================================================
# RESEND REGISTRATION OTP
# ============================================================

@auth_bp.route(
    '/resend-otp',
    methods=['POST']
)
def resend_otp():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                'error':
                    'Request data is required'
            }), 400

        email = clean_identifier(
            data.get('email')
        ).lower()

        if not email:

            return jsonify({
                'error':
                    'Email is required'
            }), 400

        if not validate_email(email):

            return jsonify({
                'error':
                    'Invalid email format'
            }), 400

        # ----------------------------------------------------
        # ACTIVE USER CANNOT RESEND REGISTRATION OTP
        # ----------------------------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if (
            existing_user
            and existing_user.is_active
        ):

            return jsonify({
                'error':
                    'Email already registered'
            }), 400

        # ----------------------------------------------------
        # DEACTIVATED OR NEW USER
        #
        # Both are allowed to receive a registration OTP.
        # ----------------------------------------------------

        otp_service = OTPService()

        result = otp_service.resend_otp(
            email,
            'registration'
        )

        if not result.get('success'):

            return jsonify({
                'error': result.get(
                    'message',
                    'Unable to resend verification email'
                )
            }), 500

        response = {
            'message':
                'Verification email resent successfully',

            'expires_at':
                result.get('expires_at')
        }

        # ----------------------------------------------------
        # DEVELOPMENT FALLBACK
        # ----------------------------------------------------

        if result.get('otp_code'):

            response['otp_code'] = (
                result.get('otp_code')
            )

        return jsonify(
            response
        ), 200

    except Exception as e:

        print(
            f'Resend OTP error: {e}'
        )

        return jsonify({
            'error':
                'Unable to resend verification email'
        }), 500


# ============================================================
# FORGOT PASSWORD - SEND OTP
# ============================================================

@auth_bp.route(
    '/forgot-password',
    methods=['POST']
)
def forgot_password():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                'error':
                    'Request data is required'
            }), 400

        email = clean_identifier(
            data.get('email')
        ).lower()

        if not email:

            return jsonify({
                'error':
                    'Email is required'
            }), 400

        if not validate_email(email):

            return jsonify({
                'error':
                    'Invalid email format'
            }), 400

        # ----------------------------------------------------
        # FIND USER
        # ----------------------------------------------------

        user = User.query.filter_by(
            email=email
        ).first()

        # ----------------------------------------------------
        # SECURITY
        #
        # Do not reveal whether an email exists.
        # ----------------------------------------------------

        if not user:

            return jsonify({
                'message': (
                    'If an account exists for this email, '
                    'a password reset code has been sent.'
                )
            }), 200

        # ----------------------------------------------------
        # GENERATE PASSWORD RESET OTP
        # ----------------------------------------------------

        otp_service = OTPService()

        result = otp_service.generate_and_send_otp(
            email,
            'password_reset'
        )

        if not result.get('success'):

            return jsonify({
                'error': result.get(
                    'message',
                    'Unable to send password reset code'
                )
            }), 500

        response = {
            'message':
                'Password reset verification code sent',

            'expires_at':
                result.get('expires_at')
        }

        # ----------------------------------------------------
        # DEVELOPMENT FALLBACK
        # ----------------------------------------------------

        if result.get('otp_code'):

            response['otp_code'] = (
                result.get('otp_code')
            )

        return jsonify(
            response
        ), 200

    except Exception as e:

        print(
            f'Forgot password error: {e}'
        )

        return jsonify({
            'error':
                'Unable to process password reset request'
        }), 500


# ============================================================
# RESET PASSWORD - VERIFY OTP + CHANGE PASSWORD
# ============================================================

@auth_bp.route(
    '/reset-password',
    methods=['POST']
)
def reset_password():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                'error':
                    'Request data is required'
            }), 400

        # ----------------------------------------------------
        # READ DATA
        # ----------------------------------------------------

        email = clean_identifier(
            data.get('email')
        ).lower()

        otp_code = clean_identifier(
            data.get('otp_code')
        )

        new_password = data.get(
            'new_password'
        )

        # ----------------------------------------------------
        # REQUIRED FIELDS
        # ----------------------------------------------------

        if not email:

            return jsonify({
                'error':
                    'Email is required'
            }), 400

        if not otp_code:

            return jsonify({
                'error':
                    'OTP code is required'
            }), 400

        if not new_password:

            return jsonify({
                'error':
                    'New password is required'
            }), 400

        # ----------------------------------------------------
        # VALIDATE EMAIL
        # ----------------------------------------------------

        if not validate_email(email):

            return jsonify({
                'error':
                    'Invalid email format'
            }), 400

        # ----------------------------------------------------
        # VALIDATE OTP
        # ----------------------------------------------------

        if not re.fullmatch(
            r'\d{6}',
            otp_code
        ):

            return jsonify({
                'error':
                    'OTP must be a 6-digit code'
            }), 400

        # ----------------------------------------------------
        # VALIDATE PASSWORD
        # ----------------------------------------------------

        if len(new_password) < 6:

            return jsonify({
                'error': (
                    'New password must be at least '
                    '6 characters long'
                )
            }), 400

        # ----------------------------------------------------
        # FIND USER
        # ----------------------------------------------------

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            return jsonify({
                'error':
                    'Invalid or expired OTP'
            }), 400

        # ----------------------------------------------------
        # VERIFY PASSWORD RESET OTP
        #
        # OTPService.verify_otp consumes the OTP.
        # ----------------------------------------------------

        otp_service = OTPService()

        otp_result = otp_service.verify_otp(
            email,
            otp_code,
            'password_reset'
        )

        if not otp_result.get('success'):

            return jsonify({
                'error':
                    'Invalid or expired password reset code'
            }), 400

        # ----------------------------------------------------
        # CHANGE PASSWORD
        # ----------------------------------------------------

        user.set_password(
            new_password
        )

        db.session.commit()

        return jsonify({

            'message':
                'Password reset successfully. '
                'You can now login with your new password.'

        }), 200

    except Exception as e:

        print(
            f'Reset password error: {e}'
        )

        db.session.rollback()

        return jsonify({
            'error':
                'Unable to reset password'
        }), 500


# ============================================================
# REGISTER WITH OTP
# ============================================================

@auth_bp.route(
    '/register-with-otp',
    methods=['POST']
)
def register_with_otp():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                'error':
                    'Request data is required'
            }), 400

        # ----------------------------------------------------
        # READ FIELDS
        # ----------------------------------------------------

        email = clean_identifier(
            data.get('email')
        ).lower()

        username = clean_identifier(
            data.get('username')
        )

        password = data.get(
            'password'
        )

        first_name = clean_identifier(
            data.get('first_name')
        )

        last_name = clean_identifier(
            data.get('last_name')
        )

        phone = clean_identifier(
            data.get('phone')
        )

        address = clean_identifier(
            data.get('address')
        )

        otp_code = clean_identifier(
            data.get('otp_code')
        )

        # ----------------------------------------------------
        # REQUIRED FIELDS
        # ----------------------------------------------------

        required = {

            'Email':
                email,

            'Username':
                username,

            'Password':
                password,

            'First name':
                first_name,

            'Last name':
                last_name,

            'OTP code':
                otp_code

        }

        for field, value in required.items():

            if not value:

                return jsonify({

                    'error':
                        f'{field} is required'

                }), 400

        # ----------------------------------------------------
        # VALIDATE EMAIL
        # ----------------------------------------------------

        if not validate_email(email):

            return jsonify({
                'error':
                    'Invalid email format'
            }), 400

        # ----------------------------------------------------
        # VALIDATE USERNAME
        # ----------------------------------------------------

        if not re.fullmatch(
            r'[A-Za-z0-9_.-]{3,80}',
            username
        ):

            return jsonify({

                'error':
                    'Username must be 3-80 characters '
                    'and contain only letters, numbers, '
                    'underscore, dot or hyphen.'

            }), 400

        # ----------------------------------------------------
        # VALIDATE PASSWORD
        # ----------------------------------------------------

        if len(password) < 6:

            return jsonify({

                'error':
                    'Password must be at least '
                    '6 characters long'

            }), 400

        # ----------------------------------------------------
        # VALIDATE OTP
        # ----------------------------------------------------

        if not re.fullmatch(
            r'\d{6}',
            otp_code
        ):

            return jsonify({

                'error':
                    'OTP must be a 6-digit code'

            }), 400

        # ----------------------------------------------------
        # FIND EXISTING EMAIL ACCOUNT
        # ----------------------------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()

        # ----------------------------------------------------
        # ACTIVE ACCOUNT
        #
        # An active account cannot be registered again.
        # ----------------------------------------------------

        if (
            existing_user
            and existing_user.is_active
        ):

            return jsonify({

                'error':
                    'Email already registered'

            }), 400

        # ----------------------------------------------------
        # CHECK USERNAME
        #
        # If another user owns the username, reject it.
        #
        # If the username belongs to the same deactivated
        # account, it is allowed.
        # ----------------------------------------------------

        existing_username = None

        for candidate in User.query.all():
            candidate_username = (
                candidate.username or ''
            ).strip().lower()

            if candidate_username == username.lower():
                existing_username = candidate
                break

        if (
            existing_username
            and (
                not existing_user
                or existing_username.id
                != existing_user.id
            )
        ):

            return jsonify({

                'error':
                    'Username already taken'

            }), 400

        # ----------------------------------------------------
        # FIND REGISTRATION OTP
        #
        # We intentionally do NOT use OTPService.verify_otp()
        # here because verify_otp() consumes the OTP.
        #
        # This endpoint directly checks and consumes it.
        # ----------------------------------------------------

        otp = OTP.query.filter(
            OTP.email == email,
            OTP.otp_code == otp_code,
            OTP.purpose == 'registration',
            OTP.is_used.is_(False),
            OTP.expires_at > db.func.now()
        ).first()

        if not otp:

            return jsonify({

                'error':
                    'Invalid or expired OTP'

            }), 400

        # ----------------------------------------------------
        # CONSUME OTP
        # ----------------------------------------------------

        otp.is_used = True

        # ====================================================
        # REACTIVATE DEACTIVATED ACCOUNT
        # ====================================================

        if existing_user:

            # ------------------------------------------------
            # This branch can only be reached for a
            # DEACTIVATED account because active accounts
            # were rejected above.
            # ------------------------------------------------

            existing_user.username = username

            existing_user.first_name = first_name

            existing_user.last_name = last_name

            existing_user.phone = (
                phone or None
            )

            existing_user.address = (
                address or None
            )

            existing_user.role = (
                existing_user.role
                or 'user'
            )

            # ------------------------------------------------
            # REACTIVATE
            # ------------------------------------------------

            existing_user.is_active = True

            existing_user.is_verified = True

            # ------------------------------------------------
            # SET NEW PASSWORD
            # ------------------------------------------------

            existing_user.set_password(
                password
            )

            user = existing_user

            try:

                db.session.commit()

            except Exception as e:

                db.session.rollback()

                print(
                    f'Account reactivation error: {e}'
                )

                return jsonify({

                    'error':
                        'Unable to reactivate account. '
                        'The username or email may already exist.'

                }), 400

            # ------------------------------------------------
            # WELCOME / REACTIVATION EMAIL
            # ------------------------------------------------

            try:

                EmailService().send_welcome_email(
                    user.email,
                    user.username
                )

            except Exception as e:

                print(
                    f'Welcome email error: {e}'
                )

            # ------------------------------------------------
            # CREATE LOGIN TOKEN
            # ------------------------------------------------

            access_token = user.get_token()

            return jsonify({

                'message':
                    'Account reactivated successfully',

                'access_token':
                    access_token,

                'user':
                    user.to_dict()

            }), 200

        # ====================================================
        # CREATE BRAND NEW ACCOUNT
        # ====================================================

        user = User(

            username=username,

            email=email,

            first_name=first_name,

            last_name=last_name,

            phone=phone or None,

            address=address or None,

            role='user',

            is_active=True,

            is_verified=True

        )

        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        user.set_password(
            password
        )

        db.session.add(
            user
        )

        try:

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            print(
                f'User creation error: {e}'
            )

            return jsonify({

                'error':
                    'Unable to create account. '
                    'The username or email may already exist.'

            }), 400

        # ----------------------------------------------------
        # WELCOME EMAIL
        # ----------------------------------------------------

        try:

            EmailService().send_welcome_email(
                user.email,
                user.username
            )

        except Exception as e:

            print(
                f'Welcome email error: {e}'
            )

        # ----------------------------------------------------
        # CREATE LOGIN TOKEN
        # ----------------------------------------------------

        access_token = user.get_token()

        return jsonify({

            'message':
                'Registration completed successfully',

            'access_token':
                access_token,

            'user':
                user.to_dict()

        }), 201

    except Exception as e:

        db.session.rollback()

        print(
            f'Registration with OTP error: {e}'
        )

        return jsonify({

            'error':
                'Unable to complete registration'

        }), 500


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route(
    '/login',
    methods=['POST']
)
def login():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                'error':
                    'Request data is required'
            }), 400

        # ----------------------------------------------------
        # ACCEPT COMMON FRONTEND FIELD NAMES
        # ----------------------------------------------------

        identifier = (

            data.get('identifier')

            or data.get('username')

            or data.get('email')

        )

        password = data.get(
            'password'
        )

        identifier = clean_identifier(
            identifier
        )

        if not identifier or not password:

            return jsonify({

                'error':
                    'Username/email and password are required'

            }), 400

        # ----------------------------------------------------
        # CASE-INSENSITIVE LOGIN
        # ----------------------------------------------------

        identifier_lower = (
            identifier.lower()
        )

        users = User.query.all()

        user = None

        for candidate in users:

            candidate_username = (
                candidate.username or ''
            ).strip().lower()

            candidate_email = (
                candidate.email or ''
            ).strip().lower()

            if (
                candidate_username
                == identifier_lower
                or
                candidate_email
                == identifier_lower
            ):

                user = candidate

                break

        # ----------------------------------------------------
        # USER NOT FOUND
        # ----------------------------------------------------

        if not user:

            return jsonify({

                'error':
                    'Invalid credentials'

            }), 401

        # ----------------------------------------------------
        # PASSWORD
        # ----------------------------------------------------

        if not user.check_password(
            password
        ):

            return jsonify({

                'error':
                    'Invalid credentials'

            }), 401

        # ----------------------------------------------------
        # DEACTIVATED ACCOUNT
        #
        # IMPORTANT:
        # We do NOT automatically reactivate the account.
        #
        # User must explicitly reactivate it through
        # registration + OTP.
        # ----------------------------------------------------

        if not user.is_active:

            return jsonify({

                'error':
                    'Account is deactivated'

            }), 401

        # ----------------------------------------------------
        # EMAIL VERIFICATION
        # ----------------------------------------------------

        if not user.is_verified:

            return jsonify({

                'error':
                    'Email not verified. '
                    'Please verify your email before logging in.'

            }), 401

        # ----------------------------------------------------
        # CREATE TOKEN
        # ----------------------------------------------------

        access_token = user.get_token()

        return jsonify({

            'message':
                'Login successful',

            'access_token':
                access_token,

            'user':
                user.to_dict()

        }), 200

    except Exception as e:

        print(
            f'Login error: {e}'
        )

        return jsonify({

            'error':
                'An unexpected error occurred during login'

        }), 500


# ============================================================
# GET PROFILE
# ============================================================

@auth_bp.route(
    '/profile',
    methods=['GET']
)
@jwt_required()
def get_profile():

    try:

        user_id = get_jwt_identity()

        user = User.query.get(
            user_id
        )

        if not user:

            return jsonify({

                'error':
                    'User not found'

            }), 404

        return jsonify({

            'user':
                user.to_dict()

        }), 200

    except Exception as e:

        print(
            f'Profile error: {e}'
        )

        return jsonify({

            'error':
                'Unable to retrieve profile'

        }), 500


# ============================================================
# UPDATE PROFILE
# ============================================================

@auth_bp.route(
    '/profile',
    methods=['PUT']
)
@jwt_required()
def update_profile():

    try:

        user_id = get_jwt_identity()

        user = User.query.get(
            user_id
        )

        if not user:

            return jsonify({

                'error':
                    'User not found'

            }), 404

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({

                'error':
                    'Request data is required'

            }), 400

        allowed_fields = [

            'first_name',

            'last_name',

            'phone',

            'address'

        ]

        for field in allowed_fields:

            if field in data:

                setattr(

                    user,

                    field,

                    data[field]

                )

        db.session.commit()

        return jsonify({

            'message':
                'Profile updated successfully',

            'user':
                user.to_dict()

        }), 200

    except Exception as e:

        db.session.rollback()

        print(
            f'Profile update error: {e}'
        )

        return jsonify({

            'error':
                'Unable to update profile'

        }), 500


# ============================================================
# DEACTIVATE ACCOUNT
# ============================================================

@auth_bp.route(
    '/deactivate',
    methods=['POST']
)
@jwt_required()
def deactivate_account():

    try:

        user_id = get_jwt_identity()

        user = User.query.get(
            user_id
        )

        if not user:

            return jsonify({

                'error':
                    'User not found'

            }), 404

        # ----------------------------------------------------
        # DEACTIVATE USER
        # ----------------------------------------------------

        user.is_active = False

        db.session.commit()

        return jsonify({

            'message':
                'Your account has been deactivated successfully.'

        }), 200

    except Exception as e:

        db.session.rollback()

        print(
            f'Account deactivation error: {e}'
        )

        return jsonify({

            'error':
                'Unable to deactivate account'

        }), 500


# ============================================================
# CHANGE PASSWORD
# ============================================================

@auth_bp.route(
    '/change-password',
    methods=['POST']
)
@jwt_required()
def change_password():

    try:

        user_id = get_jwt_identity()

        user = User.query.get(
            user_id
        )

        if not user:

            return jsonify({

                'error':
                    'User not found'

            }), 404

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({

                'error':
                    'Request data is required'

            }), 400

        current_password = data.get(
            'current_password'
        )

        new_password = data.get(
            'new_password'
        )

        if (
            not current_password
            or not new_password
        ):

            return jsonify({

                'error':
                    'Current password and new password are required'

            }), 400

        # ----------------------------------------------------
        # CHECK CURRENT PASSWORD
        # ----------------------------------------------------

        if not user.check_password(
            current_password
        ):

            return jsonify({

                'error':
                    'Current password is incorrect'

            }), 400

        # ----------------------------------------------------
        # PASSWORD LENGTH
        # ----------------------------------------------------

        if len(new_password) < 6:

            return jsonify({

                'error':
                    'New password must be at least 6 characters long'

            }), 400

        # ----------------------------------------------------
        # SET NEW PASSWORD
        # ----------------------------------------------------

        user.set_password(
            new_password
        )

        db.session.commit()

        return jsonify({

            'message':
                'Password changed successfully'

        }), 200

    except Exception as e:

        db.session.rollback()

        print(
            f'Change password error: {e}'
        )

        return jsonify({

            'error':
                'Unable to change password'

        }), 500