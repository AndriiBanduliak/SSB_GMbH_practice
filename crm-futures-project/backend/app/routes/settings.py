from flask import Blueprint, request, jsonify
from .. import db
from ..models import User
# Добавьте импорт для аутентификации, когда она будет готова
# from flask_jwt_extended import jwt_required, get_jwt_identity

settings_bp = Blueprint('settings', __name__)

# Временный хардкод ID пользователя для примера
# В реальном приложении нужно получать ID из токена аутентификации
TEMP_USER_ID = 1

@settings_bp.route('/', methods=['GET'])
# @jwt_required() # Раскомментируйте после настройки JWT
def get_settings():
    # user_id = get_jwt_identity() # Получение ID из токена
    user_id = TEMP_USER_ID # Временный хардкод
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "language": user.language,
        "theme": user.theme
    }), 200

@settings_bp.route('/', methods=['PUT'])
# @jwt_required()
def update_settings():
    # user_id = get_jwt_identity()
    user_id = TEMP_USER_ID # Временный хардкод
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

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
            return jsonify({
                "message": "Settings updated successfully",
                "language": user.language,
                "theme": user.theme
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to update settings", "error": str(e)}), 500
    else:
        return jsonify({"message": "No valid settings provided to update"}), 400

# Добавьте здесь эндпоинты для других настроек (профиль, уведомления и т.д.)
