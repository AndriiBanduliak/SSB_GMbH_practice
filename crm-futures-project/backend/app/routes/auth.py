from flask import Blueprint, request, jsonify
from .. import db
from ..models import User
from flask_jwt_extended import create_access_token
# import email validator library if needed: pip install email-validator
# from email_validator import validate_email, EmailNotValidError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing username, email or password"}), 400

    username = data.get('username').strip()
    email = data.get('email').strip().lower()
    password = data.get('password')

    # Простая валидация (можно улучшить)
    if len(username) < 3:
         return jsonify({"message": "Username must be at least 3 characters long"}), 400
    if len(password) < 6:
         return jsonify({"message": "Password must be at least 6 characters long"}), 400
    # try:
    #     validate_email(email) # Проверка формата email
    # except EmailNotValidError as e:
    #     return jsonify({"message": str(e)}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409 # 409 Conflict
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password) # Хешируем пароль

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201 # 201 Created
    except Exception as e:
        db.session.rollback()
        # Логирование ошибки здесь было бы полезно
        print(f"Error during registration: {e}")
        return jsonify({"message": "Failed to register user due to server error"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or (not data.get('username') and not data.get('email')) or not data.get('password'):
        return jsonify({"message": "Missing username/email or password"}), 400

    login_identifier = data.get('username') or data.get('email')
    password = data.get('password')

    user = None
    if '@' in login_identifier: # Попытка входа по email
        user = User.query.filter_by(email=login_identifier.lower()).first()
    else: # Попытка входа по username
        user = User.query.filter_by(username=login_identifier).first()

    if user and user.check_password(password):
        # Идентификационные данные верны, создаем токен
        # В identity можно поместить любую JSON-сериализуемую информацию,
        # но ID пользователя - самый частый и полезный вариант.
        access_token = create_access_token(identity=user.id)
        user_data = user.to_dict() # Получаем данные пользователя без хеша пароля
        return jsonify(access_token=access_token, user=user_data), 200
    else:
        # Неверные данные
        return jsonify({"message": "Invalid username/email or password"}), 401 # 401 Unauthorized

# Можно добавить эндпоинт /refresh для обновления токена, если нужно
# Можно добавить /logout, если используется система блокировки токенов (сложнее)