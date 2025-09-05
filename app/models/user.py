"""User model for authentication and authorization."""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager
from app.utils.auth_helpers import verify_reset_token as verify_token

# User role constants.
ROLE_CUSTOMER = 'customer'
ROLE_OWNER = 'owner'

class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships.
    customer_profile = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
    owner_profile = db.relationship('RestaurantOwner', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password is correct."""
        return check_password_hash(self.password_hash, password)
    
    def is_customer(self):
        """Check if user is a customer."""
        return self.role == ROLE_CUSTOMER
    
    def is_owner(self):
        """Check if user is a restaurant owner."""
        return self.role == ROLE_OWNER
        
    @staticmethod
    def verify_reset_token(token):
        """Verify password reset token."""
        user_id = verify_token(token)
        if user_id:
            return User.query.get(user_id)
        return None

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return User.query.get(int(user_id))
