"""Custom decorators for route authorization."""

from functools import wraps
from flask import abort
from flask_login import current_user

def customer_required(f):
    """Restrict route access to customers only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_customer():
            abort(403)  # Forbidden.
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    """Restrict route access to restaurant owners only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_owner():
            abort(403)  # Forbidden.
        return f(*args, **kwargs)
    return decorated_function
