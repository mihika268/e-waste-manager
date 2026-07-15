#!/usr/bin/env python3
"""
Database Management Utility for E-Waste Management System
"""

import os
import shutil
from datetime import datetime
from app import create_app, db

def backup_database():
    """Create a backup of the database"""
    app = create_app()
    with app.app_context():
        try:
            db_path = 'instance/ewaste.db'
            backup_dir = 'backups'
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f"ewaste_backup_{timestamp}.db")
            
            shutil.copy2(db_path, backup_path)
            print(f"Database backup created: {backup_path}")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

def database_stats():
    """Show database statistics"""
    app = create_app()
    with app.app_context():
        try:
            from app.models.user import User
            from app.models.ewaste import EWasteCategory, EWasteItem, Collection
            
            stats = {
                'users': User.query.count(),
                'categories': EWasteCategory.query.count(),
                'ewaste_items': EWasteItem.query.count(),
                'collections': Collection.query.count()
            }
            
            print("Database Statistics:")
            for table, count in stats.items():
                print(f"{table}: {count}")
            
            return stats
        except Exception as e:
            print(f"Error getting stats: {e}")
            return None

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'backup':
            backup_database()
        elif sys.argv[1] == 'stats':
            database_stats()
    else:
        print("Usage: python database_manager.py [backup|stats]")