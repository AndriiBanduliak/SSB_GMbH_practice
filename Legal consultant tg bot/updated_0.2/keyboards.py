import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Tuple # Для аннотации типов

from config import Translations # Импортируем Translations для доступа к текстам кнопок

# Инициализируем логгер для этого модуля
logger = logging.getLogger(__name__)

def get_main_keyboard(lang_code: str) -> InlineKeyboardMarkup:
    """
    Возвращает основную инлайн-клавиатуру главного меню бота.
    :param lang_code: Код языка пользователя для локализации кнопок.
    :return: Объект InlineKeyboardMarkup.
    """
    # Сокращенная ссылка на функцию получения перевода
    T = lambda key: Translations.get_text(lang_code, key)
    
    keyboard = [
        [InlineKeyboardButton(T('ask_question_btn'), callback_data="ask_question")],
        [InlineKeyboardButton(T('analyze_doc_btn'), callback_data="analyze_document")],
        [InlineKeyboardButton(T('edit_doc_btn'), callback_data="edit_document")],
        [InlineKeyboardButton(T('create_request_btn'), callback_data="create_request")],
        [InlineKeyboardButton(T('create_contract_btn'), callback_data="create_contract")],
        [InlineKeyboardButton(T('info_btn'), callback_data="info")],
        [InlineKeyboardButton(T('share_contact_btn'), callback_data="request_contact")],
    ]
    logger.debug(f"Generated main keyboard for lang: {lang_code}")
    return InlineKeyboardMarkup(keyboard)

def get_back_button(lang_code: str) -> InlineKeyboardMarkup:
    """
    Возвращает инлайн-клавиатуру с одной кнопкой "Назад".
    :param lang_code: Код языка пользователя для локализации кнопки.
    :return: Объект InlineKeyboardMarkup.
    """
    keyboard = [
        [InlineKeyboardButton(Translations.get_text(lang_code, 'back_btn'), callback_data="back_to_main")]
    ]
    logger.debug(f"Generated back button for lang: {lang_code}")
    return InlineKeyboardMarkup(keyboard)

def get_cancel_button(lang_code: str) -> InlineKeyboardMarkup:
    """
    Возвращает инлайн-клавиатуру с одной кнопкой "Отмена".
    :param lang_code: Код языка пользователя для локализации кнопки.
    :return: Объект InlineKeyboardMarkup.
    """
    keyboard = [
        [InlineKeyboardButton(Translations.get_text(lang_code, 'cancel_btn'), callback_data="cancel_creation")]
    ]
    logger.debug(f"Generated cancel button for lang: {lang_code}")
    return InlineKeyboardMarkup(keyboard)

def get_contact_request_keyboard(lang_code: str) -> ReplyKeyboardMarkup:
    """
    Возвращает Reply-клавиатуру для запроса номера телефона пользователя.
    Включает кнопку "Поделиться номером" и кнопку "Назад".
    :param lang_code: Код языка пользователя для локализации кнопок.
    :return: Объект ReplyKeyboardMarkup.
    """
    T = lambda key: Translations.get_text(lang_code, key)
    keyboard = [
        [KeyboardButton(text=T('share_contact_btn'), request_contact=True)], # Кнопка запроса контакта
        [KeyboardButton(text=T('back_btn'))] # Кнопка "Назад"
    ]
    logger.debug(f"Generated contact request keyboard for lang: {lang_code}")
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_confirmation_keyboard(lang_code: str, confirm_callback: str, edit_buttons: List[Tuple[str, str]]) -> InlineKeyboardMarkup:
    """
    Генерирует универсальную инлайн-клавиатуру для подтверждения данных с опциями редактирования.
    
    :param lang_code: Код языка для локализации кнопок.
    :param confirm_callback: Callback-данные для кнопки "Подтвердить" (например, "contract_confirm_client").
    :param edit_buttons: Список кортежей, где каждый кортеж содержит:
                         (строковый ключ для получения текста кнопки из Translations,
                          строка callback_data для этой кнопки).
    :return: Объект InlineKeyboardMarkup.
    """
    T = lambda key: Translations.get_text(lang_code, key)
    
    keyboard = [
        [InlineKeyboardButton(T('confirm_btn'), callback_data=confirm_callback)]
    ]
    
    for text_key, callback_data_str in edit_buttons:
        keyboard.append([InlineKeyboardButton(T(text_key), callback_data=callback_data_str)])
        
    keyboard.append([InlineKeyboardButton(T('cancel_btn'), callback_data="cancel_creation")])
    
    logger.debug(f"Generated confirmation keyboard for lang: {lang_code} with {len(edit_buttons)} edit options.")
    return InlineKeyboardMarkup(keyboard)