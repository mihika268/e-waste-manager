from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.models.community import CommunityPost, PostComment, PostLike
from app.models.user import User

community_bp = Blueprint('community', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@community_bp.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    """Get community posts with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        post_type = request.args.get('type')
        search = request.args.get('search')
        
        query = CommunityPost.query
        
        # Filter by post type
        if post_type:
            query = query.filter_by(post_type=post_type)
        
        # Search in title and content
        if search:
            query = query.filter(
                db.or_(
                    CommunityPost.title.contains(search),
                    CommunityPost.content.contains(search),
                    CommunityPost.tags.contains(search)
                )
            )
        
        # Order by featured posts first, then by creation date
        posts = query.order_by(CommunityPost.is_featured.desc(), 
                              CommunityPost.created_at.desc())\
                     .paginate(page=page, per_page=per_page, error_out=False)
        
        # Get user data for each post
        posts_data = []
        for post in posts.items:
            post_dict = post.to_dict()
            user = User.query.get(post.user_id)
            if user:
                post_dict['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            posts_data.append(post_dict)
        
        return jsonify({
            'success': True,
            'posts': posts_data,
            'total': posts.total,
            'pages': posts.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get posts: {str(e)}'}), 500

@community_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """Create a new community post"""
    try:
        user_id = get_jwt_identity()
        
        # Handle form data
        title = request.form.get('title')
        content = request.form.get('content')
        post_type = request.form.get('post_type', 'general')
        tags = request.form.get('tags', '')
        
        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                root_upload = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                upload_dir = os.path.join(root_upload, 'community')
                os.makedirs(upload_dir, exist_ok=True)
                
                filename = secure_filename(f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                abs_path = os.path.join(upload_dir, filename)
                file.save(abs_path)
                image_path = os.path.join('community', filename).replace('\\', '/')
        
        # Create post
        post = CommunityPost(
            user_id=user_id,
            title=title,
            content=content,
            post_type=post_type,
            image_path=image_path,
            tags=tags
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'post': post.to_dict(),
            'message': 'Post created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create post: {str(e)}'}), 500

@community_bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    """Get a specific post with comments"""
    try:
        post = CommunityPost.query.get_or_404(post_id)
        
        # Get post data with user info
        post_dict = post.to_dict()
        user = User.query.get(post.user_id)
        if user:
            post_dict['user'] = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        
        # Get comments with user info
        comments = PostComment.query.filter_by(post_id=post_id)\
                                   .order_by(PostComment.created_at.asc()).all()
        
        comments_data = []
        for comment in comments:
            comment_dict = comment.to_dict()
            comment_user = User.query.get(comment.user_id)
            if comment_user:
                comment_dict['user'] = {
                    'id': comment_user.id,
                    'username': comment_user.username,
                    'first_name': comment_user.first_name,
                    'last_name': comment_user.last_name
                }
            comments_data.append(comment_dict)
        
        post_dict['comments'] = comments_data
        
        return jsonify({
            'success': True,
            'post': post_dict
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get post: {str(e)}'}), 500

@community_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def toggle_like(post_id):
    """Toggle like on a post"""
    try:
        user_id = get_jwt_identity()
        
        # Check if post exists
        post = CommunityPost.query.get_or_404(post_id)
        
        # Check if user already liked this post
        existing_like = PostLike.query.filter_by(post_id=post_id, user_id=user_id).first()
        
        if existing_like:
            # Unlike the post
            db.session.delete(existing_like)
            post.likes_count = max(0, post.likes_count - 1)
            liked = False
        else:
            # Like the post
            new_like = PostLike(post_id=post_id, user_id=user_id)
            db.session.add(new_like)
            post.likes_count += 1
            liked = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'liked': liked,
            'likes_count': post.likes_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to toggle like: {str(e)}'}), 500

@community_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    """Add a comment to a post"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        content = data.get('content')
        if not content:
            return jsonify({'error': 'Comment content is required'}), 400
        
        # Check if post exists
        post = CommunityPost.query.get_or_404(post_id)
        
        # Create comment
        comment = PostComment(
            post_id=post_id,
            user_id=user_id,
            content=content
        )
        
        db.session.add(comment)
        post.comments_count += 1
        db.session.commit()
        
        # Get comment with user info
        comment_dict = comment.to_dict()
        user = User.query.get(user_id)
        if user:
            comment_dict['user'] = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        
        return jsonify({
            'success': True,
            'comment': comment_dict,
            'message': 'Comment added successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add comment: {str(e)}'}), 500

@community_bp.route('/posts/types', methods=['GET'])
@jwt_required()
def get_post_types():
    """Get available post types"""
    return jsonify({
        'success': True,
        'post_types': [
            {'value': 'eco-hack', 'label': 'Eco Hack', 'icon': '💡'},
            {'value': 'diy-craft', 'label': 'DIY Craft', 'icon': '🎨'},
            {'value': 'cleanup', 'label': 'Cleanup Story', 'icon': '🧹'},
            {'value': 'tip', 'label': 'Green Tip', 'icon': '🌱'},
            {'value': 'general', 'label': 'General', 'icon': '💬'}
        ]
    })

@community_bp.route('/posts/featured', methods=['GET'])
@jwt_required()
def get_featured_posts():
    """Get featured community posts"""
    try:
        posts = CommunityPost.query.filter_by(is_featured=True)\
                                  .order_by(CommunityPost.created_at.desc())\
                                  .limit(5).all()
        
        posts_data = []
        for post in posts:
            post_dict = post.to_dict()
            user = User.query.get(post.user_id)
            if user:
                post_dict['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            posts_data.append(post_dict)
        
        return jsonify({
            'success': True,
            'featured_posts': posts_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get featured posts: {str(e)}'}), 500
