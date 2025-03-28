from flask import Blueprint, request, jsonify
from .. import db
from ..models import User
# Импортируем нужные функции JWT
from flask_jwt_extended import jwt_required, get_jwt_identity

settings_bp = Blueprint('settings', __name__)

# --- Хук для логгирования заголовков перед КАЖДЫМ запросом к этому блюпринту ---
@settings_bp.before_request
def log_request_headers_hook():
    # Этот код выполнится перед каждым GET или PUT к /api/settings/
    # и ДО того, как сработает декоратор @jwt_required
    print("---")
    print(f"Incoming {request.method} request to {request.path}")
    print("Headers:")
    # Выводим заголовки в удобном формате
    for header, value in request.headers.items():
        print(f"  {header}: {value}")
    print("---")
# -----------------------------------------------------------------------------

@settings_bp.route('/', methods=['GET'])
# Явно указываем, что токен ожидается ТОЛЬКО в заголовках
@jwt_required(locations=['headers'])
def get_settings():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found for token"}), 404 # Уточним сообщение

    return jsonify({
        "language": user.language,
        "theme": user.theme
    }), 200


@settings_bp.route('/', methods=['PUT'])
# Явно указываем, что токен ожидается ТОЛЬКО в заголовках
@jwt_required(locations=['headers'])
def update_settings():
    # Логгирование заголовков уже произошло в before_request хуке
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found for token"}), 404 # Уточним сообщение

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    updated = False
    if 'language' in data and data['language'] in ['en', 'de', 'ru']:
        user.language = data['language']
        updated = True
    if 'theme' in data and data['theme'] in ['light', 'dark']:
        user.theme = data['theme']
        updated = True

    if updated:
        try:
            db.session.commit()
            # Логгируем успешное обновление
            print(f"User {user_id} updated settings: lang={user.language}, theme={user.theme}")
            return jsonify({
                "message": "Settings updated successfully",
                "language": user.language,
                "theme": user.theme
            }), 200
        except Exception as e:
            db.session.rollback()
            # Логируем ошибку базы данных
            print(f"DATABASE ERROR updating settings for user {user_id}: {e}")
            return jsonify({"message": "Database error during settings update"}), 500 # Уточним сообщение
    else:
        # Этот блок вряд ли должен достигаться при текущей логике,
        # но если данные некорректны, вернем 400
        return jsonify({"message": "No valid settings data found in request"}), 400

# Другие эндпоинты (если будут)