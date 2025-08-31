"""
REVIEW AND FEEDBACK MODELS FOR STORING CUSTOMER FEEDBACK
"""

from datetime import datetime
from app import db

class Review(db.Model):
    """
    REVIEW MODEL FOR STORING RESTAURANT AND MENU ITEM REVIEWS
    """
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 STAR RATING
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review #{self.id} - {self.rating}/5>'

class Feedback(db.Model):
    """
    FEEDBACK MODEL FOR STORING GENERAL APPLICATION FEEDBACK
    """
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        status = "Resolved" if self.is_resolved else "Pending"
        return f'<Feedback #{self.id} - {status}>'
