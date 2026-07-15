#!/usr/bin/env python3
"""
Enhanced Database Management System for E-Waste Management
Provides comprehensive database operations, monitoring, and maintenance
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.ewaste import EWasteCategory, EWasteItem, Collection
from app.models.community import CommunityPost, PostComment, PostLike
from app.models.feedback import Complaint, Feedback
from app.models.scanner import WasteScan, CarbonFootprint
from app.models.otp import OTP

class DatabaseManager:
    def __init__(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.backup_dir = 'backups'
        self.db_path = 'instance/ewaste.db'
    
    def __enter__(self):
        self.app_context.push()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.app_context.pop()
    
    def init_database(self):
        """Initialize database with all tables"""
        try:
            print("🗃️ Initializing database...")
            db.create_all()
            
            # Initialize default categories
            self.init_categories()
            
            print("✅ Database initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            return False
    
    def init_categories(self):
        """Initialize default e-waste categories"""
        categories = [
            {'name': 'Computers & Laptops', 'description': 'Desktop computers, laptops, tablets', 'recycling_fee': 25.0},
            {'name': 'Mobile Phones', 'description': 'Smartphones, feature phones, accessories', 'recycling_fee': 10.0},
            {'name': 'Television & Monitors', 'description': 'TVs, computer monitors, displays', 'recycling_fee': 30.0},
            {'name': 'Home Appliances', 'description': 'Refrigerators, washing machines, microwaves', 'recycling_fee': 50.0},
            {'name': 'Audio & Video Equipment', 'description': 'Speakers, headphones, cameras', 'recycling_fee': 15.0},
            {'name': 'Gaming Consoles', 'description': 'Video game consoles and accessories', 'recycling_fee': 20.0},
            {'name': 'Batteries', 'description': 'All types of batteries', 'recycling_fee': 5.0},
            {'name': 'Cables & Accessories', 'description': 'Chargers, cables, adapters', 'recycling_fee': 2.0}
        ]
        
        created_count = 0
        for cat_data in categories:
            existing = EWasteCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = EWasteCategory(**cat_data)
                db.session.add(category)
                created_count += 1
        
        if created_count > 0:
            db.session.commit()
            print(f"✅ Created {created_count} default categories")
        else:
            print("ℹ️ Categories already exist")
    
    def create_backup(self, backup_name=None):
        """Create a database backup"""
        try:
            if not os.path.exists(self.db_path):
                print(f"❌ Database file not found: {self.db_path}")
                return None
            
            # Ensure backup directory exists
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            
            # Generate backup filename
            if backup_name is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"ewaste_backup_{timestamp}.db"
            
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            # Get backup size
            backup_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
            
            print(f"💾 Database backup created: {backup_path}")
            print(f"📊 Backup size: {backup_size:.2f} MB")
            return backup_path
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return None
    
    def get_statistics(self):
        """Get comprehensive database statistics"""
        try:
            stats = {
                'database': {
                    'size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0,
                    'created': datetime.fromtimestamp(os.path.getctime(self.db_path)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(self.db_path) else 'N/A',
                    'modified': datetime.fromtimestamp(os.path.getmtime(self.db_path)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(self.db_path) else 'N/A'
                },
                'tables': {
                    'users': User.query.count(),
                    'categories': EWasteCategory.query.count(),
                    'ewaste_items': EWasteItem.query.count(),
                    'collections': Collection.query.count(),
                    'community_posts': CommunityPost.query.count(),
                    'complaints': Complaint.query.count(),
                    'feedback': Feedback.query.count(),
                    'waste_scans': WasteScan.query.count(),
                    'carbon_footprints': CarbonFootprint.query.count(),
                    'otps': OTP.query.count()
                }
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return None
    
    def cleanup_expired_data(self):
        """Clean up expired and old data"""
        try:
            print("🧹 Cleaning up expired data...")
            
            # Clean up expired OTPs
            expired_otps = OTP.cleanup_expired_otps()
            print(f"  - Cleaned up {expired_otps} expired OTPs")
            
            # Clean up old waste scans (older than 90 days)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            old_scans = WasteScan.query.filter(WasteScan.scanned_at < cutoff_date).all()
            for scan in old_scans:
                db.session.delete(scan)
            
            if old_scans:
                db.session.commit()
                print(f"  - Cleaned up {len(old_scans)} old waste scans")
            
            # Clean up old carbon footprint records (older than 1 year)
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            old_footprints = CarbonFootprint.query.filter(CarbonFootprint.recorded_at < cutoff_date).all()
            for footprint in old_footprints:
                db.session.delete(footprint)
            
            if old_footprints:
                db.session.commit()
                print(f"  - Cleaned up {len(old_footprints)} old carbon footprint records")
            
            print("✅ Cleanup completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False
    
    def optimize_database(self):
        """Optimize database performance"""
        try:
            print("⚡ Optimizing database...")
            
            # Get raw SQLite connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Run VACUUM to reclaim space
            cursor.execute("VACUUM")
            print("  - Database vacuumed")
            
            # Run ANALYZE to update statistics
            cursor.execute("ANALYZE")
            print("  - Database statistics updated")
            
            conn.commit()
            conn.close()
            
            print("✅ Database optimization completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error optimizing database: {e}")
            return False
    
    def reset_database(self):
        """Reset database (WARNING: Deletes all data)"""
        try:
            print("⚠️  WARNING: This will delete all data in the database!")
            confirm = input("Are you sure? Type 'YES' to continue: ")
            
            if confirm != 'YES':
                print("❌ Database reset cancelled")
                return False
            
            print("🗑️  Dropping all tables...")
            db.drop_all()
            
            print("🔄 Recreating tables...")
            db.create_all()
            
            print("✅ Database reset completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            return False

def main():
    """Main function with CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_db_manager.py [command] [options]")
        print("\nAvailable commands:")
        print("  init          - Initialize database")
        print("  backup        - Create database backup")
        print("  stats         - Show database statistics")
        print("  cleanup       - Clean up expired data")
        print("  optimize      - Optimize database performance")
        print("  reset         - Reset database (WARNING: Deletes all data)")
        return
    
    command = sys.argv[1]
    
    with DatabaseManager() as manager:
        if command == 'init':
            manager.init_database()
        elif command == 'backup':
            backup_name = sys.argv[2] if len(sys.argv) > 2 else None
            manager.create_backup(backup_name)
        elif command == 'stats':
            stats = manager.get_statistics()
            if stats:
                print("\n📊 Database Statistics")
                print("=" * 40)
                print(f"Database Size: {stats['database']['size_mb']:.2f} MB")
                print(f"Created: {stats['database']['created']}")
                print(f"Modified: {stats['database']['modified']}")
                print("\nTable Counts:")
                for table, count in stats['tables'].items():
                    print(f"  {table.replace('_', ' ').title()}: {count}")
        elif command == 'cleanup':
            manager.cleanup_expired_data()
        elif command == 'optimize':
            manager.optimize_database()
        elif command == 'reset':
            manager.reset_database()
        else:
            print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main()