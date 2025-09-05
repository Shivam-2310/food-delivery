"""Authentication helper functions."""

import logging
import os

from flask import current_app, render_template, request
from itsdangerous import URLSafeTimedSerializer

logger = logging.getLogger(__name__)

def generate_reset_token(user):
    """Generate password reset token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user.id, salt='password-reset')

def verify_reset_token(token, expiration=3600):
    """Verify password reset token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        user_id = serializer.loads(
            token,
            salt='password-reset',
            max_age=expiration
        )
        return user_id
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None

def send_password_reset_email(user, token):
    """Simulates by logging the reset link."""
    reset_url = f"{request.host_url}auth/reset_password/{token}"
    logger.info(f"[SIMULATED EMAIL] Password reset link for {user.email}: {reset_url}")
    
# Not used actual mailing service in this application for simplicity