from flask import Flask, request # Добавим request для логгирования
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import config
import logging # Добавим стандартное логгирование

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    """Фабрика приложений."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    app.logger.info(f"Initializing App with '{config_name}' config")
    app.logger.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}") # Логгируем URI базы

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Регистрация Blueprints
    from .routes.settings import settings_bp
    from .routes.auth import auth_bp
    from .routes.contacts import contacts_bp

    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contacts_bp, url_prefix='/api/contacts')

    app.logger.info("Blueprints registered")

    @app.route('/health')
    def health_check():
        return "Backend OK", 200

    # Добавим простой логгер для всех запросов (опционально)
    @app.before_request
    def log_request_info():
        app.logger.debug('Headers: %s', request.headers)
        app.logger.debug('Body: %s', request.get_data())

    return app
