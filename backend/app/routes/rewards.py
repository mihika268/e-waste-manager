"""
Rewards and Points API Routes

This module handles all API endpoints related to:
- Points management
- Badge achievements
- Reward redemption
- Leaderboards

Author: Muskan Uttam
Created: 2025
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.rewards import UserPoints, Badge, UserBadge, Reward, RewardRedemption, PointsTransaction
from app.models.user import User
import secrets

rewards_bp = Blueprint('rewards', __name__)


@rewards_bp.route('/points', methods=['GET'])
@jwt_required()
def get_user_points():
    """Get current user's points balance"""
    try:
        user_id = get_jwt_identity()
        points_account = UserPoints.query.filter_by(user_id=user_id).first()
        
        if not points_account:
            # Initialize points account if it doesn't exist
            points_account = UserPoints(user_id=user_id)
            db.session.add(points_account)
            db.session.commit()
        
        return jsonify(points_account.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/points/transactions', methods=['GET'])
@jwt_required()
def get_points_transactions():
    """Get user's points transaction history"""
    try:
        user_id = get_jwt_identity()
        points_account = UserPoints.query.filter_by(user_id=user_id).first()
        
        if not points_account:
            return jsonify({'transactions': []}), 200
        
        transactions = PointsTransaction.query.filter_by(
            points_account_id=points_account.id
        ).order_by(PointsTransaction.created_at.desc()).limit(50).all()
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/badges', methods=['GET'])
@jwt_required()
def get_user_badges():
    """Get user's earned badges"""
    try:
        user_id = get_jwt_identity()
        user_badges = UserBadge.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'badges': [ub.to_dict() for ub in user_badges]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/badges/available', methods=['GET'])
@jwt_required()
def get_available_badges():
    """Get all available badges"""
    try:
        badges = Badge.query.all()
        
        return jsonify({
            'badges': [b.to_dict() for b in badges]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/rewards', methods=['GET'])
@jwt_required()
def get_available_rewards():
    """Get all available rewards"""
    try:
        rewards = Reward.query.filter_by(is_active=True).all()
        
        return jsonify({
            'rewards': [r.to_dict() for r in rewards]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/rewards/<int:reward_id>/redeem', methods=['POST'])
@jwt_required()
def redeem_reward(reward_id):
    """Redeem a reward"""
    try:
        user_id = get_jwt_identity()
        
        # Get reward
        reward = Reward.query.get(reward_id)
        if not reward or not reward.is_active:
            return jsonify({'error': 'Reward not found or inactive'}), 404
        
        # Get user's points account
        points_account = UserPoints.query.filter_by(user_id=user_id).first()
        if not points_account:
            points_account = UserPoints(user_id=user_id)
            db.session.add(points_account)
            db.session.commit()
        
        # Check if user has enough points
        if points_account.points < reward.points_cost:
            return jsonify({'error': 'Insufficient points'}), 400
        
        # Generate unique redemption code
        redemption_code = secrets.token_urlsafe(16)
        
        # Create redemption record
        redemption = RewardRedemption(
            user_id=user_id,
            reward_id=reward_id,
            points_spent=reward.points_cost,
            redemption_code=redemption_code
        )
        
        # Redeem points
        success, message = points_account.redeem_points(reward.points_cost, f'Redeemed: {reward.name}')
        
        if not success:
            return jsonify({'error': message}), 400
        
        db.session.add(redemption)
        db.session.commit()
        
        return jsonify({
            'message': 'Reward redeemed successfully',
            'redemption': redemption.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/redemptions', methods=['GET'])
@jwt_required()
def get_user_redemptions():
    """Get user's redemption history"""
    try:
        user_id = get_jwt_identity()
        redemptions = RewardRedemption.query.filter_by(user_id=user_id).order_by(
            RewardRedemption.redeemed_at.desc()
        ).all()
        
        return jsonify({
            'redemptions': [r.to_dict() for r in redemptions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get global leaderboard"""
    try:
        top_users = UserPoints.query.order_by(
            UserPoints.points.desc()
        ).limit(100).all()
        
        leaderboard = []
        for rank, points_account in enumerate(top_users, start=1):
            user = User.query.get(points_account.user_id)
            if user:
                leaderboard.append({
                    'rank': rank,
                    'username': user.username,
                    'points': points_account.points,
                    'total_earned': points_account.total_earned
                })
        
        return jsonify({'leaderboard': leaderboard}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rewards_bp.route('/leaderboard/my-rank', methods=['GET'])
@jwt_required()
def get_my_rank():
    """Get current user's rank"""
    try:
        user_id = get_jwt_identity()
        points_account = UserPoints.query.filter_by(user_id=user_id).first()
        
        if not points_account:
            return jsonify({'rank': None, 'message': 'No points yet'}), 200
        
        # Count users with more points
        rank = UserPoints.query.filter(
            UserPoints.points > points_account.points
        ).count() + 1
        
        return jsonify({
            'rank': rank,
            'points': points_account.points
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

