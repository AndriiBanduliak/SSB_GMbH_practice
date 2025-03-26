import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла, если он есть
basedir = os.path.abspath(os.path.dirname(__file__))
# Путь к .env в корне проекта
dotenv_path = os.path.join(basedir, '..', '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Можно добавить другие общие настройки

    @staticmethod
    def init_app(app):
        pass  # Пока ничего специфичного


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + \
        os.path.join(
            basedir, 'data-dev.sqlite')  # Фоллбэк на SQLite для простоты


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Добавьте здесь настройки для продакшена (логирование, и т.д.)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
