#!/usr/bin/env python3
"""
Startup script for E-Waste Management System

This script initializes the database and starts the Flask application.
It's the easiest way to get the project running!

Author: [Your Name/Team]
Created: 2024

Usage:
    python start.py

What it does:
    1. Sets up the database with default categories
    2. Starts the Flask development server on http://localhost:5000
    3. Provides helpful information for getting started

Note: Make sure you've installed dependencies first:
    cd backend
    pip install -r requirements.txt
"""

import os
import sys
import logging

# Configure logging to show INFO level messages in console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Ensure we can import the backend app when running from project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app, db
from app.models.ewaste import EWasteCategory

def setup_database():
    """Setup database with initial data"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Setting up database...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Check if categories exist, if not create them
        if EWasteCategory.query.count() == 0:
            print("📦 Creating default categories...")
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
            
            for cat_data in categories:
                category = EWasteCategory(**cat_data)
                db.session.add(category)
            
            db.session.commit()
            print("✅ Default categories created")
        
        print("🎉 Database setup completed!")
        return app

def main():
    """Main function to start the application"""
    print("🌱 E-Waste Management System")
    print("=" * 40)
    
    # Setup database
    app = setup_database()
    
    print("\n📋 Quick Start Guide:")
    print("1. Open your browser and go to: http://localhost:5000")
    print("2. Click 'Create Account' to register a new user")
    print("3. Or use sample data by running: python init_sample_data.py")
    print("\n🔐 Sample Login (after running init_sample_data.py):")
    print("   Username: john_doe")
    print("   Password: password123")
    
    print("\n🚀 Starting Flask development server...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
