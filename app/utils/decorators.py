"""
CUSTOM DECORATORS FOR ROUTE AUTHORIZATION
"""

from functools import wraps
from flask import abort
from flask_login import current_user

def customer_required(f):
    """
    DECORATOR TO RESTRICT ROUTE ACCESS TO CUSTOMERS ONLY
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_customer():
            abort(403)  # FORBIDDEN
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    """
    DECORATOR TO RESTRICT ROUTE ACCESS TO RESTAURANT OWNERS ONLY
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_owner():
            abort(403)  # FORBIDDEN
        return f(*args, **kwargs)
    return decorated_function
