from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import asc, desc


class User(db.Model):
    __tablename__ = 'users'  # Явно указываем имя таблицы
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    language = db.Column(db.String(5), default='en')
    theme = db.Column(db.String(10), default='light')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=16)

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

# ... (импорты и класс User остаются без изменений) ...
# Импортируем asc и desc для сортировки

# ... (класс User) ...


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False, index=True)  # Имя
    # Отчество (nullable=True, т.к. может не быть)
    middle_name = db.Column(db.String(100), nullable=True, index=True)
    # Фамилия (добавим, обычно нужна)
    last_name = db.Column(db.String(100), nullable=True, index=True)
    phone_number = db.Column(
        db.String(20), nullable=True, index=True)  # Телефон
    email = db.Column(db.String(120), nullable=True, index=True)      # Email
    company = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с пользователем (владельцем контакта)
    # Предполагаем, что у каждого контакта есть владелец (агент CRM)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship(
        'User', backref=db.backref('contacts', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'company': self.company,
            'notes': self.notes,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z'
        }

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name or ""}>'
