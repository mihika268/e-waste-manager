from app import db
from datetime import datetime

class Complaint(db.Model):
    """Model for complaints and feedback"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_type = db.Column(db.String(100), nullable=False)  # missed_pickup, overflowing_bin, service_issue, other
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(500))
    image_path = db.Column(db.String(255))
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(50), default='open')  # open, in_progress, resolved, closed
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin/collector assigned
    resolution_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if hasattr(self, 'user') else None,
            'complaint_type': self.complaint_type,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'image_path': self.image_path,
            'priority': self.priority,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'resolution_notes': self.resolution_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

class Feedback(db.Model):
    """Model for general feedback and suggestions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feedback_type = db.Column(db.String(50), nullable=False)  # suggestion, compliment, general
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 star rating
    is_anonymous = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='new')  # new, reviewed, implemented
    admin_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id if not self.is_anonymous else None,
            'user': self.user.to_dict() if hasattr(self, 'user') and not self.is_anonymous else None,
            'feedback_type': self.feedback_type,
            'subject': self.subject,
            'message': self.message,
            'rating': self.rating,
            'is_anonymous': self.is_anonymous,
            'status': self.status,
            'admin_response': self.admin_response,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
