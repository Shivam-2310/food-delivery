"""Order models for storing orders and order items."""

from datetime import datetime

from app import db

# Order status constants.
STATUS_PENDING = 'pending'
STATUS_CONFIRMED = 'confirmed'
STATUS_PREPARING = 'preparing'
STATUS_READY = 'ready'
STATUS_COMPLETED = 'completed'
STATUS_CANCELLED = 'cancelled'

class Order(db.Model):
    """Order model for storing customer orders."""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    status = db.Column(db.String(20), default=STATUS_PENDING, index=True)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships.
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order #{self.id}>'
    
    @property
    def item_count(self):
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items)
    
    @property
    def status_display(self):
        """Get human-readable status."""
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
        """Update order status."""
        if new_status in [STATUS_PENDING, STATUS_CONFIRMED, STATUS_PREPARING, 
                          STATUS_READY, STATUS_COMPLETED, STATUS_CANCELLED]:
            self.status = new_status
            return True
        return False

class OrderItem(db.Model):
    """Order item model for storing individual items in an order."""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at time of order.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderItem {self.menu_item_id} x{self.quantity}>'
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item."""
        return self.price * self.quantity
