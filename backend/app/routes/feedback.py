from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from app import db
from app.models.feedback import Complaint, Feedback
from app.models.user import User

feedback_bp = Blueprint('feedback', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@feedback_bp.route('/complaints', methods=['POST'])
@jwt_required()
def create_complaint():
    """Create a new complaint"""
    try:
        user_id = get_jwt_identity()
        
        # Handle form data
        complaint_type = request.form.get('complaint_type')
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location', '')
        priority = request.form.get('priority', 'medium')
        
        if not all([complaint_type, title, description]):
            return jsonify({'error': 'Complaint type, title, and description are required'}), 400
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                root_upload = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                upload_dir = os.path.join(root_upload, 'complaints')
                os.makedirs(upload_dir, exist_ok=True)
                
                filename = secure_filename(f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                abs_path = os.path.join(upload_dir, filename)
                file.save(abs_path)
                image_path = os.path.join('complaints', filename).replace('\\', '/')
        
        # Create complaint
        complaint = Complaint(
            user_id=user_id,
            complaint_type=complaint_type,
            title=title,
            description=description,
            location=location,
            image_path=image_path,
            priority=priority
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'complaint': complaint.to_dict(),
            'message': 'Complaint submitted successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create complaint: {str(e)}'}), 500

@feedback_bp.route('/complaints', methods=['GET'])
@jwt_required()
def get_complaints():
    """Get complaints (user's own or all for admin)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        complaint_type = request.args.get('type')
        
        # Build query
        if user.role == 'admin':
            # Admin can see all complaints
            query = Complaint.query
        else:
            # Regular users can only see their own complaints
            query = Complaint.query.filter_by(user_id=user_id)
        
        # Apply filters
        if status:
            query = query.filter_by(status=status)
        if complaint_type:
            query = query.filter_by(complaint_type=complaint_type)
        
        # Paginate results
        complaints = query.order_by(Complaint.created_at.desc())\
                         .paginate(page=page, per_page=per_page, error_out=False)
        
        # Get complaints with user data
        complaints_data = []
        for complaint in complaints.items:
            complaint_dict = complaint.to_dict()
            if user.role == 'admin':
                complaint_user = User.query.get(complaint.user_id)
                if complaint_user:
                    complaint_dict['user'] = {
                        'id': complaint_user.id,
                        'username': complaint_user.username,
                        'first_name': complaint_user.first_name,
                        'last_name': complaint_user.last_name,
                        'email': complaint_user.email
                    }
            complaints_data.append(complaint_dict)
        
        return jsonify({
            'success': True,
            'complaints': complaints_data,
            'total': complaints.total,
            'pages': complaints.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get complaints: {str(e)}'}), 500

@feedback_bp.route('/complaints/<int:complaint_id>', methods=['GET'])
@jwt_required()
def get_complaint(complaint_id):
    """Get a specific complaint"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        complaint = Complaint.query.get_or_404(complaint_id)
        
        # Check permissions
        if user.role != 'admin' and complaint.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        complaint_dict = complaint.to_dict()
        
        # Add user info for admin
        if user.role == 'admin':
            complaint_user = User.query.get(complaint.user_id)
            if complaint_user:
                complaint_dict['user'] = {
                    'id': complaint_user.id,
                    'username': complaint_user.username,
                    'first_name': complaint_user.first_name,
                    'last_name': complaint_user.last_name,
                    'email': complaint_user.email,
                    'phone': complaint_user.phone
                }
        
        return jsonify({
            'success': True,
            'complaint': complaint_dict
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get complaint: {str(e)}'}), 500

@feedback_bp.route('/complaints/<int:complaint_id>', methods=['PUT'])
@jwt_required()
def update_complaint(complaint_id):
    """Update complaint status (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        complaint = Complaint.query.get_or_404(complaint_id)
        data = request.get_json()
        
        # Update fields
        if 'status' in data:
            complaint.status = data['status']
            if data['status'] == 'resolved':
                complaint.resolved_at = datetime.utcnow()
        
        if 'assigned_to' in data:
            complaint.assigned_to = data['assigned_to']
        
        if 'resolution_notes' in data:
            complaint.resolution_notes = data['resolution_notes']
        
        if 'priority' in data:
            complaint.priority = data['priority']
        
        complaint.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'complaint': complaint.to_dict(),
            'message': 'Complaint updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update complaint: {str(e)}'}), 500

@feedback_bp.route('/feedback', methods=['POST'])
@jwt_required()
def create_feedback():
    """Create general feedback"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        feedback_type = data.get('feedback_type')
        subject = data.get('subject')
        message = data.get('message')
        rating = data.get('rating')
        is_anonymous = data.get('is_anonymous', False)
        
        if not all([feedback_type, subject, message]):
            return jsonify({'error': 'Feedback type, subject, and message are required'}), 400
        
        # Create feedback
        feedback = Feedback(
            user_id=user_id,
            feedback_type=feedback_type,
            subject=subject,
            message=message,
            rating=rating,
            is_anonymous=is_anonymous
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'feedback': feedback.to_dict(),
            'message': 'Feedback submitted successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create feedback: {str(e)}'}), 500

@feedback_bp.route('/feedback', methods=['GET'])
@jwt_required()
def get_feedback():
    """Get feedback (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        feedback_type = request.args.get('type')
        status = request.args.get('status')
        
        query = Feedback.query
        
        if feedback_type:
            query = query.filter_by(feedback_type=feedback_type)
        if status:
            query = query.filter_by(status=status)
        
        feedback_items = query.order_by(Feedback.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
        
        # Get feedback with user data (if not anonymous)
        feedback_data = []
        for feedback in feedback_items.items:
            feedback_dict = feedback.to_dict()
            if not feedback.is_anonymous:
                feedback_user = User.query.get(feedback.user_id)
                if feedback_user:
                    feedback_dict['user'] = {
                        'id': feedback_user.id,
                        'username': feedback_user.username,
                        'first_name': feedback_user.first_name,
                        'last_name': feedback_user.last_name,
                        'email': feedback_user.email
                    }
            feedback_data.append(feedback_dict)
        
        return jsonify({
            'success': True,
            'feedback': feedback_data,
            'total': feedback_items.total,
            'pages': feedback_items.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get feedback: {str(e)}'}), 500

@feedback_bp.route('/complaint-types', methods=['GET'])
@jwt_required()
def get_complaint_types():
    """Get available complaint types"""
    return jsonify({
        'success': True,
        'complaint_types': [
            {'value': 'missed_pickup', 'label': 'Missed Pickup', 'icon': '📅'},
            {'value': 'overflowing_bin', 'label': 'Overflowing Bin', 'icon': '🗑️'},
            {'value': 'damaged_bin', 'label': 'Damaged Bin', 'icon': '🔧'},
            {'value': 'service_delay', 'label': 'Service Delay', 'icon': '⏰'},
            {'value': 'poor_service', 'label': 'Poor Service Quality', 'icon': '👎'},
            {'value': 'billing_issue', 'label': 'Billing Issue', 'icon': '💳'},
            {'value': 'safety_concern', 'label': 'Safety Concern', 'icon': '⚠️'},
            {'value': 'other', 'label': 'Other', 'icon': '❓'}
        ]
    })

@feedback_bp.route('/feedback-types', methods=['GET'])
@jwt_required()
def get_feedback_types():
    """Get available feedback types"""
    return jsonify({
        'success': True,
        'feedback_types': [
            {'value': 'suggestion', 'label': 'Suggestion', 'icon': '💡'},
            {'value': 'compliment', 'label': 'Compliment', 'icon': '👍'},
            {'value': 'general', 'label': 'General Feedback', 'icon': '💬'},
            {'value': 'feature_request', 'label': 'Feature Request', 'icon': '🚀'},
            {'value': 'bug_report', 'label': 'Bug Report', 'icon': '🐛'}
        ]
    })

@feedback_bp.route('/complaints/stats', methods=['GET'])
@jwt_required()
def get_complaint_stats():
    """Get complaint statistics (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Status breakdown
        status_stats = db.session.query(
            Complaint.status,
            db.func.count(Complaint.id).label('count')
        ).group_by(Complaint.status).all()
        
        # Type breakdown
        type_stats = db.session.query(
            Complaint.complaint_type,
            db.func.count(Complaint.id).label('count')
        ).group_by(Complaint.complaint_type).all()
        
        # Priority breakdown
        priority_stats = db.session.query(
            Complaint.priority,
            db.func.count(Complaint.id).label('count')
        ).group_by(Complaint.priority).all()
        
        # Recent complaints (last 7 days)
        recent_date = datetime.utcnow() - timedelta(days=7)
        recent_complaints = Complaint.query.filter(
            Complaint.created_at >= recent_date
        ).count()
        
        # Average resolution time
        resolved_complaints = Complaint.query.filter(
            Complaint.status == 'resolved',
            Complaint.resolved_at.isnot(None)
        ).all()
        
        if resolved_complaints:
            total_resolution_time = sum(
                (complaint.resolved_at - complaint.created_at).total_seconds()
                for complaint in resolved_complaints
            )
            avg_resolution_hours = (total_resolution_time / len(resolved_complaints)) / 3600
        else:
            avg_resolution_hours = 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_complaints': Complaint.query.count(),
                'recent_complaints': recent_complaints,
                'avg_resolution_hours': avg_resolution_hours,
                'status_breakdown': [
                    {'status': row.status, 'count': row.count}
                    for row in status_stats
                ],
                'type_breakdown': [
                    {'type': row.complaint_type, 'count': row.count}
                    for row in type_stats
                ],
                'priority_breakdown': [
                    {'priority': row.priority, 'count': row.count}
                    for row in priority_stats
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get complaint stats: {str(e)}'}), 500
