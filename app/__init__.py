"""JustEat food ordering application."""

import logging
import os

from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions.
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(test_config=None):
    """Application factory function."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuration.
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_only_for_development'),
        SQLALCHEMY_DATABASE_URI='sqlite:///justeat.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.static_folder, 'uploads')
    )
    
    if test_config is None:
        # Load instance config, if it exists.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load test config if passed.
        app.config.from_mapping(test_config)
    
    # Ensure instance folder exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Ensure upload folder exists.
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database.
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Setup login manager.
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "PLEASE LOGIN TO ACCESS THIS PAGE"
    login_manager.login_message_category = "info"
    
    # Configure logging.
    logging.basicConfig(
        filename='justeat.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints.
    from app.controllers import (
        auth_controller,
        customer_controller,
        main_controller,
        owner_controller,
    )
    app.register_blueprint(auth_controller.bp)
    app.register_blueprint(customer_controller.bp)
    app.register_blueprint(owner_controller.bp)
    app.register_blueprint(main_controller.bp)
    
    # Context processor for automatic daily reset.
    @app.before_request
    def ensure_daily_reset():
        """Ensure all menu items are checked for daily reset on every request."""
        # Skip database operations for static files and non-HTML requests.
        if request.endpoint and (
            request.endpoint.startswith('static') or 
            request.endpoint.startswith('_internal') or
            request.path.startswith('/static/')
        ):
            return
        
        try:
            from app.models.menu import MenuItem
            from datetime import datetime
            
            # Get today's date.
            today = datetime.utcnow().date()
            
            # Find all menu items that need daily reset.
            items_to_reset = MenuItem.query.filter(MenuItem.last_order_date != today).all()
            
            if items_to_reset:
                # Reset all items that need it.
                for item in items_to_reset:
                    item.times_ordered_today = 0
                    item.last_order_date = today
                
                # Commit the changes.
                db.session.commit()
        except Exception as e:
            # Do not let daily reset errors break the app.
            app.logger.warning(f"Daily reset check failed: {e}")
            # Roll back any partial changes.
            try:
                db.session.rollback()
            except:
                pass
    
    # Error handlers.
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    return app
