from app import create_app, db
from app.models.users import User
from app.models.listings import Listing
from app.models.swaps import SwapRequest
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

# Sample images provided
sample_images = [
    'https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://images.unsplash.com/photo-1523381294911-8d3cead13475?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OHx8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://plus.unsplash.com/premium_photo-1673356301514-2cad91907f74?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://plus.unsplash.com/premium_photo-1718913931807-4da5b5dd27fa?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8dCUyMHNoaXJ0fGVufDB8fDB8fHww',
    'https://plus.unsplash.com/premium_photo-1661416497808-2319460830cb?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8c2xlZXZlfGVufDB8fDB8fHww',
    'https://images.unsplash.com/photo-1675668409245-955188b96bf6?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8c2xlZXZlfGVufDB8fDB8fHww',
    'https://plus.unsplash.com/premium_photo-1664202526559-e21e9c0fb46a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8ZmFzaGlvbnxlbnwwfHwwfHx8MA%3D%3D'
]

def create_sample_users():
    """Create sample users for testing"""
    users_data = [
        {'username': 'alice_style', 'email': 'alice@example.com', 'points': 250},
        {'username': 'bob_fashion', 'email': 'bob@example.com', 'points': 180},
        {'username': 'carol_trends', 'email': 'carol@example.com', 'points': 320},
        {'username': 'david_wear', 'email': 'david@example.com', 'points': 150},
        {'username': 'emma_closet', 'email': 'emma@example.com', 'points': 400},
        {'username': 'frank_swap', 'email': 'frank@example.com', 'points': 90},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=generate_password_hash('password123'),
            points=user_data['points'],
            is_admin=False
        )
        users.append(user)
        db.session.add(user)
    
    # Add an admin user
    admin = User(
        username='admin',
        email='admin@rewear.com',
        password=generate_password_hash('admin123'),
        points=1000,
        is_admin=True
    )
    users.append(admin)
    db.session.add(admin)
    
    db.session.commit()
    return users

def create_sample_listings(users):
    """Create sample listings for testing"""
    listings_data = [
        {
            'title': 'Vintage Blue Denim Shirt',
            'description': 'Classic blue denim shirt in excellent condition. Perfect for casual outings and layering.',
            'category': 'Men',
            'type': 'Shirt',
            'size': 'M',
            'point_value': 120,
        },
        {
            'title': 'Elegant Black Evening Dress',
            'description': 'Stunning black evening dress, worn only once. Perfect for special occasions.',
            'category': 'Women',
            'type': 'Dress',
            'size': 'S',
            'point_value': 200,
        },
        {
            'title': 'Casual White Cotton T-Shirt',
            'description': 'Comfortable white cotton t-shirt. Great for everyday wear and easy to style.',
            'category': 'Men',
            'type': 'Shirt',
            'size': 'L',
            'point_value': 80,
        },
        {
            'title': 'Floral Summer Dress',
            'description': 'Beautiful floral print summer dress. Light and breezy, perfect for warm weather.',
            'category': 'Women',
            'type': 'Dress',
            'size': 'M',
            'point_value': 150,
        },
        {
            'title': 'Kids Rainbow Striped Shirt',
            'description': 'Colorful rainbow striped shirt for kids. Fun and vibrant design.',
            'category': 'Kids',
            'type': 'Shirt',
            'size': 'S',
            'point_value': 60,
        },
        {
            'title': 'Dark Blue Jeans',
            'description': 'Classic dark blue jeans in great condition. Comfortable fit and timeless style.',
            'category': 'Men',
            'type': 'Pants',
            'size': 'L',
            'point_value': 140,
        },
        {
            'title': 'Red Silk Blouse',
            'description': 'Elegant red silk blouse. Professional and stylish, perfect for work or special events.',
            'category': 'Women',
            'type': 'Shirt',
            'size': 'M',
            'point_value': 180,
        },
        {
            'title': 'Leather Jacket',
            'description': 'Genuine leather jacket in black. Edgy and stylish, adds attitude to any outfit.',
            'category': 'Men',
            'type': 'Others',
            'size': 'XL',
            'point_value': 300,
        },
        {
            'title': 'Summer Maxi Dress',
            'description': 'Flowing maxi dress perfect for summer occasions. Comfortable and elegant.',
            'category': 'Women',
            'type': 'Dress',
            'size': 'L',
            'point_value': 160,
        },
        {
            'title': 'Designer Polo Shirt',
            'description': 'High-quality designer polo shirt. Sophisticated and versatile for various occasions.',
            'category': 'Men',
            'type': 'Shirt',
            'size': 'M',
            'point_value': 220,
        }
    ]
    
    listings = []
    for i, listing_data in enumerate(listings_data):
        # Create some variation in created dates
        days_ago = random.randint(1, 30)
        created_date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Random approval status (most should be approved for testing)
        is_approved = random.choice([True, True, True, False])  # 75% approved
        
        listing = Listing(
            uploader_id=random.choice(users[:-1]).user_id,  # Don't use admin as uploader
            title=listing_data['title'],
            description=listing_data['description'],
            category=listing_data['category'],
            type=listing_data['type'],
            size=listing_data['size'],
            image_url=random.choice(sample_images),
            point_value=listing_data['point_value'],
            is_approved=is_approved,
            is_available=True,
            status='Available',
            created_at=created_date
        )
        listings.append(listing)
        db.session.add(listing)
    
    db.session.commit()
    return listings

