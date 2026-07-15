"""
Referral System API Routes

This module handles API endpoints for:
- Creating and managing referral codes
- Applying referral codes during registration
- Tracking referral history and rewards

Author: Muskan Uttam
Created: 2025
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.referral import ReferralCode, Referral
from app.models.rewards import UserPoints
from app.models.user import User

referral_bp = Blueprint('referral', __name__)


@referral_bp.route('/code', methods=['GET'])
@jwt_required()
def get_referral_code():
    """Get or create user's referral code"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user has a referral code
        referral_code = ReferralCode.query.filter_by(user_id=user_id).first()
        
        if not referral_code:
            # Create new referral code
            code = ReferralCode.generate_unique_code()
            referral_code = ReferralCode(user_id=user_id, code=code)
            db.session.add(referral_code)
            db.session.commit()
        
        return jsonify(referral_code.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@referral_bp.route('/code', methods=['POST'])
@jwt_required()
def regenerate_referral_code():
    """Regenerate user's referral code"""
    try:
        user_id = get_jwt_identity()
        
        # Deactivate old code
        old_code = ReferralCode.query.filter_by(user_id=user_id).first()
        if old_code:
            old_code.is_active = False
        
        # Create new referral code
        code = ReferralCode.generate_unique_code()
        referral_code = ReferralCode(user_id=user_id, code=code)
        db.session.add(referral_code)
        db.session.commit()
        
        return jsonify({
            'message': 'Referral code regenerated successfully',
            'code': referral_code.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@referral_bp.route('/history', methods=['GET'])
@jwt_required()
def get_referral_history():
    """Get user's referral history"""
    try:
        user_id = get_jwt_identity()
        
        # Get referrals where user is the referrer
        referrals = Referral.query.filter_by(referrer_id=user_id).order_by(
            Referral.created_at.desc()
        ).all()
        
        return jsonify({
            'referrals': [r.to_dict() for r in referrals],
            'total_referrals': len(referrals),
            'total_points': sum(r.points_awarded for r in referrals)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@referral_bp.route('/validate/<code>', methods=['GET'])
def validate_referral_code(code):
    """Validate a referral code (public endpoint)"""
    try:
        referral_code = ReferralCode.query.filter_by(code=code, is_active=True).first()
        
        if not referral_code:
            return jsonify({
                'valid': False,
                'message': 'Invalid referral code'
            }), 404
        
        return jsonify({
            'valid': True,
            'message': 'Valid referral code'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@referral_bp.route('/apply/<code>', methods=['POST'])
@jwt_required()
def apply_referral_code(code):
    """Apply a referral code to reward both referrer and referee"""
    try:
        user_id = get_jwt_identity()
        
        # Validate referral code
        referral_code = ReferralCode.query.filter_by(code=code, is_active=True).first()
        if not referral_code:
            return jsonify({'error': 'Invalid referral code'}), 400
        
        # Check if user is trying to use their own code
        if referral_code.user_id == user_id:
            return jsonify({'error': 'Cannot use your own referral code'}), 400
        
        # Check if user has already used this code
        existing_referral = Referral.query.filter_by(
            referee_id=user_id,
            referral_code_id=referral_code.id
        ).first()
        
        if existing_referral:
            return jsonify({'error': 'Referral code already used'}), 400
        
        # Award points to referee (new user)
        referee_points = UserPoints.query.filter_by(user_id=user_id).first()
        if not referee_points:
            referee_points = UserPoints(user_id=user_id)
            db.session.add(referee_points)
        
        referee_points.add_points(25, f'Applied referral code: {code}')
        
        # Award points to referrer
        referrer_points = UserPoints.query.filter_by(user_id=referral_code.user_id).first()
        if not referrer_points:
            referrer_points = UserPoints(user_id=referral_code.user_id)
            db.session.add(referrer_points)
        
        referrer_points.add_points(50, f'Referral used by user #{user_id}')
        
        # Create referral record
        referral = Referral(
            referral_code_id=referral_code.id,
            referrer_id=referral_code.user_id,
            referee_id=user_id,
            points_awarded=50
        )
        db.session.add(referral)
        db.session.commit()
        
        return jsonify({
            'message': 'Referral code applied successfully',
            'points_awarded': 25,
            'referral': referral.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@referral_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_referral_stats():
    """Get referral statistics for current user"""
    try:
        user_id = get_jwt_identity()
        
        # Get referral code
        referral_code = ReferralCode.query.filter_by(user_id=user_id).first()
        
        if not referral_code:
            return jsonify({
                'total_referrals': 0,
                'total_points': 0,
                'code': None
            }), 200
        
        # Get referrals
        referrals = Referral.query.filter_by(referrer_id=user_id).all()
        
        return jsonify({
            'total_referrals': len(referrals),
            'total_points': sum(r.points_awarded for r in referrals),
            'code': referral_code.code,
            'usage_count': len(referrals)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

