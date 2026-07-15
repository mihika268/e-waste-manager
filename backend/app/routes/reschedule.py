"""
Pickup Rescheduling API Routes

This module handles API endpoints for rescheduling collection pickups.

Author: Muskan Uttam
Created: 2025
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.ewaste import Collection
from datetime import datetime

reschedule_bp = Blueprint('reschedule', __name__)


@reschedule_bp.route('/collections/<int:collection_id>/reschedule', methods=['POST'])
@jwt_required()
def reschedule_collection(collection_id):
    """Reschedule a collection pickup"""
    try:
        user_id = get_jwt_identity()
        
        # Get collection
        collection = Collection.query.filter_by(
            id=collection_id,
            user_id=user_id
        ).first()
        
        if not collection:
            return jsonify({'error': 'Collection not found'}), 404
        
        # Validate status
        if collection.status in ['completed', 'cancelled']:
            return jsonify({'error': 'Cannot reschedule completed or cancelled collections'}), 400
        
        # Get new date from request
        data = request.get_json()
        
        if not data.get('new_date'):
            return jsonify({'error': 'New collection date is required'}), 400
        
        try:
            new_date = datetime.fromisoformat(data['new_date'].replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Validate reschedule count (max 3 reschedules)
        if collection.reschedule_count >= 3:
            return jsonify({'error': 'Maximum reschedule limit reached'}), 400
        
        # Reschedule
        reason = data.get('reason', '')
        collection.reschedule(new_date, reason)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Collection rescheduled successfully',
            'collection': collection.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reschedule_bp.route('/collections/<int:collection_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_collection(collection_id):
    """Cancel a collection pickup"""
    try:
        user_id = get_jwt_identity()
        
        # Get collection
        collection = Collection.query.filter_by(
            id=collection_id,
            user_id=user_id
        ).first()
        
        if not collection:
            return jsonify({'error': 'Collection not found'}), 404
        
        # Validate status
        if collection.status == 'completed':
            return jsonify({'error': 'Cannot cancel completed collections'}), 400
        
        if collection.status == 'cancelled':
            return jsonify({'error': 'Collection already cancelled'}), 400
        
        # Cancel collection
        collection.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'message': 'Collection cancelled successfully',
            'collection': collection.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@reschedule_bp.route('/collections/<int:collection_id>/history', methods=['GET'])
@jwt_required()
def get_reschedule_history(collection_id):
    """Get reschedule history for a collection"""
    try:
        user_id = get_jwt_identity()
        
        # Get collection
        collection = Collection.query.filter_by(
            id=collection_id,
            user_id=user_id
        ).first()
        
        if not collection:
            return jsonify({'error': 'Collection not found'}), 404
        
        history = {
            'original_date': collection.original_collection_date.isoformat() if collection.original_collection_date else None,
            'current_date': collection.collection_date.isoformat() if collection.collection_date else None,
            'reschedule_count': collection.reschedule_count,
            'reschedule_reason': collection.reschedule_reason,
            'status': collection.status
        }
        
        return jsonify({'history': history}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

