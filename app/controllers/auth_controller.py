"""
AUTHENTICATION CONTROLLER FOR LOGIN AND PASSWORD RESET
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import db
from app.models import User, Customer, RestaurantOwner
from app.forms.auth_forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils.auth_helpers import send_password_reset_email, generate_reset_token

bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    LOGIN ROUTE FOR CUSTOMER AND RESTAURANT OWNER
    """
    if current_user.is_authenticated:
        if current_user.is_customer():
            return redirect(url_for('customer.dashboard'))
        else:
            return redirect(url_for('owner.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user or not user.check_password(form.password.data) or user.role != form.role.data:
            logger.warning(f"Failed login attempt for username: {form.username.data}")
            flash("INVALID USERNAME, PASSWORD OR ROLE. PLEASE TRY AGAIN.", "danger")
            return render_template('auth/login.html', form=form)
        
        login_user(user, remember=form.remember.data)
        logger.info(f"User {user.username} logged in successfully")
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.is_customer():
                next_page = url_for('customer.dashboard')
            else:
                next_page = url_for('owner.dashboard')
        
        flash("LOGIN SUCCESSFUL!", "success")
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """
    LOGOUT ROUTE
    """
    logger.info(f"User {current_user.username} logged out")
    logout_user()
    flash("YOU HAVE BEEN LOGGED OUT SUCCESSFULLY.", "info")
    return redirect(url_for('main.index'))

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    REQUEST PASSWORD RESET ROUTE
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_reset_token(user)
            send_password_reset_email(user, token)
            logger.info(f"Password reset requested for email: {form.email.data}")
        flash("CHECK YOUR EMAIL FOR INSTRUCTIONS TO RESET YOUR PASSWORD.", "info")
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    RESET PASSWORD ROUTE
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash("INVALID OR EXPIRED TOKEN", "danger")
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        logger.info(f"Password reset completed for user: {user.username}")
        flash("YOUR PASSWORD HAS BEEN RESET SUCCESSFULLY.", "success")
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)
