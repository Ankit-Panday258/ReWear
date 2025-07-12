from app import db
import uuid
from datetime import datetime
from sqlalchemy import String, CheckConstraint


class SwapRequest(db.Model):
    __tablename__ = 'swaps'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requester_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    requested_item_id = db.Column(db.String(36), db.ForeignKey('listings.id'), nullable=False)
    offered_item_id = db.Column(db.String(36), db.ForeignKey('listings.id'), nullable=True)
    status = db.Column(db.String(50), default='Pending', nullable=False)
    swap_type = db.Column(db.String(50), nullable=False)
    points_used = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], backref=db.backref('swap_requests_made', lazy=True))
    requested_item = db.relationship('Listing', foreign_keys=[requested_item_id], backref=db.backref('swap_requests_received', lazy=True))
    offered_item = db.relationship('Listing', foreign_keys=[offered_item_id], backref=db.backref('swap_requests_offered', lazy=True))
    
    # Check constraint for valid status values
    __table_args__ = (
        CheckConstraint(
            status.in_(['Pending', 'Accepted', 'Rejected', 'Cancelled']),
            name='check_status'
        ),
        CheckConstraint(
            swap_type.in_(['direct_swap', 'point_redemption']),
            name='check_swap_type'
        ),
        CheckConstraint(
            points_used >= 0,
            name='check_points_used_positive'
        ),
    )
    
    def __repr__(self):
        return f'<SwapRequest {self.id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'requester_id': self.requester_id,
            'requested_item_id': self.requested_item_id,
            'offered_item_id': self.offered_item_id,
            'status': self.status,
            'swap_type': self.swap_type,
            'points_used': self.points_used,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def accept(self):
        """Accept the swap request"""
        self.status = 'Accepted'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def reject(self):
        """Reject the swap request"""
        self.status = 'Rejected'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def cancel(self):
        """Cancel the swap request"""
        self.status = 'Cancelled'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_point_redemption(self):
        """Check if this is a point-based redemption"""
        return self.swap_type == 'point_redemption'
    
    def is_direct_swap(self):
        """Check if this is a direct item swap"""
        return self.swap_type == 'direct_swap'