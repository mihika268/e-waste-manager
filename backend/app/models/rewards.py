"""
Rewards and Points System Model

This module handles the gamification aspects of the application:
- User points and achievements
- Badges and milestones
- Reward redemption system

Author: Muskan Uttam
Created: 2025
"""

from app import db
from datetime import datetime

class UserPoints(db.Model):
    """Track user points and reward history"""
    __tablename__ = 'user_points'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    total_earned = db.Column(db.Integer, default=0)
    total_redeemed = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('PointsTransaction', backref='points_account', lazy=True, cascade='all, delete-orphan')
    
    def add_points(self, amount, reason=''):
        """Add points to user account"""
        self.points += amount
        self.total_earned += amount
        self.last_updated = datetime.utcnow()
        
        # Create transaction record
        transaction = PointsTransaction(
            points_account_id=self.id,
            amount=amount,
            transaction_type='earned',
            reason=reason
        )
        db.session.add(transaction)
        return self
    
    def redeem_points(self, amount, reason=''):
        """Redeem points from user account"""
        if self.points < amount:
            return False, "Insufficient points"
        
        self.points -= amount
        self.total_redeemed += amount
        self.last_updated = datetime.utcnow()
        
        # Create transaction record
        transaction = PointsTransaction(
            points_account_id=self.id,
            amount=-amount,
            transaction_type='redeemed',
            reason=reason
        )
        db.session.add(transaction)
        return True, "Points redeemed successfully"
    
    def to_dict(self):
        return {
            'points': self.points,
            'total_earned': self.total_earned,
            'total_redeemed': self.total_redeemed,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class PointsTransaction(db.Model):
    """Track individual point transactions"""
    __tablename__ = 'points_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    points_account_id = db.Column(db.Integer, db.ForeignKey('user_points.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # earned, redeemed
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Badge(db.Model):
    """Badge definitions and user badge achievements"""
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    points_threshold = db.Column(db.Integer)  # Points needed to earn this badge
    condition_type = db.Column(db.String(50))  # points_total, items_registered, items_collected, etc.
    condition_value = db.Column(db.Integer)  # Value needed to meet condition
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    achievements = db.relationship('UserBadge', backref='badge', lazy=True)
    
    @staticmethod
    def check_and_award_badges(user_id, points, context=''):
        """Check if user qualifies for any badges and award them"""
        # Get user's points account
        points_account = UserPoints.query.filter_by(user_id=user_id).first()
        if not points_account:
            points_account = UserPoints(user_id=user_id)
            db.session.add(points_account)
            db.session.commit()
        
        # Get all badges
        badges = Badge.query.all()
        awarded_badges = []
        
        for badge in badges:
            # Check if user already has this badge
            if UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
                continue
            
            # Check if badge conditions are met
            qualifies = False
            
            if badge.condition_type == 'points_total':
                qualifies = points_account.total_earned >= badge.condition_value
            elif badge.condition_type == 'items_registered':
                from app.models.ewaste import EWasteItem
                count = EWasteItem.query.filter_by(user_id=user_id).count()
                qualifies = count >= badge.condition_value
            elif badge.condition_type == 'items_collected':
                from app.models.ewaste import Collection
                count = Collection.query.filter_by(user_id=user_id, status='collected').count()
                qualifies = count >= badge.condition_value
            
            if qualifies:
                # Award the badge
                user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
                db.session.add(user_badge)
                awarded_badges.append(badge.to_dict())
        
        db.session.commit()
        return awarded_badges
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'points_threshold': self.points_threshold,
            'condition_type': self.condition_type,
            'condition_value': self.condition_value
        }


class UserBadge(db.Model):
    """User badge achievements"""
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'badge': self.badge.to_dict() if self.badge else None,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None
        }


class Reward(db.Model):
    """Rewards that can be redeemed with points"""
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points_cost = db.Column(db.Integer, nullable=False)
    reward_type = db.Column(db.String(50))  # discount, free_item, cash_back, etc.
    value = db.Column(db.String(200))  # The actual reward value
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    redemptions = db.relationship('RewardRedemption', backref='reward', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'points_cost': self.points_cost,
            'reward_type': self.reward_type,
            'value': self.value,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


class RewardRedemption(db.Model):
    """Track reward redemptions"""
    __tablename__ = 'reward_redemptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('rewards.id'), nullable=False)
    points_spent = db.Column(db.Integer, nullable=False)
    redemption_code = db.Column(db.String(50), unique=True)  # Unique code for redemption
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reward': self.reward.to_dict() if self.reward else None,
            'points_spent': self.points_spent,
            'redemption_code': self.redemption_code,
            'redeemed_at': self.redeemed_at.isoformat() if self.redeemed_at else None,
            'is_used': self.is_used,
            'used_at': self.used_at.isoformat() if self.used_at else None
        }

