"""
E-Waste Management System - Flask Application Factory

This module initializes the Flask application with all necessary extensions
and blueprints. It serves as the entry point for the application setup.

Created: 2025
Purpose: Create a centralized way to configure and initialize the Flask app
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from app.config import Config
import os
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# INITIALIZE FLASK EXTENSIONS
# ============================================================

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()


# ============================================================
# APPLICATION FACTORY
# ============================================================

def create_app():
    """
    Application factory pattern - creates and configures
    the Flask application instance.
    """

    # --------------------------------------------------------
    # CREATE FLASK APP
    # --------------------------------------------------------

    app = Flask(
        __name__,
        template_folder='../../frontend/templates',
        static_folder='../../frontend/static'
    )

    app.config.from_object(Config)


    # --------------------------------------------------------
    # INITIALIZE EXTENSIONS
    # --------------------------------------------------------

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)


    # ========================================================
    # REGISTER BLUEPRINTS
    # ========================================================

    # Authentication routes
    from app.routes.auth import auth_bp

    # Main application routes
    from app.routes.main import main_bp

    # E-waste routes
    from app.routes.ewaste import ewaste_bp

    # Scanner routes
    from app.routes.scanner import scanner_bp

    # Community routes
    from app.routes.community import community_bp

    # Analytics routes
    from app.routes.analytics import analytics_bp

    # Feedback routes
    from app.routes.feedback import feedback_bp

    # Rewards routes
    from app.routes.rewards import rewards_bp

    # Certificate routes
    from app.routes.certificates import certificates_bp

    # Referral routes
    from app.routes.referral import referral_bp

    # Notification routes
    from app.routes.notifications import notification_bp

    # Reschedule routes
    from app.routes.reschedule import reschedule_bp


    # --------------------------------------------------------
    # ADMIN AND USER MODULES
    # --------------------------------------------------------

    from app.modules.admin.routes.admin_routes import admin_bp
    from app.modules.user.routes.user_routes import user_bp


    # ========================================================
    # REGISTER BLUEPRINTS WITH URL PREFIXES
    # ========================================================

    app.register_blueprint(
        auth_bp,
        url_prefix='/api/auth'
    )

    app.register_blueprint(
        main_bp
    )

    app.register_blueprint(
        ewaste_bp,
        url_prefix='/api/ewaste'
    )

    app.register_blueprint(
        scanner_bp,
        url_prefix='/api/scanner'
    )

    app.register_blueprint(
        community_bp,
        url_prefix='/api/community'
    )

    app.register_blueprint(
        analytics_bp,
        url_prefix='/api/analytics'
    )

    app.register_blueprint(
        feedback_bp,
        url_prefix='/api/feedback'
    )

    app.register_blueprint(
        rewards_bp,
        url_prefix='/api/rewards'
    )

    app.register_blueprint(
        certificates_bp,
        url_prefix='/api/certificates'
    )

    app.register_blueprint(
        referral_bp,
        url_prefix='/api/referral'
    )

    app.register_blueprint(
        notification_bp,
        url_prefix='/api/notifications'
    )

    app.register_blueprint(
        reschedule_bp,
        url_prefix='/api/reschedule'
    )

    app.register_blueprint(
        admin_bp
    )

    app.register_blueprint(
        user_bp
    )


    # ========================================================
    # AUTHENTICATION / PASSWORD PAGE ROUTES
    # ========================================================

    @app.route('/forgot-password', methods=['GET'])
    def forgot_password_page():
        """
        Display the Forgot Password page.
        """

        return render_template(
            'forgot_password.html'
        )


   

    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    with app.app_context():

        # ----------------------------------------------------
        # CREATE UPLOAD DIRECTORY
        # ----------------------------------------------------

        upload_dir = app.config.get(
            'UPLOAD_FOLDER'
        )

        try:

            if (
                upload_dir
                and not os.path.exists(upload_dir)
            ):

                os.makedirs(
                    upload_dir,
                    exist_ok=True
                )

        except Exception:
            pass


        # ----------------------------------------------------
        # IMPORT MODELS
        # ----------------------------------------------------

        from app.models import user as _user
        from app.models import ewaste as _ewaste
        from app.models import scanner as _scanner
        from app.models import community as _community
        from app.models import feedback as _feedback
        from app.models import otp as _otp
        from app.models import rewards as _rewards
        from app.models import referral as _referral
        from app.models import recycling_certificate as _certificate
        from app.models import notification_preference as _notification


        # ----------------------------------------------------
        # CREATE DATABASE TABLES
        # ----------------------------------------------------

        db.create_all()


    # ========================================================
    # RETURN APPLICATION
    # ========================================================

    return app