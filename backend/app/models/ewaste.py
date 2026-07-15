from app import db
from datetime import datetime

class EWasteCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    recycling_fee = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('EWasteItem', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'recycling_fee': self.recycling_fee,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EWasteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    serial_number = db.Column(db.String(100))
    condition = db.Column(db.String(20))  # working, broken, partially_working
    weight = db.Column(db.Float)  # in kg
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='registered')  # registered, collected, processed, recycled
    estimated_value = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('e_waste_category.id'), nullable=False)
    
    # Relationships
    collections = db.relationship('Collection', backref='ewaste_item', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'serial_number': self.serial_number,
            'condition': self.condition,
            'weight': self.weight,
            'description': self.description,
            'status': self.status,
            'estimated_value': self.estimated_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None
        }

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_date = db.Column(db.DateTime, nullable=False)
    original_collection_date = db.Column(db.DateTime)  # Track original date before rescheduling
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled, rescheduled
    notes = db.Column(db.Text)
    reschedule_reason = db.Column(db.Text)  # Reason for rescheduling
    reschedule_count = db.Column(db.Integer, default=0)  # Track number of reschedules
    collector_name = db.Column(db.String(100))
    collector_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ewaste_item_id = db.Column(db.Integer, db.ForeignKey('e_waste_item.id'), nullable=False)
    
    def reschedule(self, new_date, reason=''):
        """Reschedule the collection"""
        if not self.original_collection_date:
            self.original_collection_date = self.collection_date
        
        self.collection_date = new_date
        self.status = 'rescheduled'
        self.reschedule_count += 1
        self.reschedule_reason = reason or self.reschedule_reason
        return self

    def to_dict(self):
        return {
            'id': self.id,
            'collection_date': self.collection_date.isoformat() if self.collection_date else None,
            'original_collection_date': self.original_collection_date.isoformat() if self.original_collection_date else None,
            'status': self.status,
            'notes': self.notes,
            'reschedule_reason': self.reschedule_reason,
            'reschedule_count': self.reschedule_count,
            'collector_name': self.collector_name,
            'collector_phone': self.collector_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id,
            'ewaste_item_id': self.ewaste_item_id
        }
