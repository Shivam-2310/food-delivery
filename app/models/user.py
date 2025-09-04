"""
USER MODEL FOR AUTHENTICATION AND AUTHORIZATION
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login_manager
from app.utils.auth_helpers import verify_reset_token as verify_token

# USER ROLE CONSTANTS
ROLE_CUSTOMER = 'customer'
ROLE_OWNER = 'owner'

class User(UserMixin, db.Model):
    """
    USER MODEL FOR AUTHENTICATION AND AUTHORIZATION
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # RELATIONSHIPS
    customer_profile = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
    owner_profile = db.relationship('RestaurantOwner', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """SET USER PASSWORD"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """CHECK IF PASSWORD IS CORRECT"""
        return check_password_hash(self.password_hash, password)
    
    def is_customer(self):
        """CHECK IF USER IS A CUSTOMER"""
        return self.role == ROLE_CUSTOMER
    
    def is_owner(self):
        """CHECK IF USER IS A RESTAURANT OWNER"""
        return self.role == ROLE_OWNER
        
    @staticmethod
    def verify_reset_token(token):
        """VERIFY PASSWORD RESET TOKEN"""
        user_id = verify_token(token)
        if user_id:
            return User.query.get(user_id)
        return None

@login_manager.user_loader
def load_user(user_id):
    """LOAD USER FOR FLASK-LOGIN"""
    return User.query.get(int(user_id))
