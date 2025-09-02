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
    feedbacks = db.relationship('Feedback', backref='restaurant', lazy='dynamic')
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'
    
    @property
    def average_rating(self):
        """CALCULATE AVERAGE RATING FOR RESTAURANT FROM BOTH REVIEWS AND ORDER FEEDBACK"""
        from sqlalchemy import func
        from app import db
        from app.models.feedback import Feedback
        
        # Get average from order feedback
        feedback_avg = db.session.query(func.avg(Feedback.rating)).filter(Feedback.restaurant_id == self.id).scalar()
        feedback_avg = feedback_avg or 0
        
        # Get average from reviews
        reviews = self.reviews.all()
        review_avg = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
        
        # Combine both ratings (give feedback more weight if available)
        if feedback_avg > 0 and review_avg > 0:
            return (feedback_avg * 2 + review_avg) / 3  # Weighted average
        elif feedback_avg > 0:
            return feedback_avg
        else:
            return review_avg
    
    @property
    def total_reviews(self):
        """GET TOTAL NUMBER OF REVIEWS AND FEEDBACK"""
        from app.models.feedback import Feedback
        from app import db
        
        review_count = self.reviews.count()
        feedback_count = db.session.query(Feedback).filter(Feedback.restaurant_id == self.id).count()
        return review_count + feedback_count
    
    def get_menu_by_category(self):
        """GROUP MENU ITEMS BY CATEGORY"""
        menu_dict = {}
        for item in self.menu_items:
            if item.category not in menu_dict:
                menu_dict[item.category] = []
            menu_dict[item.category].append(item)
        return menu_dict
