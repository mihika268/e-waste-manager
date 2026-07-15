from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.ewaste import EWasteItem, EWasteCategory, Collection
from app.models.rewards import UserPoints, Badge
from datetime import datetime

ewaste_bp = Blueprint('ewaste', __name__)

@ewaste_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all e-waste categories"""
    try:
        categories = EWasteCategory.query.all()
        return jsonify({'categories': [cat.to_dict() for cat in categories]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ewaste_bp.route('/items', methods=['GET'])
@jwt_required()
def get_items():
    """Get user's e-waste items"""
    try:
        user_id = get_jwt_identity()
        items = EWasteItem.query.filter_by(user_id=user_id).all()
        return jsonify({'items': [item.to_dict() for item in items]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ewaste_bp.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    """Create a new e-waste item"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if category exists
        category = EWasteCategory.query.get(data['category_id'])
        if not category:
            return jsonify({'error': 'Invalid category'}), 400
        
        # Create new item
        item = EWasteItem(
            name=data['name'],
            brand=data.get('brand', ''),
            model=data.get('model', ''),
            serial_number=data.get('serial_number', ''),
            condition=data.get('condition', 'working'),
            weight=data.get('weight', 0.0),
            description=data.get('description', ''),
            estimated_value=data.get('estimated_value', 0.0),
            user_id=user_id,
            category_id=data['category_id']
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Award points for registering an item
        points_account = UserPoints.query.filter_by(user_id=user_id).first()
        if not points_account:
            points_account = UserPoints(user_id=user_id)
            db.session.add(points_account)
        
        # Award 10 points for registering an item
        points_account.add_points(10, f'Registered item: {item.name}')
        
        # Check for badge achievements
        Badge.check_and_award_badges(user_id, points_account.points, 'item_registered')
        
        db.session.commit()
        
        return jsonify({
            'message': 'E-waste item created successfully',
            'item': item.to_dict(),
            'points_awarded': 10
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ewaste_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    """Update an e-waste item"""
    try:
        user_id = get_jwt_identity()
        item = EWasteItem.query.filter_by(id=item_id, user_id=user_id).first()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['name', 'brand', 'model', 'serial_number', 'condition', 
                         'weight', 'description', 'estimated_value', 'status']
        for field in allowed_fields:
            if field in data:
                setattr(item, field, data[field])
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Item updated successfully',
            'item': item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ewaste_bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    """Delete an e-waste item"""
    try:
        user_id = get_jwt_identity()
        item = EWasteItem.query.filter_by(id=item_id, user_id=user_id).first()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': 'Item deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ewaste_bp.route('/collections', methods=['GET'])
@jwt_required()
def get_collections():
    """Get user's collections"""
    try:
        user_id = get_jwt_identity()
        collections = Collection.query.filter_by(user_id=user_id).all()
        return jsonify({'collections': [col.to_dict() for col in collections]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ewaste_bp.route('/collections', methods=['POST'])
@jwt_required()
def schedule_collection():
    """Schedule a collection for an e-waste item"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['ewaste_item_id', 'collection_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if item exists and belongs to user
        item = EWasteItem.query.filter_by(id=data['ewaste_item_id'], user_id=user_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Parse collection date
        try:
            collection_date = datetime.fromisoformat(data['collection_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Create collection
        collection = Collection(
            collection_date=collection_date,
            notes=data.get('notes', ''),
            collector_name=data.get('collector_name', ''),
            collector_phone=data.get('collector_phone', ''),
            user_id=user_id,
            ewaste_item_id=data['ewaste_item_id']
        )
        
        db.session.add(collection)
        db.session.commit()
        
        return jsonify({
            'message': 'Collection scheduled successfully',
            'collection': collection.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ewaste_bp.route('/collections/<int:collection_id>', methods=['PUT'])
@jwt_required()
def update_collection(collection_id):
    """Update a collection (e.g., cancel it)"""
    try:
        user_id = get_jwt_identity()
        collection = Collection.query.filter_by(id=collection_id, user_id=user_id).first()
        
        if not collection:
            return jsonify({'error': 'Collection not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['status', 'notes', 'collector_name', 'collector_phone']
        for field in allowed_fields:
            if field in data:
                setattr(collection, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Collection updated successfully',
            'collection': collection.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
