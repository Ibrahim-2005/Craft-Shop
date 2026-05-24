from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "soft"

    from .models.admin import Admin
    from .models.customer import Customer

    @login_manager.user_loader
    def load_user(user_id):
        if not user_id:
            return None
        if ":" in user_id:
            role, raw_id = user_id.split(":", 1)
            if role == "admin":
                return Admin.query.get(int(raw_id))
            if role == "customer":
                return Customer.query.get(int(raw_id))
        return Admin.query.get(int(user_id))

    from .routes.public_routes import public_bp
    from .routes.auth_routes import auth_bp
    from .routes.customer_auth_routes import customer_auth_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(customer_auth_bp)
    app.register_blueprint(auth_bp, url_prefix="/admin")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    if app.config.get("AUTO_CREATE_DB", False):
        with app.app_context():
            db.create_all()
            from .utils.schema import ensure_runtime_schema

            ensure_runtime_schema()

    return app
