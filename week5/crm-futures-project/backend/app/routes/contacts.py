from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import asc, desc
from .. import db
from ..models import Contact, User
from flask_jwt_extended import jwt_required, get_jwt_identity

contacts_bp = Blueprint('contacts', __name__)

ALLOWED_SORT_FIELDS = {'first_name', 'middle_name', 'last_name', 'phone_number', 'email', 'created_at'}
DEFAULT_SORT_FIELD = 'first_name'
DEFAULT_SORT_ORDER = 'asc'

@contacts_bp.before_request
def log_contacts_request_info():
    current_app.logger.debug(f"Incoming {request.method} request to contacts BP: {request.path}")

@contacts_bp.route('/', methods=['GET'])
@jwt_required(locations=['headers'])
def get_contacts():
    """Получение списка контактов с сортировкой."""
    current_user_id = get_jwt_identity()

    sort_by = request.args.get('sort_by', DEFAULT_SORT_FIELD).lower()
    sort_order = request.args.get('sort_order', DEFAULT_SORT_ORDER).lower()

    if sort_by not in ALLOWED_SORT_FIELDS:
        current_app.logger.warning(f"Invalid sort_by field requested: {sort_by}. Falling back to default.")
        sort_by = DEFAULT_SORT_FIELD
    if sort_order not in ['asc', 'desc']:
        current_app.logger.warning(f"Invalid sort_order value requested: {sort_order}. Falling back to default.")
        sort_order = DEFAULT_SORT_ORDER

    try:
        query = Contact.query.filter_by(owner_id=current_user_id)
        sort_column = getattr(Contact, sort_by, None)

        if sort_column is not None:
            order_func = desc if sort_order == 'desc' else asc
            query = query.order_by(order_func(sort_column))
        else:
             query = query.order_by(asc(getattr(Contact, DEFAULT_SORT_FIELD)))

        contacts = query.all()
        contacts_list = [contact.to_dict() for contact in contacts]

        # current_app.logger.info(f"Fetched {len(contacts_list)} contacts for user {current_user_id}")
        return jsonify(contacts=contacts_list), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching contacts for user {current_user_id}: {e}")
        return jsonify({"message": "Failed to retrieve contacts due to server error"}), 500

# TODO: Add POST, GET (single), PUT, DELETE endpoints for contacts
