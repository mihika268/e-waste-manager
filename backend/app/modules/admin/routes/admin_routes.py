from flask import Blueprint, jsonify, request
from app.models.user import User
from app.models.ewaste import EWasteItem as EWaste
from app.models.community import CommunityPost
from app.models.feedback import Feedback
from app.modules.shared.decorators.role_required import admin_required
from app import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# User Management Routes
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users(current_user):
    """Get all users with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    role = request.args.get('role')
    
    query = User.query
    if role:
        query = query.filter_by(role=role)
    
    users = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    })

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_details(current_user, user_id):
    """Get detailed information about a specific user"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
@admin_required
def toggle_user_status(current_user, user_id):
    """Activate/Deactivate user account"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({
        'message': f'User {user.username} has been {"activated" if user.is_active else "deactivated"}',
        'user': user.to_dict()
    })

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(current_user, user_id):
    """Update user role"""
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in ['user', 'admin', 'collector']:
        return jsonify({'error': 'Invalid role'}), 400
    
    user = User.query.get_or_404(user_id)
    user.role = new_role
    db.session.commit()
    
    return jsonify({
        'message': f'User {user.username} role updated to {new_role}',
        'user': user.to_dict()
    })

# E-Waste Management Routes
@admin_bp.route('/e-waste', methods=['GET'])
@admin_required
def get_all_e_waste(current_user):
    """Get all e-waste items with analytics"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = EWaste.query
    if status:
        query = query.filter_by(status=status)
    
    e_waste_items = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'e_waste_items': [item.to_dict() for item in e_waste_items.items],
        'total': e_waste_items.total,
        'pages': e_waste_items.pages,
        'current_page': page
    })

@admin_bp.route('/e-waste/analytics', methods=['GET'])
@admin_required
def get_e_waste_analytics(current_user):
    """Get e-waste analytics and statistics"""
    total_items = EWaste.query.count()
    by_status = db.session.query(EWaste.status, db.func.count(EWaste.id)).group_by(EWaste.status).all()
    by_category = db.session.query(EWaste.category, db.func.count(EWaste.id)).group_by(EWaste.category).all()
    
    return jsonify({
        'total_items': total_items,
        'by_status': dict(by_status),
        'by_category': dict(by_category),
        'recent_items': [item.to_dict() for item in EWaste.query.order_by(EWaste.created_at.desc()).limit(5).all()]
    })

# Community Management Routes
@admin_bp.route('/community/posts', methods=['GET'])
@admin_required
def get_all_community_posts(current_user):
    """Get all community posts with moderation capabilities"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'posts': [post.to_dict() for post in posts.items],
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    })

@admin_bp.route('/community/posts/<int:post_id>/moderate', methods=['PUT'])
@admin_required
def moderate_community_post(current_user, post_id):
    """Moderate a community post"""
    post = CommunityPost.query.get_or_404(post_id)
    data = request.get_json()
    
    action = data.get('action')
    if action == 'hide':
        post.is_hidden = True
    elif action == 'unhide':
        post.is_hidden = False
    elif action == 'delete':
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted successfully'})
    else:
        return jsonify({'error': 'Invalid action'}), 400
    
    db.session.commit()
    return jsonify({
        'message': f'Post {action}d successfully',
        'post': post.to_dict()
    })

# Feedback Management Routes
@admin_bp.route('/feedback', methods=['GET'])
@admin_required
def get_all_feedback(current_user):
    """Get all user feedback"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Feedback.query
    if status:
        query = query.filter_by(status=status)
    
    feedback_items = query.order_by(Feedback.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'feedback': [item.to_dict() for item in feedback_items.items],
        'total': feedback_items.total,
        'pages': feedback_items.pages,
        'current_page': page
    })

@admin_bp.route('/feedback/<int:feedback_id>/respond', methods=['PUT'])
@admin_required
def respond_to_feedback(current_user, feedback_id):
    """Respond to user feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)
    data = request.get_json()
    
    response_text = data.get('response')
    if not response_text:
        return jsonify({'error': 'Response text is required'}), 400
    
    feedback.admin_response = response_text
    feedback.responded_at = datetime.utcnow()
    feedback.status = 'responded'
    db.session.commit()
    
    return jsonify({
        'message': 'Feedback response sent successfully',
        'feedback': feedback.to_dict()
    })

# Dashboard Analytics
@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats(current_user):
    """Get comprehensive dashboard statistics"""
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_e_waste': EWaste.query.count(),
        'total_posts': CommunityPost.query.count(),
        'total_feedback': Feedback.query.count(),
        'pending_feedback': Feedback.query.filter_by(status='pending').count(),
        'users_by_role': {
            'user': User.query.filter_by(role='user').count(),
            'admin': User.query.filter_by(role='admin').count(),
            'collector': User.query.filter_by(role='collector').count()
        },
        'recent_users': [user.to_dict() for user in User.query.order_by(User.created_at.desc()).limit(5).all()],
        'recent_e_waste': [item.to_dict() for item in EWaste.query.order_by(EWaste.created_at.desc()).limit(5).all()]
    }
    
    return jsonify(stats)