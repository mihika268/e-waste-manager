"""
Recycling Certificate Model

This module defines the database model for storing recycling certificates.

Author: Muskan Uttam
Created: 2025
"""

from app import db
from datetime import datetime

class RecyclingCertificate(db.Model):
    """Store generated certificates"""
    __tablename__ = 'recycling_certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('e_waste_item.id'))
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    issued_date = db.Column(db.DateTime, default=datetime.utcnow)
    pdf_path = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'certificate_number': self.certificate_number,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
            'pdf_path': self.pdf_path
        }

