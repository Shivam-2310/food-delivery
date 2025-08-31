"""
RESTAURANT AND RESTAURANT OWNER MODELS
"""

from datetime import datetime
from app import db

class RestaurantOwner(db.Model):
    """
    RESTAURANT OWNER MODEL FOR STORING OWNER INFORMATION
    """
    __tablename__ = 'restaurant_owners'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    restaurants = db.relationship('Restaurant', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<RestaurantOwner {self.name}>'

class Restaurant(db.Model):
    """
    RESTAURANT MODEL FOR STORING RESTAURANT INFORMATION
    """
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('restaurant_owners.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False, index=True)
    cuisine_type = db.Column(db.String(50), index=True)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='restaurant', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='restaurant', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'
    
    @property
    def average_rating(self):
        """CALCULATE AVERAGE RATING FOR RESTAURANT"""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)
    
    @property
    def total_reviews(self):
        """GET TOTAL NUMBER OF REVIEWS"""
        return self.reviews.count()
    
    def get_menu_by_category(self):
        """GROUP MENU ITEMS BY CATEGORY"""
        menu_dict = {}
        for item in self.menu_items:
            if item.category not in menu_dict:
                menu_dict[item.category] = []
            menu_dict[item.category].append(item)
        return menu_dict
