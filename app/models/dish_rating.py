"""
DISH RATING MODEL FOR STORING INDIVIDUAL FOOD ITEM RATINGS
"""

from datetime import datetime
from app import db

class DishRating(db.Model):
    """
    DISH RATING MODEL FOR STORING INDIVIDUAL FOOD ITEM RATINGS
    ONLY ALLOWED AFTER ORDER IS COMPLETED
    """
    __tablename__ = 'dish_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 STAR RATING
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # UNIQUE CONSTRAINT: One rating per customer per menu item per order
    __table_args__ = (db.UniqueConstraint('order_id', 'menu_item_id', name='unique_order_dish_rating'),)
    
    # RELATIONSHIPS
    order = db.relationship('Order', backref='dish_ratings')
    customer = db.relationship('Customer', backref='dish_ratings')
    restaurant = db.relationship('Restaurant', backref='dish_ratings')
    menu_item = db.relationship('MenuItem', backref='dish_ratings')
    
    def __repr__(self):
        return f'<Dish Rating #{self.id} - Item {self.menu_item_id} - {self.rating}/5>'
