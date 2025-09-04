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
    last_order_date = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    order_items = db.relationship('OrderItem', backref='menu_item', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MenuItem {self.name}>'
    
    @property
    def is_mostly_ordered(self):
        """CHECK IF ITEM IS MOSTLY ORDERED (>10 TIMES TODAY)"""
        # Ensure we're checking today's count
        self._ensure_daily_reset()
        return self.times_ordered_today > 10
    
    def _ensure_daily_reset(self):
        """ENSURE DAILY RESET IF IT'S A NEW DAY (AUTOMATIC AT MIDNIGHT)"""
        today = datetime.utcnow().date()
        if self.last_order_date != today:
            # It's a new day - automatically reset the counter
            self.times_ordered_today = 0
            self.last_order_date = today
            # Don't commit here - let the calling function handle it
    
    def increment_daily_order_count(self, quantity=1):
        """INCREMENT DAILY ORDER COUNT WITH AUTOMATIC DAILY RESET AT MIDNIGHT"""
        today = datetime.utcnow().date()
        
        # Automatic reset if it's a new day (after 12 AM)
        if self.last_order_date != today:
            self.times_ordered_today = 0
            self.last_order_date = today
        
        # Increment the count
        self.times_ordered_today += quantity
    
    
    def reset_daily_order_count(self):
        """RESET THE DAILY ORDER COUNT"""
        self.times_ordered_today = 0
        self.last_order_date = datetime.utcnow().date()
    
