"""Main controller for homepage and common pages."""

import logging
from flask import Blueprint, render_template, redirect, url_for

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@bp.route('/')
def index():
    """Homepage route."""
    return render_template('main/index.html')


# Disabled: About page route is not used in the frontend.
# @bp.route('/about')
# def about():
#     """About page route."""
#     return render_template('main/about.html')


# Disabled: Contact page route is not used in the frontend.
# @bp.route('/contact')
# def contact():
#     """Contact page route."""
#     return render_template('main/contact.html')