def create_sample_swaps(users, listings):
    """Create sample swap requests for testing"""
    # Only create swaps for approved and available listings
    available_listings = [l for l in listings if l.is_approved and l.is_available]
    
    if len(available_listings) < 2:
        print("Not enough approved listings to create swaps")
        return []
    
    swaps_data = [
        {
            'requester_id': users[0].user_id,
            'requested_item_id': available_listings[0].id,
            'offered_item_id': available_listings[1].id,
            'swap_type': 'direct_swap',
            'status': 'Pending',
            'points_used': 0
        },
        {
            'requester_id': users[1].user_id,
            'requested_item_id': available_listings[2].id,
            'offered_item_id': None,
            'swap_type': 'point_redemption',
            'status': 'Pending',
            'points_used': available_listings[2].point_value
        },
        {
            'requester_id': users[2].user_id,
            'requested_item_id': available_listings[3].id,
            'offered_item_id': available_listings[4].id,
            'swap_type': 'direct_swap',
            'status': 'Accepted',
            'points_used': 0
        }
    ]
    
    swaps = []
    for swap_data in swaps_data:
        # Ensure the requester is not the same as the item owner
        requested_item = next(l for l in available_listings if l.id == swap_data['requested_item_id'])
        if swap_data['requester_id'] == requested_item.uploader_id:
            continue  # Skip this swap to avoid self-swapping
            
        swap = SwapRequest(
            requester_id=swap_data['requester_id'],
            requested_item_id=swap_data['requested_item_id'],
            offered_item_id=swap_data['offered_item_id'],
            swap_type=swap_data['swap_type'],
            status=swap_data['status'],
            points_used=swap_data['points_used']
        )
        swaps.append(swap)
        db.session.add(swap)
    
    db.session.commit()
    return swaps

def populate_sample_data():
    """Main function to populate the database with sample data"""
    app = create_app()
    with app.app_context():
        print("Creating sample data...")
        
        # Create sample users
        print("Creating sample users...")
        users = create_sample_users()
        print(f"Created {len(users)} users")
        
        # Create sample listings
        print("Creating sample listings...")
        listings = create_sample_listings(users)
        print(f"Created {len(listings)} listings")
        
        # Create sample swaps
        print("Creating sample swap requests...")
        swaps = create_sample_swaps(users, listings)
        print(f"Created {len(swaps)} swap requests")
        
        print("Sample data creation completed!")
        print("\nSample accounts created:")
        print("Admin: admin@rewear.com / admin123")
        print("Users: alice@example.com, bob@example.com, carol@example.com, etc. / password123")

if __name__ == '__main__':
    populate_sample_data()
