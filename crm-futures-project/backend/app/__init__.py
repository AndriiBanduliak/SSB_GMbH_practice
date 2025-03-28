from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    """Фабрика приложений."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Регистрация Blueprints
    from .routes.settings import settings_bp
    from .routes.auth import auth_bp
    from .routes.contacts import contacts_bp # <--- Импорт нового блюпринта

    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contacts_bp, url_prefix='/api/contacts') # <--- Регистрация

    @app.route('/health')
    def health_check():
        return "Backend OK", 200

    return app