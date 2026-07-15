"""
Certificates API Routes

This module handles API endpoints for generating and managing recycling certificates.

Author: Muskan Uttam
Created: 2025
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.recycling_certificate import RecyclingCertificate
from app.models.ewaste import EWasteItem
from app.models.user import User
from app.utils.certificate_generator import CertificateGenerator
import os
import io
from datetime import datetime

certificates_bp = Blueprint('certificates', __name__)


@certificates_bp.route('/generate/<int:item_id>', methods=['POST'])
@jwt_required()
def generate_certificate(item_id):
    """Generate a certificate for a specific item"""
    try:
        user_id = get_jwt_identity()
        
        # Get item
        item = EWasteItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Get user
        user = User.query.get(user_id)
        
        # Generate certificate
        cert_number = f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        file_path = os.path.join('backend', 'certificates', f"{cert_number}.pdf")
        
        pdf_content = CertificateGenerator.generate_certificate(user, item, file_path)
        
        # Save certificate record
        certificate = RecyclingCertificate(
            user_id=user_id,
            item_id=item_id,
            certificate_number=cert_number,
            pdf_path=file_path
        )
        db.session.add(certificate)
        db.session.commit()
        
        return jsonify({
            'message': 'Certificate generated successfully',
            'certificate': certificate.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@certificates_bp.route('/download/<int:certificate_id>', methods=['GET'])
@jwt_required()
def download_certificate(certificate_id):
    """Download a certificate PDF"""
    try:
        user_id = get_jwt_identity()
        certificate = RecyclingCertificate.query.filter_by(
            id=certificate_id, 
            user_id=user_id
        ).first()
        
        if not certificate:
            return jsonify({'error': 'Certificate not found'}), 404
        
        if not os.path.exists(certificate.pdf_path):
            return jsonify({'error': 'Certificate file not found'}), 404
        
        return send_file(
            certificate.pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"certificate_{certificate.certificate_number}.pdf"
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificates_bp.route('/list', methods=['GET'])
@jwt_required()
def list_certificates():
    """Get user's certificates"""
    try:
        user_id = get_jwt_identity()
        certificates = RecyclingCertificate.query.filter_by(
            user_id=user_id
        ).order_by(RecyclingCertificate.issued_date.desc()).all()
        
        return jsonify({
            'certificates': [c.to_dict() for c in certificates]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@certificates_bp.route('/summary', methods=['POST'])
@jwt_required()
def generate_summary_certificate():
    """Generate an annual summary certificate"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get filter parameters
        year = data.get('year', datetime.now().year)
        
        # Get user's items for the year
        user = User.query.get(user_id)
        items = EWasteItem.query.filter_by(user_id=user_id).filter(
            db.extract('year', EWasteItem.created_at) == year
        ).all()
        
        if not items:
            return jsonify({'error': 'No items found for this year'}), 404
        
        # Generate summary certificate
        pdf_content = CertificateGenerator.generate_summary_certificate(user, items, year)
        
        # Return PDF as download
        cert_number = f"SUMMARY-{year}"
        filename = f"certificate_{cert_number}.pdf"
        
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

