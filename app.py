from flask import Flask, render_template, redirect, url_for
from config import Config
from models import db, User
from flask_login import LoginManager
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'materials'), exist_ok=True)

    # Register blueprints (will be created in next steps)
    from routes.auth import auth_bp
    from routes.collector import collector_bp
    from routes.recycler import recycler_bp
    from routes.admin import admin_bp
    from routes.main import main_bp
    
    from routes.transaction import transaction_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(collector_bp, url_prefix='/collector')
    app.register_blueprint(recycler_bp, url_prefix='/recycler')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(transaction_bp, url_prefix='/transaction')
    app.register_blueprint(main_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
