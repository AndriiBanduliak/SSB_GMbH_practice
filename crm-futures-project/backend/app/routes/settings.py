from flask import Blueprint, request, jsonify
from .. import db
from ..models import User
# Заменяем временный ID на получение из JWT
from flask_jwt_extended import jwt_required, get_jwt_identity  # <--- Импортировать

settings_bp = Blueprint('settings', __name__)

# Убираем временный хардкод ID пользователя
# TEMP_USER_ID = 1


@settings_bp.route('/', methods=['GET'])
@jwt_required()  # <--- Добавляем декоратор для защиты
def get_settings():
    user_id = get_jwt_identity()  # <--- Получаем ID пользователя из токена
    user = User.query.get(user_id)
    if not user:
        # Эта ситуация маловероятна, если токен валиден, но для полноты
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "language": user.language,
        "theme": user.theme
    }), 200


@settings_bp.route('/', methods=['PUT'])
@jwt_required()  # <--- Добавляем декоратор для защиты
def update_settings():
    user_id = get_jwt_identity()  # <--- Получаем ID пользователя из токена
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
            print(f"Error updating settings: {e}")  # Логирование ошибки
            return jsonify({"message": "Failed to update settings", "error": str(e)}), 500
    else:
        return jsonify({"message": "No valid settings provided to update"}), 400
    
    
# Добавьте здесь эндпоинты для других настроек (профиль, уведомления и т.д.)
