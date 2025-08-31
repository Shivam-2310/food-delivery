"""
AUTHENTICATION HELPER FUNCTIONS
"""

import os
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, render_template, request
import logging

logger = logging.getLogger(__name__)

def generate_reset_token(user):
    """
    GENERATE PASSWORD RESET TOKEN
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user.id, salt='password-reset')

def verify_reset_token(token, expiration=3600):
    """
    VERIFY PASSWORD RESET TOKEN
    """
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
    """
    SEND PASSWORD RESET EMAIL (SIMULATION)
    
    NOTE: IN PRODUCTION, THIS WOULD SEND AN ACTUAL EMAIL.
    FOR THE ASSIGNMENT, WE SIMULATE THIS BY LOGGING THE RESET LINK.
    """
    reset_url = f"{request.host_url}auth/reset_password/{token}"
    logger.info(f"[SIMULATED EMAIL] Password reset link for {user.email}: {reset_url}")
    
    # IN A REAL APP, THIS WOULD USE AN EMAIL SERVICE
    # email_text = render_template('email/reset_password.txt', user=user, token=token)
    # email_html = render_template('email/reset_password.html', user=user, token=token)
    # send_email("Reset Your Password", user.email, email_text, email_html)
