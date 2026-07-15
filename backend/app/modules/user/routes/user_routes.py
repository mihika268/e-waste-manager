from flask import Blueprint, jsonify, request
from app.models.user import User
from app.models.ewaste import EWasteItem as EWaste
from app.models.community import CommunityPost
from app.models.feedback import Feedback
from app.modules.shared.decorators.role_required import user_required
from app.modules.shared.middleware.auth_middleware import require_auth, check_email_verified
from app import db
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# User Profile Routes
@user_bp.route('/profile', methods=['GET'])
@user_required
def get_user_profile(current_user):
    """Get current user's profile"""
    return jsonify(current_user.to_dict())

@user_bp.route('/profile', methods=['PUT'])
@user_required
def update_user_profile(current_user):
    """Update current user's profile"""
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'phone', 'address']
    for field in allowed_fields:
        if field in data:
            setattr(current_user, field, data[field])
    
    db.session.commit()
    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict()
    })

@user_bp.route('/profile/change-password', methods=['PUT'])
@user_required
def change_password(current_user):
    """Change user's password"""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new passwords are required'}), 400
    
    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'})

# E-Waste Personal Management
@user_bp.route('/e-waste', methods=['GET'])
@user_required
def get_user_e_waste(current_user):
    """Get current user's e-waste items"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = EWaste.query.filter_by(user_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    
    e_waste_items = query.order_by(EWaste.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'e_waste_items': [item.to_dict() for item in e_waste_items.items],
        'total': e_waste_items.total,
        'pages': e_waste_items.pages,
        'current_page': page
    })

@user_bp.route('/e-waste', methods=['POST'])
@user_required
def create_e_waste_item(current_user):
    """Create a new e-waste item"""
    data = request.get_json()
    
    required_fields = ['category', 'description', 'location']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    e_waste_item = EWaste(
        user_id=current_user.id,
        category=data['category'],
        description=data['description'],
        location=data['location'],
        estimated_weight=data.get('estimated_weight'),
        image_url=data.get('image_url'),
        status='pending'
    )
    
    db.session.add(e_waste_item)
    db.session.commit()
    
    return jsonify({
        'message': 'E-waste item created successfully',
        'e_waste_item': e_waste_item.to_dict()
    }), 201

@user_bp.route('/e-waste/<int:item_id>', methods=['PUT'])
@user_required
def update_e_waste_item(current_user, item_id):
    """Update user's e-waste item"""
    e_waste_item = EWaste.query.filter_by(id=item_id, user_id=current_user.id).first()
    
    if not e_waste_item:
        return jsonify({'error': 'E-waste item not found'}), 404
    
    data = request.get_json()
    allowed_fields = ['category', 'description', 'location', 'estimated_weight', 'image_url']
    
    for field in allowed_fields:
        if field in data:
            setattr(e_waste_item, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'E-waste item updated successfully',
        'e_waste_item': e_waste_item.to_dict()
    })

@user_bp.route('/e-waste/<int:item_id>', methods=['DELETE'])
@user_required
def delete_e_waste_item(current_user, item_id):
    """Delete user's e-waste item"""
    e_waste_item = EWaste.query.filter_by(id=item_id, user_id=current_user.id).first()
    
    if not e_waste_item:
        return jsonify({'error': 'E-waste item not found'}), 404
    
    db.session.delete(e_waste_item)
    db.session.commit()
    
    return jsonify({'message': 'E-waste item deleted successfully'})

# Community Posts (Personal)
@user_bp.route('/community/posts', methods=['GET'])
@user_required
def get_user_community_posts(current_user):
    """Get current user's community posts"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    posts = CommunityPost.query.filter_by(user_id=current_user.id).order_by(
        CommunityPost.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'posts': [post.to_dict() for post in posts.items],
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    })

@user_bp.route('/community/posts', methods=['POST'])
@user_required
def create_community_post(current_user):
    """Create a new community post"""
    data = request.get_json()
    
    required_fields = ['title', 'content']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    post = CommunityPost(
        user_id=current_user.id,
        title=data['title'],
        content=data['content'],
        category=data.get('category', 'general')
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'message': 'Community post created successfully',
        'post': post.to_dict()
    }), 201

@user_bp.route('/community/posts/<int:post_id>', methods=['PUT'])
@user_required
def update_community_post(current_user, post_id):
    """Update user's community post"""
    post = CommunityPost.query.filter_by(id=post_id, user_id=current_user.id).first()
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    data = request.get_json()
    allowed_fields = ['title', 'content', 'category']
    
    for field in allowed_fields:
        if field in data:
            setattr(post, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Post updated successfully',
        'post': post.to_dict()
    })

@user_bp.route('/community/posts/<int:post_id>', methods=['DELETE'])
@user_required
def delete_community_post(current_user, post_id):
    """Delete user's community post"""
    post = CommunityPost.query.filter_by(id=post_id, user_id=current_user.id).first()
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'})

# Feedback Routes
@user_bp.route('/feedback', methods=['GET'])
@user_required
def get_user_feedback(current_user):
    """Get current user's feedback"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    feedback_items = Feedback.query.filter_by(user_id=current_user.id).order_by(
        Feedback.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'feedback': [item.to_dict() for item in feedback_items.items],
        'total': feedback_items.total,
        'pages': feedback_items.pages,
        'current_page': page
    })

@user_bp.route('/feedback', methods=['POST'])
@user_required
def create_feedback(current_user):
    """Create new feedback"""
    data = request.get_json()
    
    required_fields = ['subject', 'message']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    feedback = Feedback(
        user_id=current_user.id,
        subject=data['subject'],
        message=data['message'],
        category=data.get('category', 'general'),
        status='pending'
    )
    
    db.session.add(feedback)
    db.session.commit()
    
    return jsonify({
        'message': 'Feedback submitted successfully',
        'feedback': feedback.to_dict()
    }), 201

# User Dashboard
@user_bp.route('/dashboard', methods=['GET'])
@user_required
def get_user_dashboard(current_user):
    """Get user dashboard data"""
    dashboard_data = {
        'user_stats': {
            'total_e_waste_items': EWaste.query.filter_by(user_id=current_user.id).count(),
            'pending_e_waste_items': EWaste.query.filter_by(user_id=current_user.id, status='pending').count(),
            'total_community_posts': CommunityPost.query.filter_by(user_id=current_user.id).count(),
            'total_feedback': Feedback.query.filter_by(user_id=current_user.id).count()
        },
        'recent_e_waste': [item.to_dict() for item in 
                          EWaste.query.filter_by(user_id=current_user.id)
                          .order_by(EWaste.created_at.desc()).limit(5).all()],
        'recent_posts': [post.to_dict() for post in 
                        CommunityPost.query.filter_by(user_id=current_user.id)
                        .order_by(CommunityPost.created_at.desc()).limit(5).all()],
        'profile': current_user.to_dict()
    }
    
    return jsonify(dashboard_data)