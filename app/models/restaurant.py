"""
RESTAURANT AND RESTAURANT OWNER MODELS
"""

from datetime import datetime
from app import db
import json

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
    # Store multiple cuisines as JSON-encoded text
    cuisines = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='restaurant', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='restaurant', lazy='dynamic')
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'
    
    @property
    def average_rating(self):
        """Calculate average rating using order feedback only."""
        from sqlalchemy import func
        from app import db
        from app.models.feedback import Feedback
        avg_value = db.session.query(func.avg(Feedback.rating)).filter(Feedback.restaurant_id == self.id).scalar()
        return avg_value or 0
    
    @property
    def total_reviews(self):
        """Get total number of order feedback items (deprecate legacy reviews)."""
        from app.models.feedback import Feedback
        from app import db
        return db.session.query(Feedback).filter(Feedback.restaurant_id == self.id).count()
    
    def get_menu_by_category(self):
        """GROUP MENU ITEMS BY CATEGORY"""
        menu_dict = {}
        for item in self.menu_items:
            if item.category not in menu_dict:
                menu_dict[item.category] = []
            menu_dict[item.category].append(item)
        return menu_dict

    # ---------------------
    # CUISINES HELPERS
    # ---------------------
    def get_cuisines(self):
        """Return cuisines as a list (empty list if none)."""
        try:
            if self.cuisines:
                data = json.loads(self.cuisines)
                if isinstance(data, list):
                    return [c for c in data if isinstance(c, str) and c.strip()]
        except Exception:
            pass
        return []

    def set_cuisines(self, cuisines_list):
        """Persist cuisines from a list of strings."""
        cuisines_clean = []
        if cuisines_list:
            for c in cuisines_list:
                if not isinstance(c, str):
                    continue
                c_stripped = c.strip()
                if c_stripped and c_stripped not in cuisines_clean:
                    cuisines_clean.append(c_stripped)
        self.cuisines = json.dumps(cuisines_clean) if cuisines_clean else None

    @property
    def cuisines_display(self):
        """Human readable cuisines string for UI."""
        cuisines = self.get_cuisines()
        return ", ".join(cuisines) if cuisines else ""
    
    def get_dietary_options(self):
        """Get available dietary options for this restaurant based on menu items."""
        dietary_options = {
            'has_vegetarian': False,
            'has_vegan': False,
            'has_guilt_free': False,
            'has_non_vegetarian': False
        }
        
        for item in self.menu_items:
            if item.is_vegetarian:
                dietary_options['has_vegetarian'] = True
            else:
                dietary_options['has_non_vegetarian'] = True
            
            if item.is_vegan:
                dietary_options['has_vegan'] = True
            
            if item.is_guilt_free:
                dietary_options['has_guilt_free'] = True
        
        return dietary_options