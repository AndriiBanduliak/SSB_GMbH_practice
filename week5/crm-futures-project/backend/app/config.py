import os
from dotenv import load_dotenv
from datetime import timedelta

# Загружаем переменные из .env файла, если он есть
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '..', '..', '.env') # Путь к .env в корне проекта
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print("Loaded environment variables from .env file") # Добавим лог загрузки
else:
    print("Warning: .env file not found")

class Config:
    # Основные настройки Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Убедимся, что бэкенд тоже видит правильный URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Настройки Flask-JWT-Extended
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'another-hard-to-guess-string'
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_CSRF_CHECK_FORM = False
    JWT_CSRF_IN_COOKIES = False
    JWT_COOKIE_CSRF_PROTECT = False
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) # Опционально

    @staticmethod
    def init_app(app):
        # Проверка наличия ключей при инициализации
        if not app.config.get('SECRET_KEY'):
             app.logger.warning('SECRET_KEY is not set!')
        if not app.config.get('JWT_SECRET_KEY'):
             app.logger.warning('JWT_SECRET_KEY is not set!')
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            app.logger.error('DATABASE_URL (SQLALCHEMY_DATABASE_URI) is not set!')
        pass


class DevelopmentConfig(Config):
    """Конфигурация для разработки."""
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1' # Читаем FLASK_DEBUG из env
    # Фоллбэк на SQLite убран, т.к. мы всегда используем MySQL с Docker
    # Если DATABASE_URL не задан, будет ошибка при запуске


class ProductionConfig(Config):
    """Конфигурация для продакшена."""
    DEBUG = False
    # В продакшенеSQLALCHEMY_DATABASE_URI должен быть задан через переменные окружения сервера

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
