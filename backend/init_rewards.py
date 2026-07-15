"""
Initialize default badges and rewards for the E-Waste Management System

Run this script to populate the database with default badges and rewards
that users can earn and redeem.

Author: Muskan Uttam
Created: 2025
"""

from app import create_app, db
from app.models.rewards import Badge, Reward

def init_badges_and_rewards():
    """Initialize default badges and rewards"""
    app = create_app()
    
    with app.app_context():
        print("🏆 Initializing badges and rewards...")
        
        # Default badges
        badges = [
            {
                'name': 'First Steps',
                'description': 'Register your first e-waste item',
                'icon': '🌟',
                'points_threshold': 10,
                'condition_type': 'items_registered',
                'condition_value': 1
            },
            {
                'name': 'Eco Warrior',
                'description': 'Register 10 e-waste items',
                'icon': '🥇',
                'points_threshold': 100,
                'condition_type': 'items_registered',
                'condition_value': 10
            },
            {
                'name': 'Super Recycler',
                'description': 'Register 25 e-waste items',
                'icon': '🏆',
                'points_threshold': 250,
                'condition_type': 'items_registered',
                'condition_value': 25
            },
            {
                'name': 'Point Collector',
                'description': 'Earn 100 points',
                'icon': '💎',
                'points_threshold': 100,
                'condition_type': 'points_total',
                'condition_value': 100
            },
            {
                'name': 'Point Master',
                'description': 'Earn 500 points',
                'icon': '👑',
                'points_threshold': 500,
                'condition_type': 'points_total',
                'condition_value': 500
            },
            {
                'name': 'Collection Hero',
                'description': 'Get 5 items collected',
                'icon': '🚚',
                'points_threshold': 50,
                'condition_type': 'items_collected',
                'condition_value': 5
            }
        ]
        
        # Create badges
        for badge_data in badges:
            existing = Badge.query.filter_by(name=badge_data['name']).first()
            if not existing:
                badge = Badge(**badge_data)
                db.session.add(badge)
                print(f"✅ Created badge: {badge_data['name']}")
        
        # Default rewards
        rewards = [
            {
                'name': '10% Discount',
                'description': 'Get 10% off on your next e-waste collection',
                'points_cost': 50,
                'reward_type': 'discount',
                'value': '10%'
            },
            {
                'name': 'Free Collection',
                'description': 'Get one free collection pickup',
                'points_cost': 100,
                'reward_type': 'free_item',
                'value': '1 free pickup'
            },
            {
                'name': 'Plant a Tree',
                'description': 'Contribute to planting a tree in your name',
                'points_cost': 200,
                'reward_type': 'charity',
                'value': 'Tree planted'
            },
            {
                'name': 'Premium Badge',
                'description': 'Get a special premium badge on your profile',
                'points_cost': 150,
                'reward_type': 'badge',
                'value': 'Premium Badge'
            }
        ]
        
        # Create rewards
        for reward_data in rewards:
            existing = Reward.query.filter_by(name=reward_data['name']).first()
            if not existing:
                reward = Reward(**reward_data)
                db.session.add(reward)
                print(f"✅ Created reward: {reward_data['name']}")
        
        db.session.commit()
        print("🎉 Badges and rewards initialized successfully!")

if __name__ == '__main__':
    init_badges_and_rewards()

