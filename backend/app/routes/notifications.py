"""
Notification Preferences API Routes

This module handles API endpoints for managing user notification preferences.

Author: Muskan Uttam
Created: 2025
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.notification_preference import NotificationPreference

notification_bp = Blueprint('notifications', __name__)


@notification_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get user's notification preferences"""
    try:
        user_id = get_jwt_identity()
        
        preferences = NotificationPreference.query.filter_by(user_id=user_id).first()
        
        if not preferences:
            # Create default preferences
            preferences = NotificationPreference(user_id=user_id)
            db.session.add(preferences)
            db.session.commit()
        
        return jsonify(preferences.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notification_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update user's notification preferences"""
    try:
        user_id = get_jwt_identity()
        
        preferences = NotificationPreference.query.filter_by(user_id=user_id).first()
        
        if not preferences:
            preferences = NotificationPreference(user_id=user_id)
            db.session.add(preferences)
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'email_enabled', 'email_new_item', 'email_collection_scheduled',
            'email_collection_reminder', 'email_collection_completed',
            'email_points_earned', 'email_badge_earned', 'email_referral_bonus',
            'sms_enabled', 'sms_collection_reminder', 'sms_collection_completed'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(preferences, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Preferences updated successfully',
            'preferences': preferences.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

