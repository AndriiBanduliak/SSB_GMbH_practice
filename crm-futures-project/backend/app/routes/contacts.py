from flask import Blueprint, request, jsonify
from sqlalchemy import asc, desc  # Импортируем функции сортировки
from .. import db
from ..models import Contact, User  # Импортируем обе модели
from flask_jwt_extended import jwt_required, get_jwt_identity

contacts_bp = Blueprint('contacts', __name__)

# Допустимые поля для сортировки (для безопасности и валидации)
ALLOWED_SORT_FIELDS = {'first_name', 'middle_name',
                       'last_name', 'phone_number', 'email', 'created_at'}
DEFAULT_SORT_FIELD = 'first_name'
DEFAULT_SORT_ORDER = 'asc'


@contacts_bp.route('/', methods=['GET'])
@jwt_required(locations=['headers'])
def get_contacts():
    """Получение списка контактов с сортировкой."""
    current_user_id = get_jwt_identity()

    # Получаем параметры сортировки из query string (?sort_by=...&sort_order=...)
    sort_by = request.args.get('sort_by', DEFAULT_SORT_FIELD).lower()
    sort_order = request.args.get('sort_order', DEFAULT_SORT_ORDER).lower()

    # Валидация параметров сортировки
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = DEFAULT_SORT_FIELD  # Возвращаемся к дефолту при неверном значении
    if sort_order not in ['asc', 'desc']:
        sort_order = DEFAULT_SORT_ORDER  # Возвращаемся к дефолту

    try:
        # Формируем базовый запрос для контактов текущего пользователя
        query = Contact.query.filter_by(owner_id=current_user_id)

        # Получаем атрибут модели для сортировки
        # getattr безопаснее прямого форматирования строки
        sort_column = getattr(Contact, sort_by, None)

        # Применяем сортировку, если атрибут найден
        if sort_column is not None:
            if sort_order == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            # Если вдруг sort_by некорректен даже после проверки (маловероятно)
            query = query.order_by(asc(getattr(Contact, DEFAULT_SORT_FIELD)))

        # Получаем все отсортированные контакты
        contacts = query.all()

        # Преобразуем в список словарей
        contacts_list = [contact.to_dict() for contact in contacts]

        return jsonify(contacts=contacts_list), 200

    except Exception as e:
        # Логирование ошибки было бы полезно здесь
        print(f"Error fetching contacts for user {current_user_id}: {e}")
        return jsonify({"message": "Failed to retrieve contacts due to server error"}), 500

# Здесь можно добавить другие эндпоинты для контактов:
# POST /api/contacts/ - создание нового контакта
# GET /api/contacts/<int:contact_id> - получение одного контакта
# PUT /api/contacts/<int:contact_id> - обновление контакта
# DELETE /api/contacts/<int:contact_id> - удаление контакта
