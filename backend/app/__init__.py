"""
E-Waste Management System - Flask Application Factory

This module initializes the Flask application with all necessary extensions
and blueprints. It serves as the entry point for the application setup.

Author: Muskan Uttam
Created: 2025
Purpose: Create a centralized way to configure and initialize the Flask app
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from app.config import Config
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This allows us to keep sensitive data like API keys outside of version control
load_dotenv()

# Initialize Flask extensions
# These will be registered with the app instance later
db = SQLAlchemy()        # Database ORM for managing SQLite database
jwt = JWTManager()      # JSON Web Token management for authentication
bcrypt = Bcrypt()       # Password hashing library for secure password storage

def create_app():
    """
    Application factory pattern - creates and configures the Flask app instance.
    
    This function:
    1. Creates a Flask app instance
    2. Loads configuration from Config class
    3. Registers all extensions (db, jwt, bcrypt)
    4. Registers all blueprints (routes)
    5. Creates database tables
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, template_folder='../../frontend/templates', static_folder='../../frontend/static')
    app.config.from_object(Config)
    
    # Initialize extensions
    # These connect the extensions to our Flask app instance
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)
    
    # Register blueprints (routes)
    # Each blueprint handles a specific part of the application
    
    # Authentication routes (login, register, profile)
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.ewaste import ewaste_bp
    from app.routes.scanner import scanner_bp
    from app.routes.community import community_bp
    from app.routes.analytics import analytics_bp
    from app.routes.feedback import feedback_bp
    from app.routes.rewards import rewards_bp
    from app.routes.certificates import certificates_bp
    from app.routes.referral import referral_bp
    from app.routes.notifications import notification_bp
    from app.routes.reschedule import reschedule_bp
    
    # Register modular admin and user routes
    from app.modules.admin.routes.admin_routes import admin_bp
    from app.modules.user.routes.user_routes import user_bp
    
    # Register all blueprints with their URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(ewaste_bp, url_prefix='/api/ewaste')
    app.register_blueprint(scanner_bp, url_prefix='/api/scanner')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    app.register_blueprint(rewards_bp, url_prefix='/api/rewards')
    app.register_blueprint(certificates_bp, url_prefix='/api/certificates')
    app.register_blueprint(referral_bp, url_prefix='/api/referral')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(reschedule_bp, url_prefix='/api/reschedule')
    
    # Create tables
    with app.app_context():
        # Ensure upload directory exists
        upload_dir = app.config.get('UPLOAD_FOLDER')
        try:
            if upload_dir and not os.path.exists(upload_dir):
                os.makedirs(upload_dir, exist_ok=True)
        except Exception:
            pass

        # Import models to ensure SQLAlchemy registers all tables
        from app.models import user as _user  # noqa: F401
        from app.models import ewaste as _ewaste  # noqa: F401
        from app.models import scanner as _scanner  # noqa: F401
        from app.models import community as _community  # noqa: F401
        from app.models import feedback as _feedback  # noqa: F401
        from app.models import otp as _otp  # noqa: F401
        from app.models import rewards as _rewards  # noqa: F401
        from app.models import referral as _referral  # noqa: F401
        from app.models import recycling_certificate as _certificate  # noqa: F401
        from app.models import notification_preference as _notification  # noqa: F401
        db.create_all()
    
    return app
