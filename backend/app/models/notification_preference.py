"""
Notification Preferences Model

This module handles user notification preferences for email and SMS alerts.

Author: Muskan Uttam
Created: 2025
"""

from app import db
from datetime import datetime

class NotificationPreference(db.Model):
    """Store user notification preferences"""
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Email preferences
    email_enabled = db.Column(db.Boolean, default=True)
    email_new_item = db.Column(db.Boolean, default=True)
    email_collection_scheduled = db.Column(db.Boolean, default=True)
    email_collection_reminder = db.Column(db.Boolean, default=True)
    email_collection_completed = db.Column(db.Boolean, default=True)
    email_points_earned = db.Column(db.Boolean, default=True)
    email_badge_earned = db.Column(db.Boolean, default=True)
    email_referral_bonus = db.Column(db.Boolean, default=True)
    
    # SMS preferences
    sms_enabled = db.Column(db.Boolean, default=False)
    sms_collection_reminder = db.Column(db.Boolean, default=True)
    sms_collection_completed = db.Column(db.Boolean, default=True)
    
    # Updated timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'email_enabled': self.email_enabled,
            'email_new_item': self.email_new_item,
            'email_collection_scheduled': self.email_collection_scheduled,
            'email_collection_reminder': self.email_collection_reminder,
            'email_collection_completed': self.email_collection_completed,
            'email_points_earned': self.email_points_earned,
            'email_badge_earned': self.email_badge_earned,
            'email_referral_bonus': self.email_referral_bonus,
            'sms_enabled': self.sms_enabled,
            'sms_collection_reminder': self.sms_collection_reminder,
            'sms_collection_completed': self.sms_collection_completed
        }

