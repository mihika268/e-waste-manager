"""
Referral System Model

This module handles user referrals and referral tracking.
Users can invite friends and earn points for successful referrals.

Author: Muskan Uttam
Created: 2025
"""

from app import db
from datetime import datetime
import secrets

class ReferralCode(db.Model):
    """Store user referral codes"""
    __tablename__ = 'referral_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    referrals = db.relationship('Referral', backref='referral_code', lazy=True)
    
    @staticmethod
    def generate_unique_code():
        """Generate a unique referral code"""
        while True:
            code = secrets.token_urlsafe(8).upper()[:8]
            if not ReferralCode.query.filter_by(code=code).first():
                return code
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'usage_count': Referral.query.filter_by(referral_code_id=self.id).count()
        }


class Referral(db.Model):
    """Track referral usage"""
    __tablename__ = 'referrals'
    
    id = db.Column(db.Integer, primary_key=True)
    referral_code_id = db.Column(db.Integer, db.ForeignKey('referral_codes.id'), nullable=False)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points_awarded = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'referral_code': self.referral_code.code if self.referral_code else None,
            'referee_id': self.referee_id,
            'points_awarded': self.points_awarded,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

