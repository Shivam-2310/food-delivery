"""Feedback model for storing customer feedback."""

from datetime import datetime

from app import db

class Feedback(db.Model):
    """Feedback model for storing order-specific feedback.

    Only allowed after order is completed.
    """
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 star rating.
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note: order relationship is defined in the Order model.
    
    def __repr__(self):
        status = "Responded" if self.is_resolved else "Pending Response"
        return f'<Order Feedback #{self.id} - {self.rating}/5 - {status}>'
