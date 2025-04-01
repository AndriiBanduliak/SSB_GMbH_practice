from flask import Blueprint, request, jsonify, current_app
from .. import db
from ..models import User
# Импортируем нужные функции JWT
from flask_jwt_extended import jwt_required, get_jwt_identity

# Создаем Blueprint для маршрутов настроек
settings_bp = Blueprint('settings', __name__)

# --- Хук для логгирования заголовков перед КАЖДЫМ запросом к этому блюпринту ---


@settings_bp.before_request
def log_request_headers_hook():
    current_app.logger.debug(
        f"Incoming {request.method} request to settings: {request.path}")
    if current_app.config.get('DEBUG', False):
        headers_string = "\n".join(
            [f"  {key}: {value}" for key, value in request.headers.items()])
        current_app.logger.debug(f"Request Headers:\n{headers_string}")
        # Также залогируем тело запроса здесь, если это PUT/POST
        if request.method in ['POST', 'PUT'] and request.data:
            try:
                # Попробуем декодировать как UTF-8, игнорируя ошибки, если это не текст
                body_preview = request.get_data(as_text=True)
                # Ограничим длину для лога
                current_app.logger.debug(
                    f"Request Body Preview: {body_preview[:500]}")
            except UnicodeDecodeError:
                current_app.logger.debug(
                    "Request Body: (binary data or wrong encoding)")

# --- Маршрут для получения текущих настроек пользователя ---


@settings_bp.route('/', methods=['GET'])
@jwt_required(locations=['headers'])
def get_settings():
    """Возвращает язык и тему текущего аутентифицированного пользователя."""
    current_app.logger.info(
        "--- Entered get_settings function ---")  # Лог входа в функцию
    try:
        user_id = get_jwt_identity()
        current_app.logger.debug(
            f"get_settings: JWT Identity (user_id): {user_id}")
        user = User.query.get(user_id)

        if not user:
            current_app.logger.warning(
                f"GET /settings: User not found for JWT identity: {user_id}")
            return jsonify({"message": "User associated with token not found"}), 404

        current_app.logger.info(
            f"get_settings: Found user {user.username}, returning settings.")
        return jsonify({
            "language": user.language,
            "theme": user.theme
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error in GET /settings: {e}", exc_info=True)
        return jsonify({"message": "An unexpected error occurred"}), 500

# --- Маршрут для обновления настроек пользователя ---


@settings_bp.route('/', methods=['PUT'])
@jwt_required(locations=['headers'])
def update_settings():
    """Обновляет язык и/или тему текущего аутентифицированного пользователя."""
    # --- Лог в самом начале функции ---
    user_id_from_token = get_jwt_identity()  # Получаем ID сразу для лога
    current_app.logger.info(
        f"--- Entered update_settings function for user_id: {user_id_from_token} ---")
    # Дополнительный вывод
    print(
        f"DEBUG PRINT: Entered update_settings for user_id: {user_id_from_token}")
    # ---------------------------------
    try:
        # Находим пользователя в базе данных по ID из токена
        user = User.query.get(user_id_from_token)

        # Проверка, найден ли пользователь
        if not user:
            current_app.logger.warning(
                f"PUT /settings: User not found for JWT identity: {user_id_from_token}")
            return jsonify({"message": "User associated with token not found"}), 404
        current_app.logger.debug(
            f"update_settings: Found user {user.username}")

        # Получаем данные из тела JSON запроса
        data = request.get_json()
        current_app.logger.debug(f"update_settings: Received data: {data}")
        if not data:
            current_app.logger.warning(
                f"PUT /settings: No JSON data received for user {user_id_from_token}")
            return jsonify({"message": "No input data provided in JSON body"}), 400

        updated_fields = []
        changes_to_commit = False  # Флаг, показывающий, были ли реальные изменения

        # Обновляем язык
        if 'language' in data:
            new_language = data['language']
            if new_language in ['en', 'de', 'ru']:
                if user.language != new_language:
                    current_app.logger.debug(
                        f"Updating language for user {user_id_from_token} from '{user.language}' to '{new_language}'")
                    user.language = new_language
                    updated_fields.append(f"language='{new_language}'")
                    changes_to_commit = True
                else:
                    current_app.logger.debug(
                        f"Language for user {user_id_from_token} is already '{new_language}'")
            else:
                current_app.logger.warning(
                    f"User {user_id_from_token} tried to set invalid language: {new_language}")

        # Обновляем тему
        if 'theme' in data:
            new_theme = data['theme']
            if new_theme in ['light', 'dark']:
                if user.theme != new_theme:
                    current_app.logger.debug(
                        f"Updating theme for user {user_id_from_token} from '{user.theme}' to '{new_theme}'")
                    user.theme = new_theme
                    updated_fields.append(f"theme='{new_theme}'")
                    changes_to_commit = True
                else:
                    current_app.logger.debug(
                        f"Theme for user {user_id_from_token} is already '{new_theme}'")
            else:
                current_app.logger.warning(
                    f"User {user_id_from_token} tried to set invalid theme: {new_theme}")

        # Пытаемся сохранить, только если были реальные изменения
        if changes_to_commit:
            try:
                current_app.logger.info(
                    f"Attempting to commit settings for user {user_id_from_token}: {', '.join(updated_fields)}")
                print(
                    f"DEBUG PRINT: Attempting commit for user {user_id_from_token}")

                db.session.commit()

                current_app.logger.info(
                    f"COMMIT SUCCESSFUL: Settings updated for user {user_id_from_token}")
                print(
                    f"DEBUG PRINT: Commit successful for user {user_id_from_token}")

                return jsonify({
                    "message": "Settings updated successfully",
                    "language": user.language,
                    "theme": user.theme
                }), 200

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(
                    f"DATABASE COMMIT ERROR updating settings for user {user_id_from_token}: {e}", exc_info=True)
                print(
                    f"DEBUG PRINT: Commit FAILED for user {user_id_from_token}: {e}")
                return jsonify({"message": "Database error occurred while saving settings"}), 500
        else:
            # Если не было изменений или валидных данных
            current_app.logger.info(
                f"No actual setting changes to commit for user {user_id_from_token}")
            # Возвращаем 200 OK, т.к. ошибки нет
            return jsonify({"message": "No valid settings fields provided or values unchanged"}), 200

    except Exception as e:
        # Ловим общие ошибки выполнения функции
        current_app.logger.error(
            f"Unexpected error in PUT /settings for user {user_id_from_token}: {e}", exc_info=True)
        print(f"DEBUG PRINT: Unexpected error in PUT /settings: {e}")
        return jsonify({"message": "An unexpected error occurred"}), 500
