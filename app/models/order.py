"""
ORDER MODELS FOR STORING ORDERS AND ORDER ITEMS
"""

from datetime import datetime
from app import db

# ORDER STATUS CONSTANTS
STATUS_PENDING = 'pending'
STATUS_CONFIRMED = 'confirmed'
STATUS_PREPARING = 'preparing'
STATUS_READY = 'ready'
STATUS_COMPLETED = 'completed'
STATUS_CANCELLED = 'cancelled'

class Order(db.Model):
    """
    ORDER MODEL FOR STORING CUSTOMER ORDERS
    """
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    status = db.Column(db.String(20), default=STATUS_PENDING, index=True)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order #{self.id}>'
    
    @property
    def item_count(self):
        """GET TOTAL NUMBER OF ITEMS IN ORDER"""
        return sum(item.quantity for item in self.items)
    
    @property
    def status_display(self):
        """GET HUMAN-READABLE STATUS"""
        status_map = {
            STATUS_PENDING: 'Pending',
            STATUS_CONFIRMED: 'Confirmed',
            STATUS_PREPARING: 'Preparing',
            STATUS_READY: 'Ready for Pickup',
            STATUS_COMPLETED: 'Completed',
            STATUS_CANCELLED: 'Cancelled'
        }
        return status_map.get(self.status, self.status)
    
    def update_status(self, new_status):
        """UPDATE ORDER STATUS"""
        if new_status in [STATUS_PENDING, STATUS_CONFIRMED, STATUS_PREPARING, 
                          STATUS_READY, STATUS_COMPLETED, STATUS_CANCELLED]:
            self.status = new_status
            return True
        return False

class OrderItem(db.Model):
    """
    ORDER ITEM MODEL FOR STORING INDIVIDUAL ITEMS IN AN ORDER
    """
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # PRICE AT TIME OF ORDER
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderItem {self.menu_item_id} x{self.quantity}>'
    
    @property
    def subtotal(self):
        """CALCULATE SUBTOTAL FOR THIS ITEM"""
        return self.price * self.quantity
