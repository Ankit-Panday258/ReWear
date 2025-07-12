from app import db
import uuid
from datetime import datetime
from sqlalchemy import String

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), nullable=False)   
    email = db.Column(db.String(120), unique=True, nullable=False)   
    password = db.Column(db.String(255), nullable=False)    
    points = db.Column(db.Integer, default=100, nullable=False)   
    is_admin = db.Column(db.Boolean, default=False, nullable=False)   
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'points': self.points,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }
    
    def add_points(self, amount):
        """Add points to user account"""
        self.points += amount
        db.session.commit()
    
    def deduct_points(self, amount):
        """Deduct points from user account if sufficient balance"""
        if self.points >= amount:
            self.points -= amount
            db.session.commit()
            return True
        return False

