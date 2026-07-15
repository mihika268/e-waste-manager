import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from both root and backend .env files to avoid CWD issues
# Root .env
load_dotenv()
# Backend .env
_current_dir = os.path.dirname(os.path.dirname(__file__))  # backend/app -> backend
_backend_env = os.path.join(_current_dir, '.env')
if os.path.exists(_backend_env):
    load_dotenv(_backend_env)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ewaste-management-secret-key-2024'
    # Base directories
    base_dir = os.path.dirname(os.path.dirname(__file__))  # backend/app -> backend
    instance_dir = os.path.join(base_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)

    # Ensure SQLite file lives in backend/instance/ewaste.db for consistent paths
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        if db_url.startswith('sqlite:///'):
            # Extract path after sqlite scheme
            db_path = db_url.replace('sqlite:///', '', 1)
            # If relative, place it inside instance directory
            if not os.path.isabs(db_path):
                SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(instance_dir, os.path.basename(db_path))
            else:
                SQLALCHEMY_DATABASE_URI = db_url
        else:
            # Non-sqlite URLs (e.g., PostgreSQL) are used as-is
            SQLALCHEMY_DATABASE_URI = db_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(instance_dir, 'ewaste.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # File uploads
    # Resolve to absolute path. If env provides a relative path, make it relative to backend dir
    _env_upload = os.environ.get('UPLOAD_FOLDER')
    if _env_upload:
        _upload_path = _env_upload
        if not os.path.isabs(_upload_path):
            _upload_path = os.path.normpath(os.path.join(base_dir, _upload_path))
        UPLOAD_FOLDER = _upload_path
    else:
        UPLOAD_FOLDER = os.path.normpath(os.path.join(base_dir, 'uploads'))
    # Limit upload size to 16 MB
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # Email configuration for OTP
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # Default sender falls back to the SMTP username when not explicitly set
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME') or 'noreply@ewaste.com'
    
    # OTP configuration
    OTP_EXPIRY_MINUTES = int(os.environ.get('OTP_EXPIRY_MINUTES', 10))
    OTP_LENGTH = int(os.environ.get('OTP_LENGTH', 6))