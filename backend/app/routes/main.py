from flask import Blueprint, render_template, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.ewaste import EWasteItem, EWasteCategory, Collection

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the login page"""
    return render_template('login.html')

@main_bp.route('/login')
def login_page():
    """Serve the login page"""
    return render_template('login.html')

@main_bp.route('/register')
def register_page():
    """Serve the registration page"""
    return render_template('register.html')

@main_bp.route('/debug-register')
def debug_register_page():
    """Serve the debug registration page"""
    return render_template('debug_register.html')

@main_bp.route('/dashboard')
def dashboard():
    """Serve the dashboard page"""
    return render_template('dashboard.html')



@main_bp.route('/items')
def items_page():
    """Serve the items management page"""
    return render_template('items.html')

@main_bp.route('/collections')
def collections_page():
    """Serve the collections page"""
    return render_template('collections.html')

@main_bp.route('/profile')
def profile_page():
    """Serve the profile page"""
    return render_template('profile.html')

@main_bp.route('/community')
def community_page():
    """Serve the community feed page"""
    return render_template('community.html')

@main_bp.route('/analytics')
def analytics_page():
    """Serve the analytics dashboard page"""
    return render_template('analytics.html')

@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files (images for scans, community posts, complaints)"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return send_from_directory(upload_folder, filename)

@main_bp.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics for the logged-in user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's e-waste statistics
        total_items = EWasteItem.query.filter_by(user_id=user_id).count()
        registered_items = EWasteItem.query.filter_by(user_id=user_id, status='registered').count()
        collected_items = EWasteItem.query.filter_by(user_id=user_id, status='collected').count()
        recycled_items = EWasteItem.query.filter_by(user_id=user_id, status='recycled').count()
        
        # Get pending collections
        pending_collections = Collection.query.filter_by(user_id=user_id, status='scheduled').count()
        
        # Calculate total estimated value
        items = EWasteItem.query.filter_by(user_id=user_id).all()
        total_value = sum(item.estimated_value or 0 for item in items)
        
        stats = {
            'total_items': total_items,
            'registered_items': registered_items,
            'collected_items': collected_items,
            'recycled_items': recycled_items,
            'pending_collections': pending_collections,
            'total_estimated_value': total_value
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
