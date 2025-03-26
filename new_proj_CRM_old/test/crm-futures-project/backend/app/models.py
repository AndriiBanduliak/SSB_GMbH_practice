from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users' # Явно указываем имя таблицы
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    language = db.Column(db.String(5), default='en')
    theme = db.Column(db.String(10), default='light')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        # Возвращает словарь с данными пользователя (без пароля)
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'language': self.language,
            'theme': self.theme,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z'
        }

    def __repr__(self):
        return f'<User {self.username}>'

# Добавьте другие модели: Client, Trade, Account и т.д.
# class Client(db.Model): ...
