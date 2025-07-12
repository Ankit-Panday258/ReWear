from app import db
import uuid
from datetime import datetime
from sqlalchemy import String, CheckConstraint

default_image ='https://plus.unsplash.com/premium_photo-1718913936342-eaafff98834b?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8dCUyMHNoaXJ0fGVufDB8fDB8fHww'

class Listing(db.Model):
    __tablename__ = 'listings'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    uploader_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)  
    title = db.Column(db.String(200), nullable=False)   
    description = db.Column(db.Text, nullable=True)   
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    image_url = db.Column(db.String(255), default=default_image, nullable=True)
    point_value = db.Column(db.Integer, default=100, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)  # ADD THIS LINE
    status = db.Column(db.String(50), default='Available', nullable=False)   
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with User model
    uploader = db.relationship('User', backref=db.backref('listings', lazy=True))
    
    __table_args__ = (
        CheckConstraint(
            category.in_(['Men', 'Women', 'Kids']),
            name='check_category'
        ),
        CheckConstraint(
            type.in_(['Shirt', 'Pants', 'Dress', 'Others']),
            name='check_type'
        ),
        CheckConstraint(
            size.in_(['S', 'M', 'L', 'XL']),
            name='check_size'
        ),
        CheckConstraint(
            status.in_(['Available', 'Swapped', 'Redeemed']),
            name='check_status'
        ),
        CheckConstraint(
            point_value >= 0,
            name='check_point_value_positive'
        ),
    )
    
    def __repr__(self):
        return f'<Listing {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'uploader_id': self.uploader_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'type': self.type,
            'size': self.size,
            'image_url': self.image_url,
            'point_value': self.point_value,
            'is_approved': self.is_approved,
            'is_available': self.is_available,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
    
    def approve(self):
        """Approve the listing"""
        self.is_approved = True
        db.session.commit()
    
    def mark_as_swapped(self):
        """Mark item as swapped"""
        self.status = 'Swapped'
        self.is_available = False
        db.session.commit()
    
    def mark_as_redeemed(self):
        """Mark item as redeemed"""
        self.status = 'Redeemed'
        self.is_available = False
        db.session.commit()
