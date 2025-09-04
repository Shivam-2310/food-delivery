"""
MENU ITEM MODEL
"""

from datetime import datetime
from app import db

class MenuItem(db.Model):
    """
    MENU ITEM MODEL FOR STORING FOOD ITEMS
    """
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), index=True)
    is_vegetarian = db.Column(db.Boolean, default=True)
    is_vegan = db.Column(db.Boolean, default=False)
    is_guilt_free = db.Column(db.Boolean, default=False)
    image_path = db.Column(db.String(200))
    is_special = db.Column(db.Boolean, default=False)
    is_deal_of_day = db.Column(db.Boolean, default=False)
    times_ordered_today = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    order_items = db.relationship('OrderItem', backref='menu_item', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='menu_item', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MenuItem {self.name}>'
    
    @property
    def is_mostly_ordered(self):
        """CHECK IF ITEM IS MOSTLY ORDERED (>10 TIMES TODAY)"""
        return self.times_ordered_today > 10
    
    @property
    def average_rating(self):
        """CALCULATE AVERAGE RATING FOR MENU ITEM"""
        item_reviews = self.reviews.all()
        if not item_reviews:
            return 0
        return sum(r.rating for r in item_reviews) / len(item_reviews)
    
    @property
    def total_reviews(self):
        """GET TOTAL NUMBER OF REVIEWS"""
        return self.reviews.count()
    
    def reset_daily_order_count(self):
        """RESET THE DAILY ORDER COUNT"""
        self.times_ordered_today = 0
