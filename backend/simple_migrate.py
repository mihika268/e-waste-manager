import sqlite3
import os

def migrate_db():
    """Simple database migration"""
    db_path = 'instance/ewaste.db'
    
    if not os.path.exists(db_path):
        print("Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add missing columns to user table
        cursor.execute("ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT 0")
        print("Added is_verified column")
    except:
        print("is_verified column already exists or error occurred")
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1")
        print("Added is_active column")
    except:
        print("is_active column already exists or error occurred")
    
    conn.commit()
    conn.close()
    print("Migration completed")

if __name__ == '__main__':
    migrate_db()