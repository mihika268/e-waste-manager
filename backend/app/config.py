import os
from datetime import timedelta
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

_current_dir = os.path.dirname(os.path.dirname(__file__))
_backend_env = os.path.join(_current_dir, '.env')

if os.path.exists(_backend_env):
    load_dotenv(_backend_env, override=True)


class Config:

    # ============================================================
    # SECURITY
    # ============================================================

    SECRET_KEY = (
        os.environ.get('SECRET_KEY')
        or 'ewaste-management-secret-key-2024'
    )

    JWT_SECRET_KEY = (
        os.environ.get('JWT_SECRET_KEY')
        or 'jwt-secret-string'
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # ============================================================
    # BASE DIRECTORIES
    # ============================================================

    base_dir = os.path.dirname(
        os.path.dirname(__file__)
    )

    instance_dir = os.path.join(
        base_dir,
        'instance'
    )

    os.makedirs(
        instance_dir,
        exist_ok=True
    )

    # ============================================================
    # DATABASE
    # ============================================================

    db_url = os.environ.get('DATABASE_URL')

    if db_url:

        if db_url.startswith('sqlite:///'):

            db_path = db_url.replace(
                'sqlite:///',
                '',
                1
            )

            if not os.path.isabs(db_path):

                SQLALCHEMY_DATABASE_URI = (
                    'sqlite:///'
                    + os.path.join(
                        instance_dir,
                        os.path.basename(db_path)
                    )
                )

            else:

                SQLALCHEMY_DATABASE_URI = db_url

        else:

            SQLALCHEMY_DATABASE_URI = db_url

    else:

        SQLALCHEMY_DATABASE_URI = (
            'sqlite:///'
            + os.path.join(
                instance_dir,
                'ewaste.db'
            )
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============================================================
    # FILE UPLOADS
    # ============================================================

    _env_upload = os.environ.get(
        'UPLOAD_FOLDER'
    )

    if _env_upload:

        _upload_path = _env_upload

        if not os.path.isabs(_upload_path):

            _upload_path = os.path.normpath(
                os.path.join(
                    base_dir,
                    _upload_path
                )
            )

        UPLOAD_FOLDER = _upload_path

    else:

        UPLOAD_FOLDER = os.path.normpath(
            os.path.join(
                base_dir,
                'uploads'
            )
        )

    MAX_CONTENT_LENGTH = int(
        os.environ.get(
            'MAX_CONTENT_LENGTH'
        )
        or 16 * 1024 * 1024
    )

    # ============================================================
    # RESEND EMAIL CONFIGURATION
    # ============================================================

    RESEND_API_KEY = os.environ.get(
        'RESEND_API_KEY'
    )

    RESEND_FROM_EMAIL = (
        os.environ.get(
            'RESEND_FROM_EMAIL'
        )
        or 'onboarding@resend.dev'
    )

    # ============================================================
    # LEGACY SMTP CONFIGURATION
    # ============================================================
    # These are kept only for compatibility.
    # The application uses Resend for OTP emails.

    MAIL_SERVER = os.environ.get(
        'MAIL_SERVER'
    )

    MAIL_PORT = int(
        os.environ.get(
            'MAIL_PORT'
        )
        or 587
    )

    MAIL_USE_TLS = (
        os.environ.get(
            'MAIL_USE_TLS',
            'false'
        ).lower()
        in ['true', 'on', '1']
    )

    MAIL_USERNAME = os.environ.get(
        'MAIL_USERNAME'
    )

    MAIL_PASSWORD = os.environ.get(
        'MAIL_PASSWORD'
    )

    MAIL_DEFAULT_SENDER = os.environ.get(
        'MAIL_DEFAULT_SENDER'
    )

    # ============================================================
    # OTP CONFIGURATION
    # ============================================================

    OTP_EXPIRY_MINUTES = int(
        os.environ.get(
            'OTP_EXPIRY_MINUTES'
        )
        or 10
    )

    OTP_LENGTH = int(
        os.environ.get(
            'OTP_LENGTH'
        )
        or 6
    )