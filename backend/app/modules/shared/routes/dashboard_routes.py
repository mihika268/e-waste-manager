from flask import Blueprint, render_template, jsonify
from app.modules.shared.decorators.role_required import admin_required, user_required
from app import db

# Create a separate blueprint for serving dashboard templates
dashboard_bp = Blueprint('dashboard', __name__)

# Admin Dashboard Route
@dashboard_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard(current_user):
    """Serve the admin dashboard template"""
    return render_template('admin_dashboard.html')

# User Dashboard Route  
@dashboard_bp.route('/user/dashboard')
@user_required
def user_dashboard(current_user):
    """Serve the user dashboard template"""
    return render_template('user_dashboard.html')

# Profile page route
@dashboard_bp.route('/user/profile')
@user_required
def user_profile(current_user):
    """Serve the user profile page"""
    return render_template('user_dashboard.html', section='profile')

# Admin Users management page
@dashboard_bp.route('/admin/users')
@admin_required
def admin_users(current_user):
    """Serve the admin users management page"""
    return render_template('admin_dashboard.html', section='users')

# Admin E-Waste management page
@dashboard_bp.route('/admin/ewaste')
@admin_required
def admin_ewaste(current_user):
    """Serve the admin e-waste management page"""
    return render_template('admin_dashboard.html', section='ewaste')

# Admin Community management page
@dashboard_bp.route('/admin/community')
@admin_required
def admin_community(current_user):
    """Serve the admin community management page"""
    return render_template('admin_dashboard.html', section='community')

# Admin Feedback management page
@dashboard_bp.route('/admin/feedback')
@admin_required
def admin_feedback(current_user):
    """Serve the admin feedback management page"""
    return render_template('admin_dashboard.html', section='feedback')

# User E-Waste page
@dashboard_bp.route('/user/ewaste')
@user_required
def user_ewaste(current_user):
    """Serve the user e-waste page"""
    return render_template('user_dashboard.html', section='ewaste')

# User Community page
@dashboard_bp.route('/user/community')
@user_required
def user_community(current_user):
    """Serve the user community page"""
    return render_template('user_dashboard.html', section='community')

# User Feedback page
@dashboard_bp.route('/user/feedback')
@user_required
def user_feedback(current_user):
    """Serve the user feedback page"""
    return render_template('user_dashboard.html', section='feedback')