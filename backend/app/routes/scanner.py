from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.models.scanner import WasteScan, CarbonFootprint
from app.utils.waste_classifier import WasteClassifier

scanner_bp = Blueprint('scanner', __name__)

# Lazy-load waste classifier to avoid heavy startup cost
classifier = None

def get_classifier():
    global classifier
    if classifier is None:
        classifier = WasteClassifier()
    return classifier

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@scanner_bp.route('/scan', methods=['POST'])
@jwt_required()
def scan_waste():
    """Upload image and get AI waste classification"""
    try:
        user_id = get_jwt_identity()
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image.'}), 400
        
        # Create upload directory if it doesn't exist
        root_upload = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        upload_dir = os.path.join(root_upload, 'scans')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file
        filename = secure_filename(f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath_abs = os.path.join(upload_dir, filename)
        file.save(filepath_abs)
        # Relative path stored in DB for serving via /uploads/<path>
        filepath_rel = os.path.join('scans', filename).replace('\\', '/')
        
        # Classify waste using AI
        classification_result = get_classifier().classify_waste(filepath_abs)
        
        # Get optional weight from request
        weight_kg = float(request.form.get('weight', 1.0))
        
        # Calculate environmental impact
        impact = get_classifier().calculate_carbon_impact(classification_result['category'], weight_kg)
        
        # Save scan result to database
        waste_scan = WasteScan(
            user_id=user_id,
            image_path=filepath_rel,
            predicted_category=classification_result['category'],
            confidence_score=classification_result['confidence'],
            recommended_bin=classification_result['bin'],
            disposal_instructions=classification_result['instructions']
        )
        db.session.add(waste_scan)
        
        # Save carbon footprint data
        carbon_record = CarbonFootprint(
            user_id=user_id,
            item_type=classification_result['category'],
            weight_kg=weight_kg,
            carbon_saved_kg=impact['carbon_saved_kg'],
            energy_saved_kwh=impact['energy_saved_kwh'],
            water_saved_liters=impact['water_saved_liters']
        )
        db.session.add(carbon_record)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'scan_id': waste_scan.id,
            'classification': classification_result,
            'environmental_impact': impact,
            'weight_kg': weight_kg,
            'message': f'Item classified as {classification_result["category"]} with {classification_result["confidence"]:.1%} confidence'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500

# Alias to match README documentation
@scanner_bp.route('/classify', methods=['POST'])
@jwt_required()
def classify_waste():
    """Alias endpoint for uploading image and getting classification"""
    return scan_waste()

@scanner_bp.route('/scan/feedback', methods=['POST'])
@jwt_required()
def scan_feedback():
    """Provide feedback on scan accuracy"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        scan_id = data.get('scan_id')
        is_correct = data.get('is_correct')
        
        if not scan_id or is_correct is None:
            return jsonify({'error': 'Missing scan_id or is_correct'}), 400
        
        # Find and update scan record
        scan = WasteScan.query.filter_by(id=scan_id, user_id=user_id).first()
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        scan.is_correct = is_correct
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback recorded successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to record feedback: {str(e)}'}), 500

@scanner_bp.route('/scan/history', methods=['GET'])
@jwt_required()
def scan_history():
    """Get user's scan history"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        scans = WasteScan.query.filter_by(user_id=user_id)\
                              .order_by(WasteScan.scanned_at.desc())\
                              .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'scans': [scan.to_dict() for scan in scans.items],
            'total': scans.total,
            'pages': scans.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get scan history: {str(e)}'}), 500

@scanner_bp.route('/carbon-footprint', methods=['GET'])
@jwt_required()
def carbon_footprint():
    """Get user's carbon footprint statistics"""
    try:
        user_id = get_jwt_identity()
        
        # Get total carbon savings
        total_carbon = db.session.query(db.func.sum(CarbonFootprint.carbon_saved_kg))\
                                .filter_by(user_id=user_id).scalar() or 0
        
        total_energy = db.session.query(db.func.sum(CarbonFootprint.energy_saved_kwh))\
                                .filter_by(user_id=user_id).scalar() or 0
        
        total_water = db.session.query(db.func.sum(CarbonFootprint.water_saved_liters))\
                               .filter_by(user_id=user_id).scalar() or 0
        
        # Get breakdown by category
        category_breakdown = db.session.query(
            CarbonFootprint.item_type,
            db.func.sum(CarbonFootprint.carbon_saved_kg).label('carbon_saved'),
            db.func.sum(CarbonFootprint.weight_kg).label('total_weight'),
            db.func.count(CarbonFootprint.id).label('item_count')
        ).filter_by(user_id=user_id)\
         .group_by(CarbonFootprint.item_type)\
         .all()
        
        # Calculate equivalent impacts
        trees_equivalent = total_carbon / 22  # Average tree absorbs 22kg CO2/year
        car_miles_equivalent = total_carbon / 0.4  # Average car emits 0.4kg CO2/mile
        
        return jsonify({
            'success': True,
            'total_impact': {
                'carbon_saved_kg': float(total_carbon),
                'energy_saved_kwh': float(total_energy),
                'water_saved_liters': float(total_water),
                'trees_equivalent': float(trees_equivalent),
                'car_miles_equivalent': float(car_miles_equivalent)
            },
            'category_breakdown': [
                {
                    'category': row.item_type,
                    'carbon_saved_kg': float(row.carbon_saved),
                    'total_weight_kg': float(row.total_weight),
                    'item_count': row.item_count
                }
                for row in category_breakdown
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get carbon footprint: {str(e)}'}), 500
