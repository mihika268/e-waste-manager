from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.ewaste import EWasteItem, Collection, EWasteCategory
from app.models.scanner import WasteScan, CarbonFootprint
from app.models.community import CommunityPost
from app.models.feedback import Complaint
from app.models.user import User
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        
        # Date range for analytics
        end_date = datetime.utcnow()
        start_date_30d = end_date - timedelta(days=30)
        start_date_7d = end_date - timedelta(days=7)
        
        # User's personal stats
        user_stats = {
            'total_items': EWasteItem.query.filter_by(user_id=user_id).count(),
            'pending_collections': Collection.query.filter_by(user_id=user_id, status='pending').count(),
            'completed_collections': Collection.query.filter_by(user_id=user_id, status='completed').count(),
            'scans_performed': WasteScan.query.filter_by(user_id=user_id).count(),
            'community_posts': CommunityPost.query.filter_by(user_id=user_id).count()
        }
        
        # Carbon footprint stats
        carbon_stats = db.session.query(
            db.func.sum(CarbonFootprint.carbon_saved_kg).label('total_carbon'),
            db.func.sum(CarbonFootprint.energy_saved_kwh).label('total_energy'),
            db.func.sum(CarbonFootprint.water_saved_liters).label('total_water')
        ).filter_by(user_id=user_id).first()
        
        user_stats['carbon_impact'] = {
            'carbon_saved_kg': float(carbon_stats.total_carbon or 0),
            'energy_saved_kwh': float(carbon_stats.total_energy or 0),
            'water_saved_liters': float(carbon_stats.total_water or 0)
        }
        
        # Recent activity (last 7 days)
        recent_items = EWasteItem.query.filter(
            EWasteItem.user_id == user_id,
            EWasteItem.created_at >= start_date_7d
        ).count()
        
        recent_scans = WasteScan.query.filter(
            WasteScan.user_id == user_id,
            WasteScan.scanned_at >= start_date_7d
        ).count()
        
        user_stats['recent_activity'] = {
            'items_added': recent_items,
            'scans_performed': recent_scans
        }
        
        # Category breakdown for user's items
        category_breakdown = db.session.query(
            EWasteCategory.name.label('category'),
            db.func.count(EWasteItem.id).label('count'),
            db.func.sum(EWasteItem.estimated_value).label('total_value')
        ).join(EWasteCategory, EWasteItem.category_id == EWasteCategory.id)\
         .filter(EWasteItem.user_id == user_id)\
         .group_by(EWasteCategory.name)\
         .all()
        
        user_stats['category_breakdown'] = [
            {
                'category': row.category,
                'count': row.count,
                'total_value': float(row.total_value or 0)
            }
            for row in category_breakdown
        ]
        
        # Monthly trends (last 6 months)
        monthly_trends = []
        for i in range(6):
            month_start = (end_date.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            items_count = EWasteItem.query.filter(
                EWasteItem.user_id == user_id,
                EWasteItem.created_at >= month_start,
                EWasteItem.created_at <= month_end
            ).count()
            
            collections_count = Collection.query.filter(
                Collection.user_id == user_id,
                Collection.created_at >= month_start,
                Collection.created_at <= month_end
            ).count()
            
            monthly_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'items_added': items_count,
                'collections': collections_count
            })
        
        user_stats['monthly_trends'] = list(reversed(monthly_trends))
        
        return jsonify({
            'success': True,
            'user_stats': user_stats
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get dashboard stats: {str(e)}'}), 500

@analytics_bp.route('/system-stats', methods=['GET'])
@jwt_required()
def get_system_stats():
    """Get system-wide statistics (for admin users)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is admin
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # System-wide statistics
        total_users = User.query.filter_by(is_active=True).count()
        total_items = EWasteItem.query.count()
        total_collections = Collection.query.count()
        total_scans = WasteScan.query.count()
        total_posts = CommunityPost.query.count()
        pending_complaints = Complaint.query.filter_by(status='open').count()
        
        # Collection status breakdown
        collection_status = db.session.query(
            Collection.status,
            db.func.count(Collection.id).label('count')
        ).group_by(Collection.status).all()
        
        # Most active users
        active_users = db.session.query(
            User.id,
            User.username,
            User.first_name,
            User.last_name,
            db.func.count(EWasteItem.id).label('items_count')
        ).join(EWasteItem, User.id == EWasteItem.user_id)\
         .group_by(User.id)\
         .order_by(db.func.count(EWasteItem.id).desc())\
         .limit(10).all()
        
        # Category popularity
        category_stats = db.session.query(
            EWasteItem.category,
            db.func.count(EWasteItem.id).label('count'),
            db.func.avg(EWasteItem.estimated_value).label('avg_value')
        ).group_by(EWasteItem.category)\
         .order_by(db.func.count(EWasteItem.id).desc())\
         .all()
        
        # Environmental impact
        total_carbon = db.session.query(db.func.sum(CarbonFootprint.carbon_saved_kg)).scalar() or 0
        total_energy = db.session.query(db.func.sum(CarbonFootprint.energy_saved_kwh)).scalar() or 0
        total_water = db.session.query(db.func.sum(CarbonFootprint.water_saved_liters)).scalar() or 0
        
        return jsonify({
            'success': True,
            'system_stats': {
                'overview': {
                    'total_users': total_users,
                    'total_items': total_items,
                    'total_collections': total_collections,
                    'total_scans': total_scans,
                    'total_posts': total_posts,
                    'pending_complaints': pending_complaints
                },
                'collection_status': [
                    {'status': row.status, 'count': row.count}
                    for row in collection_status
                ],
                'active_users': [
                    {
                        'id': row.id,
                        'username': row.username,
                        'name': f"{row.first_name} {row.last_name}",
                        'items_count': row.items_count
                    }
                    for row in active_users
                ],
                'category_stats': [
                    {
                        'category': row.category,
                        'count': row.count,
                        'avg_value': float(row.avg_value or 0)
                    }
                    for row in category_stats
                ],
                'environmental_impact': {
                    'total_carbon_saved_kg': float(total_carbon),
                    'total_energy_saved_kwh': float(total_energy),
                    'total_water_saved_liters': float(total_water),
                    'trees_equivalent': float(total_carbon / 22),
                    'car_miles_equivalent': float(total_carbon / 0.4)
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get system stats: {str(e)}'}), 500

@analytics_bp.route('/recycling-trends', methods=['GET'])
@jwt_required()
def get_recycling_trends():
    """Get recycling trends and patterns"""
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Daily recycling activity
        daily_activity = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            items_added = EWasteItem.query.filter(
                EWasteItem.user_id == user_id,
                EWasteItem.created_at >= day_start,
                EWasteItem.created_at < day_end
            ).count()
            
            scans_performed = WasteScan.query.filter(
                WasteScan.user_id == user_id,
                WasteScan.scanned_at >= day_start,
                WasteScan.scanned_at < day_end
            ).count()
            
            carbon_saved = db.session.query(db.func.sum(CarbonFootprint.carbon_saved_kg))\
                                   .filter(
                                       CarbonFootprint.user_id == user_id,
                                       CarbonFootprint.recorded_at >= day_start,
                                       CarbonFootprint.recorded_at < day_end
                                   ).scalar() or 0
            
            daily_activity.append({
                'date': day.strftime('%Y-%m-%d'),
                'items_added': items_added,
                'scans_performed': scans_performed,
                'carbon_saved_kg': float(carbon_saved)
            })
        
        # Waste category trends
        category_trends = db.session.query(
            WasteScan.predicted_category,
            db.func.count(WasteScan.id).label('scan_count'),
            db.func.avg(WasteScan.confidence_score).label('avg_confidence')
        ).filter(
            WasteScan.user_id == user_id,
            WasteScan.scanned_at >= start_date
        ).group_by(WasteScan.predicted_category)\
         .order_by(db.func.count(WasteScan.id).desc())\
         .all()
        
        # Accuracy feedback
        accuracy_stats = db.session.query(
            WasteScan.is_correct,
            db.func.count(WasteScan.id).label('count')
        ).filter(
            WasteScan.user_id == user_id,
            WasteScan.is_correct.isnot(None)
        ).group_by(WasteScan.is_correct).all()
        
        total_feedback = sum(row.count for row in accuracy_stats)
        correct_feedback = sum(row.count for row in accuracy_stats if row.is_correct)
        accuracy_rate = (correct_feedback / total_feedback * 100) if total_feedback > 0 else 0
        
        return jsonify({
            'success': True,
            'trends': {
                'daily_activity': daily_activity,
                'category_trends': [
                    {
                        'category': row.predicted_category,
                        'scan_count': row.scan_count,
                        'avg_confidence': float(row.avg_confidence)
                    }
                    for row in category_trends
                ],
                'accuracy_stats': {
                    'accuracy_rate': accuracy_rate,
                    'total_feedback': total_feedback,
                    'correct_predictions': correct_feedback
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get recycling trends: {str(e)}'}), 500

@analytics_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Get community leaderboard"""
    try:
        # Top recyclers by carbon impact
        top_recyclers = db.session.query(
            User.id,
            User.username,
            User.first_name,
            User.last_name,
            db.func.sum(CarbonFootprint.carbon_saved_kg).label('total_carbon')
        ).join(CarbonFootprint, User.id == CarbonFootprint.user_id)\
         .group_by(User.id)\
         .order_by(db.func.sum(CarbonFootprint.carbon_saved_kg).desc())\
         .limit(10).all()
        
        # Most active scanners
        top_scanners = db.session.query(
            User.id,
            User.username,
            User.first_name,
            User.last_name,
            db.func.count(WasteScan.id).label('scan_count')
        ).join(WasteScan, User.id == WasteScan.user_id)\
         .group_by(User.id)\
         .order_by(db.func.count(WasteScan.id).desc())\
         .limit(10).all()
        
        # Most active community members
        top_community = db.session.query(
            User.id,
            User.username,
            User.first_name,
            User.last_name,
            db.func.count(CommunityPost.id).label('post_count')
        ).join(CommunityPost, User.id == CommunityPost.user_id)\
         .group_by(User.id)\
         .order_by(db.func.count(CommunityPost.id).desc())\
         .limit(10).all()
        
        return jsonify({
            'success': True,
            'leaderboard': {
                'top_recyclers': [
                    {
                        'rank': idx + 1,
                        'user_id': row.id,
                        'username': row.username,
                        'name': f"{row.first_name} {row.last_name}",
                        'carbon_saved_kg': float(row.total_carbon)
                    }
                    for idx, row in enumerate(top_recyclers)
                ],
                'top_scanners': [
                    {
                        'rank': idx + 1,
                        'user_id': row.id,
                        'username': row.username,
                        'name': f"{row.first_name} {row.last_name}",
                        'scan_count': row.scan_count
                    }
                    for idx, row in enumerate(top_scanners)
                ],
                'top_community': [
                    {
                        'rank': idx + 1,
                        'user_id': row.id,
                        'username': row.username,
                        'name': f"{row.first_name} {row.last_name}",
                        'post_count': row.post_count
                    }
                    for idx, row in enumerate(top_community)
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get leaderboard: {str(e)}'}), 500
