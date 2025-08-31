"""
MAIN CONTROLLER FOR HOMEPAGE AND COMMON PAGES
"""

import logging
from flask import Blueprint, render_template, redirect, url_for

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@bp.route('/')
def index():
    """
    HOMEPAGE ROUTE
    """
    return render_template('main/index.html')

@bp.route('/about')
def about():
    """
    ABOUT PAGE ROUTE
    """
    return render_template('main/about.html')

@bp.route('/contact')
def contact():
    """
    CONTACT PAGE ROUTE
    """
    return render_template('main/contact.html')
