#!/usr/bin/env python3
"""
Sample data initialization script for E-Waste Management System
Run this script to populate the database with sample data for testing
"""

from app import create_app, db
from app.models.user import User
from app.models.ewaste import EWasteCategory, EWasteItem, Collection
from datetime import datetime, timedelta
import random

def init_sample_data():
    """Initialize database with sample data"""
    app = create_app()
    
    with app.app_context():
        print("🗃️  Initializing sample data...")
        
        # Create sample categories (if not exists)
        categories_data = [
            {'name': 'Computers & Laptops', 'description': 'Desktop computers, laptops, tablets', 'recycling_fee': 25.0},
            {'name': 'Mobile Phones', 'description': 'Smartphones, feature phones, accessories', 'recycling_fee': 10.0},
            {'name': 'Television & Monitors', 'description': 'TVs, computer monitors, displays', 'recycling_fee': 30.0},
            {'name': 'Home Appliances', 'description': 'Refrigerators, washing machines, microwaves', 'recycling_fee': 50.0},
            {'name': 'Audio & Video Equipment', 'description': 'Speakers, headphones, cameras', 'recycling_fee': 15.0},
            {'name': 'Gaming Consoles', 'description': 'Video game consoles and accessories', 'recycling_fee': 20.0},
            {'name': 'Batteries', 'description': 'All types of batteries', 'recycling_fee': 5.0},
            {'name': 'Cables & Accessories', 'description': 'Chargers, cables, adapters', 'recycling_fee': 2.0}
        ]
        
        categories = {}
        for cat_data in categories_data:
            existing = EWasteCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = EWasteCategory(**cat_data)
                db.session.add(category)
                db.session.flush()
                categories[cat_data['name']] = category
            else:
                categories[cat_data['name']] = existing
        
        # Create sample users
        sample_users = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+1-555-0101',
                'address': '123 Main St, Anytown, USA',
                'role': 'user'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone': '+1-555-0102',
                'address': '456 Oak Ave, Somewhere, USA',
                'role': 'user'
            },
            {
                'username': 'admin_user',
                'email': 'admin@example.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'phone': '+1-555-0100',
                'address': '789 Admin Blvd, HQ City, USA',
                'role': 'admin'
            }
        ]
        
        users = {}
        for user_data in sample_users:
            existing = User.query.filter_by(username=user_data['username']).first()
            if not existing:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone=user_data['phone'],
                    address=user_data['address'],
                    role=user_data['role'],
                    is_verified=True  # Mark sample users as verified
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                db.session.flush()
                users[user_data['username']] = user
                print(f"✅ Created user: {user_data['username']} ({user_data['email']})")
            else:
                users[user_data['username']] = existing
                print(f"ℹ️  User already exists: {user_data['username']}")
        
        # Create sample e-waste items
        sample_items = [
            {
                'name': 'Dell Laptop XPS 13',
                'brand': 'Dell',
                'model': 'XPS 13 9310',
                'serial_number': 'DL123456789',
                'condition': 'working',
                'weight': 1.2,
                'description': 'Laptop in good working condition, minor scratches on lid',
                'estimated_value': 450.0,
                'category': 'Computers & Laptops',
                'user': 'john_doe',
                'status': 'registered'
            },
            {
                'name': 'iPhone 12',
                'brand': 'Apple',
                'model': 'iPhone 12',
                'serial_number': 'AP987654321',
                'condition': 'partially_working',
                'weight': 0.164,
                'description': 'Screen is cracked but phone still works',
                'estimated_value': 200.0,
                'category': 'Mobile Phones',
                'user': 'john_doe',
                'status': 'collected'
            },
            {
                'name': 'Samsung 4K TV',
                'brand': 'Samsung',
                'model': 'UN55TU8000',
                'serial_number': 'SM555444333',
                'condition': 'broken',
                'weight': 15.5,
                'description': 'TV does not turn on, possible power supply issue',
                'estimated_value': 100.0,
                'category': 'Television & Monitors',
                'user': 'jane_smith',
                'status': 'registered'
            },
            {
                'name': 'PlayStation 5',
                'brand': 'Sony',
                'model': 'PS5',
                'serial_number': 'PS123789456',
                'condition': 'working',
                'weight': 4.5,
                'description': 'Console works perfectly, includes controller',
                'estimated_value': 350.0,
                'category': 'Gaming Consoles',
                'user': 'jane_smith',
                'status': 'recycled'
            },
            {
                'name': 'Old Desktop Computer',
                'brand': 'HP',
                'model': 'Pavilion Desktop',
                'serial_number': 'HP111222333',
                'condition': 'broken',
                'weight': 8.2,
                'description': 'Old desktop computer, not working, for parts only',
                'estimated_value': 50.0,
                'category': 'Computers & Laptops',
                'user': 'john_doe',
                'status': 'processed'
            }
        ]
        
        items = []
        for item_data in sample_items:
            category = categories.get(item_data['category'])
            user = users.get(item_data['user'])
            
            if category and user:
                item = EWasteItem(
                    name=item_data['name'],
                    brand=item_data['brand'],
                    model=item_data['model'],
                    serial_number=item_data['serial_number'],
                    condition=item_data['condition'],
                    weight=item_data['weight'],
                    description=item_data['description'],
                    estimated_value=item_data['estimated_value'],
                    status=item_data['status'],
                    user_id=user.id,
                    category_id=category.id,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(item)
                items.append(item)
                print(f"✅ Created item: {item_data['name']} for {item_data['user']}")
        
        db.session.flush()
        
        # Create sample collections
        sample_collections = [
            {
                'item_name': 'iPhone 12',
                'user': 'john_doe',
                'collection_date': datetime.utcnow() + timedelta(days=3),
                'status': 'scheduled',
                'notes': 'Pickup scheduled for next week',
                'collector_name': 'Green Recycling Co.',
                'collector_phone': '+1-555-RECYCLE'
            },
            {
                'item_name': 'Samsung 4K TV',
                'user': 'jane_smith',
                'collection_date': datetime.utcnow() + timedelta(days=7),
                'status': 'scheduled',
                'notes': 'Large item pickup required',
                'collector_name': 'EcoWaste Solutions',
                'collector_phone': '+1-555-ECOWASTE'
            }
        ]
        
        for collection_data in sample_collections:
            user = users.get(collection_data['user'])
            item = next((i for i in items if i.name == collection_data['item_name'] and i.user_id == user.id), None)
            
            if user and item:
                collection = Collection(
                    collection_date=collection_data['collection_date'],
                    status=collection_data['status'],
                    notes=collection_data['notes'],
                    collector_name=collection_data['collector_name'],
                    collector_phone=collection_data['collector_phone'],
                    user_id=user.id,
                    ewaste_item_id=item.id
                )
                db.session.add(collection)
                print(f"✅ Created collection for: {collection_data['item_name']}")
        
        # Commit all changes
        db.session.commit()
        
        print("\n🎉 Sample data initialization completed!")
        print("\n📊 Summary:")
        print(f"   • Categories: {len(categories_data)}")
        print(f"   • Users: {len(sample_users)}")
        print(f"   • E-waste Items: {len(sample_items)}")
        print(f"   • Collections: {len(sample_collections)}")
        
        print("\n👤 Sample Login Credentials:")
        print("   • Username: john_doe, Password: password123")
        print("   • Username: jane_smith, Password: password123")
        print("   • Username: admin_user, Password: admin123")
        
        print("\n🚀 You can now start the application with: python run.py")

if __name__ == '__main__':
    init_sample_data()
