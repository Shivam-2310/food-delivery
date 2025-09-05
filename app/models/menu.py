"""Menu item model."""

from datetime import datetime
from app import db

class MenuItem(db.Model):
    """Menu item model for storing food items."""
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
    last_order_date = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships.
    order_items = db.relationship('OrderItem', backref='menu_item', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MenuItem {self.name}>'
    
    @property
    def is_mostly_ordered(self):
        """Check if item is mostly ordered (>10 times today)."""
        # Ensure we're checking today's count.
        self._ensure_daily_reset()
        return self.times_ordered_today > 10
    
    def _ensure_daily_reset(self):
        """Ensure daily reset if it's a new day (automatic at midnight)."""
        today = datetime.utcnow().date()
        if self.last_order_date != today:
            # It is a new day – automatically reset the counter.
            self.times_ordered_today = 0
            self.last_order_date = today
    
    def increment_daily_order_count(self, quantity=1):
        """Increment daily order count with automatic daily reset at midnight."""
        today = datetime.utcnow().date()
        
        # Automatic reset if it's a new day (after 12 AM).
        if self.last_order_date != today:
            self.times_ordered_today = 0
            self.last_order_date = today
        
        # Increment the count.
        self.times_ordered_today += quantity
    
    
    def reset_daily_order_count(self):
        """Reset the daily order count."""
        self.times_ordered_today = 0
        self.last_order_date = datetime.utcnow().date()
    
    @property
    def average_rating(self):
        """Calculate average rating for this menu item."""
        from sqlalchemy import func
        from app import db
        from app.models.dish_rating import DishRating
        avg_value = db.session.query(func.avg(DishRating.rating)).filter(
            DishRating.menu_item_id == self.id
        ).scalar()
        return round(avg_value, 1) if avg_value else 0
    
    @property
    def total_ratings(self):
        """Get total number of ratings for this menu item."""
        from app.models.dish_rating import DishRating
        from app import db
        return db.session.query(DishRating).filter(
            DishRating.menu_item_id == self.id
        ).count()
    
