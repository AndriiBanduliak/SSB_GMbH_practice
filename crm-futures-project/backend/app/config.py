import os
from dotenv import load_dotenv
from datetime import timedelta # <-- Не забудьте импортировать timedelta, если будете использовать JWT_ACCESS_TOKEN_EXPIRES

# Загружаем переменные из .env файла, если он есть
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '..', '..', '.env') # Путь к .env в корне проекта
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class Config:
    # Основные настройки Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Настройки Flask-JWT-Extended
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'another-hard-to-guess-string'
    JWT_TOKEN_LOCATION = ["headers"] # Ожидаем токен только в заголовках Authorization: Bearer
    JWT_CSRF_CHECK_FORM = False     # Отключаем CSRF для форм (мы используем JSON API)
    JWT_CSRF_IN_COOKIES = False     # Не ищем CSRF в куках
    JWT_COOKIE_CSRF_PROTECT = False # Не включаем CSRF-защиту через куки
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1) # Опционально: Увеличить время жизни токена до 1 часа

    @staticmethod
    def init_app(app):
        # Этот метод может использоваться для инициализации, специфичной для конфигурации,
        # например, настройки логирования для ProductionConfig. Пока пустой.
        pass


class DevelopmentConfig(Config):
    """Конфигурация для разработки."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite') # Фоллбэк на SQLite для простоты, если DATABASE_URL не задан


class ProductionConfig(Config):
    """Конфигурация для продакшена."""
    DEBUG = False # Обязательно False в продакшене!
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # В продакшене стоит убедиться, что DATABASE_URL всегда задан
    # и здесь можно добавить другие настройки (например, логирование в файл, и т.д.)

# Словарь для выбора конфигурации при создании приложения
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig # По умолчанию используем конфигурацию для разработки
}