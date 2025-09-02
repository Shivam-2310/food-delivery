"""
JUSTEAT FOOD ORDERING APPLICATION
"""

import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import logging

# INITIALIZE EXTENSIONS
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(test_config=None):
    """
    APPLICATION FACTORY FUNCTION
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # CONFIGURATION
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_only_for_development'),
        SQLALCHEMY_DATABASE_URI='sqlite:///justeat.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.static_folder, 'uploads')
    )
    
    if test_config is None:
        # LOAD INSTANCE CONFIG, IF IT EXISTS
        app.config.from_pyfile('config.py', silent=True)
    else:
        # LOAD TEST CONFIG IF PASSED
        app.config.from_mapping(test_config)
    
    # ENSURE INSTANCE FOLDER EXISTS
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # ENSURE UPLOAD FOLDER EXISTS
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # INITIALIZE DATABASE
    db.init_app(app)
    migrate.init_app(app, db)
    
    # SETUP LOGIN MANAGER
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "PLEASE LOGIN TO ACCESS THIS PAGE"
    login_manager.login_message_category = "info"
    
    # CONFIGURE LOGGING
    logging.basicConfig(
        filename='justeat.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # REGISTER BLUEPRINTS
    from app.controllers import auth_controller, customer_controller, owner_controller, main_controller
    app.register_blueprint(auth_controller.bp)
    app.register_blueprint(customer_controller.bp)
    app.register_blueprint(owner_controller.bp)
    app.register_blueprint(main_controller.bp)
    
    # ERROR HANDLERS
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    return app
