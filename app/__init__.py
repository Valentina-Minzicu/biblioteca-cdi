import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "admin.login"

def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "db.sqlite")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from . import models
    from .routes_public import public_bp
    from .routes_admin import admin_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    
    with app.app_context():
        db.create_all()
        
    return app
