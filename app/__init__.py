from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from app.models import db, User
from config import config_by_name
import os

mail = Mail()
login_manager = LoginManager()

def create_app(config_name=None):
    """Application factory - OOP Design Pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name))
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for session management"""
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.main_routes import main_bp
    from app.routes.product_routes import product_bp
    from app.routes.user_routes import user_bp
    from app.routes.cart_routes import cart_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cart_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
