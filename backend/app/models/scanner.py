from app import db
from datetime import datetime

class WasteScan(db.Model):
    """Model for AI waste scanner results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    predicted_category = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    recommended_bin = db.Column(db.String(100), nullable=False)
    disposal_instructions = db.Column(db.Text)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_correct = db.Column(db.Boolean)  # User feedback on prediction accuracy
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'predicted_category': self.predicted_category,
            'confidence_score': self.confidence_score,
            'recommended_bin': self.recommended_bin,
            'disposal_instructions': self.disposal_instructions,
            'scanned_at': self.scanned_at.isoformat() if self.scanned_at else None,
            'is_correct': self.is_correct
        }

class CarbonFootprint(db.Model):
    """Model for tracking carbon footprint reduction"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_type = db.Column(db.String(100), nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    carbon_saved_kg = db.Column(db.Float, nullable=False)  # CO2 equivalent saved
    energy_saved_kwh = db.Column(db.Float, default=0)
    water_saved_liters = db.Column(db.Float, default=0)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_type': self.item_type,
            'weight_kg': self.weight_kg,
            'carbon_saved_kg': self.carbon_saved_kg,
            'energy_saved_kwh': self.energy_saved_kwh,
            'water_saved_liters': self.water_saved_liters,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }
