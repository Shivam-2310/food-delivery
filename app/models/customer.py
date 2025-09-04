"""
CUSTOMER MODEL FOR STORING CUSTOMER INFORMATION
"""

import json
from datetime import datetime
from app import db

class Customer(db.Model):
    """
    CUSTOMER MODEL FOR STORING CUSTOMER INFORMATION AND PREFERENCES
    """
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(15))
    preferences = db.Column(db.Text)  # STORED AS JSON
    dietary_restrictions = db.Column(db.Text)  # STORED AS JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    orders = db.relationship('Order', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='customer', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.name}>'
    
    def get_preferences(self):
        """GET CUSTOMER PREFERENCES AS DICT"""
        if not self.preferences:
            return {}
        return json.loads(self.preferences)
    
    def set_preferences(self, preferences_dict):
        """SET CUSTOMER PREFERENCES FROM DICT"""
        self.preferences = json.dumps(preferences_dict)
    
    def get_dietary_restrictions(self):
        """GET CUSTOMER DIETARY RESTRICTIONS AS LIST"""
        if not self.dietary_restrictions:
            return []
        return json.loads(self.dietary_restrictions)
    
    def set_dietary_restrictions(self, restrictions_list):
        """SET CUSTOMER DIETARY RESTRICTIONS FROM LIST"""
        self.dietary_restrictions = json.dumps(restrictions_list)
    
    def add_to_favorites(self, restaurant_id):
        """ADD RESTAURANT TO FAVORITES"""
        prefs = self.get_preferences()
        if 'favorite_restaurants' not in prefs:
            prefs['favorite_restaurants'] = []
        
        if restaurant_id not in prefs['favorite_restaurants']:
            prefs['favorite_restaurants'].append(restaurant_id)
            self.set_preferences(prefs)
            return True
        return False
    
    def remove_from_favorites(self, restaurant_id):
        """REMOVE RESTAURANT FROM FAVORITES"""
        prefs = self.get_preferences()
        if 'favorite_restaurants' in prefs and restaurant_id in prefs['favorite_restaurants']:
            prefs['favorite_restaurants'].remove(restaurant_id)
            self.set_preferences(prefs)
            return True
        return False
    
    def is_favorite(self, restaurant_id):
        """CHECK IF RESTAURANT IS IN FAVORITES"""
        prefs = self.get_preferences()
        return 'favorite_restaurants' in prefs and restaurant_id in prefs['favorite_restaurants']
