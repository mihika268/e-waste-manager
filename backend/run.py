from dotenv import load_dotenv
import os

# Load environment variables from .env file before creating app
load_dotenv()

from app import create_app, db
from app.models.user import User
from app.models.ewaste import EWasteCategory, EWasteItem, Collection

app = create_app()

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        # Create default categories
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
            existing = EWasteCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = EWasteCategory(**cat_data)
                db.session.add(category)
        
        db.session.commit()
        print("Database initialized with sample categories!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
