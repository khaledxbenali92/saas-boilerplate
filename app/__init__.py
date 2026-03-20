"""
🚀 SaaS Boilerplate Starter
Production-ready SaaS foundation with Auth + Billing + Dashboard
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from app.config import config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()


def create_app(config_name="default"):
    app = Flask(__name__,
                template_folder="../frontend/pages",
                static_folder="../frontend/static")

    app.config.from_object(config[config_name])

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.api.routes import api_bp
    from app.dashboard.routes import dashboard_bp
    from app.billing.routes import billing_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(billing_bp, url_prefix="/billing")

    # Register main routes
    from app.main import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
