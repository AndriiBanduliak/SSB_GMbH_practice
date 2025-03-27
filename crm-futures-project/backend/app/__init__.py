from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import config # Импортируем словарь конфигураций
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    """Фабрика приложений."""
    app = Flask(__name__)
    app.config.from_object(config[config_name]) # Загружаем конфиг из config.py
    config[config_name].init_app(app) # Инициализация специфичная для конфига (если есть)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # Разрешаем CORS для /api

    # Регистрация Blueprints (маршрутов)
    from .routes.settings import settings_bp
    from .routes.auth import auth_bp # Раскомментируйте, когда добавите аутентификацию

    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/health')
    def health_check():
        return "Backend OK", 200

    return app
