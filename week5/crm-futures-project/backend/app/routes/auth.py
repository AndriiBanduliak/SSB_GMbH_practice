from flask import Blueprint, request, jsonify, current_app
from .. import db
from ..models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# from email_validator import validate_email, EmailNotValidError # Если нужна валидация email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing username, email or password"}), 400

    username = data.get('username').strip()
    email = data.get('email').strip().lower()
    password = data.get('password')

    if len(username) < 3:
         return jsonify({"message": "Username must be at least 3 characters long"}), 400
    if len(password) < 6:
         return jsonify({"message": "Password must be at least 6 characters long"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        current_app.logger.info(f"User registered: {username}")
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during registration for {username}: {e}")
        return jsonify({"message": "Failed to register user due to server error"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or (not data.get('username') and not data.get('email')) or not data.get('password'):
        return jsonify({"message": "Missing username/email or password"}), 400

    login_identifier = data.get('username') or data.get('email')
    password = data.get('password')

    user = None
    if '@' in login_identifier:
        user = User.query.filter_by(email=login_identifier.lower()).first()
    else:
        user = User.query.filter_by(username=login_identifier).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        user_data = user.to_dict()
        current_app.logger.info(f"User logged in: {user.username} (ID: {user.id})")
        return jsonify(access_token=access_token, user=user_data), 200
    else:
        current_app.logger.warning(f"Failed login attempt for: {login_identifier}")
        return jsonify({"message": "Invalid username/email or password"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required(locations=['headers'])
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        current_app.logger.warning(f"User not found for JWT identity: {user_id}")
        return jsonify({"message": "User not found for token"}), 404
    # current_app.logger.info(f"Fetched /me for user: {user.username}") # Можно добавить лог, если нужно
    return jsonify(user=user.to_dict()), 200

