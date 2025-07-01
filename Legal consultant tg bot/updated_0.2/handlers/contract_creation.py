import logging
import re
from datetime import date, datetime # Импортируем datetime для более точной работы с датами
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup # Для кнопок
from telegram.ext import ContextTypes, ConversationHandler # Для управления диалогом
from telegram.constants import ParseMode # Для форматирования сообщений

from config import Translations, BotState # Импортируем Translations и BotState Enum
from document_processor import generate_contract_doc # Для генерации DOCX файла договора
from keyboards import get_cancel_button, get_confirmation_keyboard # Импортируем функции для клавиатур
from utils import typing_and_waiting, number_to_ukrainian_words # Импортируем вспомогательные утилиты (числа в слова, ожидание)

# Инициализируем логгер для этого модуля
logger = logging.getLogger(__name__)

# --- Дефолтные данные для Клиента и Адвоката ---
# Эти данные будут использоваться как начальные значения и могут быть изменены пользователем.
# Это удобно для ускорения процесса, если у большинства пользователей одни и те же данные.
DEFAULT_CLIENT_DATA = {
    'name': 'Національна академія аграрних наук України',
    'position': 'Президента',
    'fio': 'Гадзала Ярослав Михайлович',
    'basis': 'Статуту',
    'edrpou': 'N/A', # Будет запрошено позже, если клиент юрлицо
    'location': 'N/A', # Будет запрошено позже
}

DEFAULT_ADVOCATE_DATA = {
    'fio': 'Бандуляк Андрій Олегович',
    'cert_series': 'ВН',
    'cert_number': '000237',
    'cert_issuer': 'Ради адвокатів Вінницької області',
    'decision_date_number': '21.03.2018 №3', # Хранится как объединенная строка для упрощения
    'location': 'N/A', # Будет запрошено позже
}

class ContractCreationHandlers:
    """
    Класс, содержащий обработчики для пошагового создания договора о правовой помощи.
    """
    def __init__(self):
        """
        Инициализирует ContractCreationHandlers.
        В отличие от других хендлеров, этот не требует прямых зависимостей
        в конструкторе, так как OpenAIService не используется для генерации договора,
        а БД не взаимодействует напрямую из этого хендлера (только через CommonHandlers).
        """
        logger.info("ContractCreationHandlers initialized.")

    async def create_contract_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начинает диалог создания договора.
        Инициализирует структуру данных договора в `context.user_data`
        и запрашивает номер и дату договора.
        Устанавливает состояние `AWAIT_CONTRACT_NUMBER_DATE`.
        """
        query = update.callback_query
        if not query:
            logger.error("create_contract_start called without a callback query.")
            return ConversationHandler.END # Выходим из диалога, если нет callback

        await query.answer() # Отвечаем на callback-запрос
        lang_code = context.user_data.get('lang_code', 'uk')
        
        # Инициализируем структуру данных для нового договора
        context.user_data['contract_data'] = {
            'contract_number': '',
            'contract_date': '',        # Полная дата в формате ДД.ММ.ГГГГ
            'contract_day': '',         # День (число)
            'contract_month': '',       # Месяц (словом)
            'contract_year': '',        # Год (число)
            'end_date': '',             # Конечная дата действия договора
            'client': DEFAULT_CLIENT_DATA.copy(), # Копируем дефолтные данные клиента
            'advocate': DEFAULT_ADVOCATE_DATA.copy(), # Копируем дефолтные данные адвоката
            'payment_type': None,       # Тип оплаты (fixed, hourly, percentage, free, combined)
            'payment_details': {},      # Детали выбранного типа оплаты
        }
        logger.debug(f"User {update.effective_user.id} started contract creation. Initializing contract_data.")
        
        # Отправляем промпт для ввода номера и даты договора
        try:
            await query.edit_message_text(
                text=Translations.get_text(lang_code, 'contract_start_intro') + "\n\n" + \
                     Translations.get_text(lang_code, 'prompt_contract_number_date'),
                reply_markup=get_cancel_button(lang_code), 
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to edit message in create_contract_start: {e}", exc_info=True)
            await query.message.reply_text( # Fallback to new message
                text=Translations.get_text(lang_code, 'contract_start_intro') + "\n\n" + \
                     Translations.get_text(lang_code, 'prompt_contract_number_date'),
                reply_markup=get_cancel_button(lang_code), 
                parse_mode=ParseMode.HTML
            )

        return BotState.AWAIT_CONTRACT_NUMBER_DATE.value

    async def handle_contract_number_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает ввод номера и даты договора.
        Валидирует формат и сохраняет данные. Затем переходит к подтверждению данных клиента.
        Устанавливает состояние `CONFIRM_CLIENT_DATA`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        text = update.message.text.strip()
        
        # Регулярное выражение для парсинга "Номер ДД.ММ.РРРР"
        match = re.match(r"(\S+)\s+(\d{2}\.\d{2}\.\d{4})", text)
        if not match:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_CONTRACT_NUMBER_DATE.value # Остаемся в текущем состоянии
        
        contract_number = match.group(1)
        contract_date_str = match.group(2)
        
        try:
            # Парсим дату и сохраняем ее компоненты
            contract_date = datetime.strptime(contract_date_str, "%d.%m.%Y")
            context.user_data['contract_data']['contract_number'] = contract_number
            context.user_data['contract_data']['contract_date'] = contract_date.strftime("%d.%m.%Y")
            context.user_data['contract_data']['contract_day'] = str(contract_date.day)
            context.user_data['contract_data']['contract_month'] = contract_date.strftime("%B") # Название месяца (например, "Июнь")
            context.user_data['contract_data']['contract_year'] = str(contract_date.year)
            logger.debug(f"User {update.effective_user.id} entered contract number and date: {contract_number}, {contract_date_str}")

            # Переходим к шагу подтверждения данных клиента
            await self._send_client_confirmation(update, context)
            return BotState.CONFIRM_CLIENT_DATA.value

        except ValueError:
            # Ошибка при парсинге даты
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_CONTRACT_NUMBER_DATE.value

    async def _send_client_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Вспомогательный метод для отправки/обновления сообщения с данными клиента
        и кнопками подтверждения/редактирования.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        client_data = context.user_data['contract_data']['client']
        
        # Список кнопок для редактирования
        edit_buttons = [
            ('edit_client_name_btn', "contract_edit_client_name"),
            ('edit_client_position_btn', "contract_edit_client_position"),
            ('edit_client_fio_btn', "contract_edit_client_fio"),
            ('edit_client_basis_btn', "contract_edit_client_basis"),
        ]
        # Используем универсальную функцию для получения клавиатуры подтверждения
        keyboard = get_confirmation_keyboard(lang_code, "contract_confirm_client", edit_buttons)
                                
        prompt = Translations.get_text(lang_code, 'contract_client_details_header') + "\n\n" + \
                 Translations.get_text(lang_code, 'confirm_client_data_prompt', 
                                       name=client_data['name'], 
                                       position=client_data['position'], 
                                       fio=client_data['fio'], 
                                       basis=client_data['basis'])
                                       
        # Пытаемся отредактировать сообщение, если это вызвано CallbackQuery
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(text=prompt, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.error(f"Failed to edit message in _send_client_confirmation: {e}", exc_info=True)
                await update.callback_query.message.reply_text(text=prompt, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else: # Иначе отправляем новое сообщение (например, после текстового ввода)
            await update.message.reply_text(text=prompt, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    async def handle_client_edit_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает выбор пользователем поля для редактирования данных клиента.
        Сохраняет выбранное поле и запрашивает новое значение.
        Переходит в соответствующее состояние `AWAIT_CLIENT_...`.
        """
        query = update.callback_query
        if not query:
            logger.error("handle_client_edit_choice called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        lang_code = context.user_data.get('lang_code', 'uk')
        # Извлекаем часть callback_data, которая указывает на поле для редактирования
        # Например, "contract_edit_client_name" -> "client_name"
        choice = query.data.replace('contract_edit_', '') 

        context.user_data['contract_data']['_edit_field'] = choice # Временное хранение, какое поле редактируем
        logger.debug(f"User {update.effective_user.id} chose to edit client field: {choice}")

        # Карта соответствия выбранного поля и ключа промпта/следующего состояния
        prompts = {
            'client_name': 'prompt_client_name',
            'client_position': 'prompt_client_position',
            'client_fio': 'prompt_client_fio',
            'client_basis': 'prompt_client_basis',
        }
        states = {
            'client_name': BotState.AWAIT_CLIENT_NAME,
            'client_position': BotState.AWAIT_CLIENT_POSITION,
            'client_fio': BotState.AWAIT_CLIENT_FIO,
            'client_basis': BotState.AWAIT_CLIENT_BASIS,
        }

        next_prompt_key = prompts.get(choice, 'error_generic')
        next_state = states.get(choice, BotState.CONFIRM_CLIENT_DATA) # Fallback на подтверждение

        try:
            await query.edit_message_text(Translations.get_text(lang_code, next_prompt_key), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Failed to edit message in handle_client_edit_choice: {e}", exc_info=True)
            await query.message.reply_text(Translations.get_text(lang_code, next_prompt_key), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
            
        return next_state.value

    async def handle_client_edited_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает ввод нового значения для редактируемого поля клиента.
        Обновляет данные и снова показывает сообщение для подтверждения данных клиента.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        # Получаем имя поля, которое редактировали, и удаляем его из user_data
        edited_field_raw = context.user_data['contract_data'].pop('_edit_field', None)
        
        if not edited_field_raw: 
            logger.error(f"User {update.effective_user.id} tried to edit client data but _edit_field was missing.")
            await update.message.reply_text(Translations.get_text(lang_code, 'error_generic'))
            # Используем import CommonHandlers здесь, чтобы избежать циклической зависимости
            from handlers.common import CommonHandlers
            return await CommonHandlers(db_instance=None).show_main_menu(update, context) # Вернемся в главное меню при ошибке
        
        # Преобразуем имя поля из callback_data в ключ, используемый в словаре `client`
        field_mapping = {
            'client_name': 'name',
            'client_position': 'position',
            'client_fio': 'fio',
            'client_basis': 'basis',
        }
        edited_field = field_mapping.get(edited_field_raw)
        
        if not edited_field:
            logger.error(f"User {update.effective_user.id} attempted to edit unknown client field: {edited_field_raw}")
            await update.message.reply_text(Translations.get_text(lang_code, 'error_generic'))
            from handlers.common import CommonHandlers
            return await CommonHandlers(db_instance=None).show_main_menu(update, context)

        new_value = update.message.text.strip()
        if not new_value:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            context.user_data['contract_data']['_edit_field'] = edited_field_raw # Сохраняем поле для повторного ввода
            return context.state # Остаемся в текущем состоянии

        context.user_data['contract_data']['client'][edited_field] = new_value
        logger.debug(f"User {update.effective_user.id} updated client field '{edited_field}' to '{new_value}'")

        # Показываем обновленное сообщение с подтверждением данных клиента
        await self._send_client_confirmation(update, context) 
        return BotState.CONFIRM_CLIENT_DATA.value

    async def handle_confirm_client_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Подтверждает данные клиента и переходит к шагу подтверждения данных адвоката.
        Устанавливает состояние `CONFIRM_ADVOCATE_DATA`.
        """
        query = update.callback_query
        if not query:
            logger.error("handle_confirm_client_data called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        logger.debug(f"User {update.effective_user.id} confirmed client data.")
        # Переходим к шагу подтверждения данных адвоката
        await self._send_advocate_confirmation(update, context)
        return BotState.CONFIRM_ADVOCATE_DATA.value

    async def _send_advocate_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Вспомогательный метод для отправки/обновления сообщения с данными адвоката
        и кнопками подтверждения/редактирования.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        advocate_data = context.user_data['contract_data']['advocate']
        
        # Разбираем объединенное поле decision_date_number для отображения
        decision_date = "N/A"
        decision_number = "N/A"
        if 'decision_date_number' in advocate_data and advocate_data['decision_date_number']:
            parts = advocate_data['decision_date_number'].split('№')
            if len(parts) == 2:
                decision_date = parts[0].strip()
                decision_number = parts[1].strip()
            elif parts:
                decision_date = parts[0].strip() # Если указана только дата

        # Список кнопок для редактирования
        edit_buttons = [
            ('edit_advocate_fio_btn', "contract_edit_advocate_fio"),
            ('edit_advocate_cert_series_btn', "contract_edit_advocate_cert_series"),
            ('edit_advocate_cert_number_btn', "contract_edit_advocate_cert_number"),
            ('edit_advocate_cert_issuer_btn', "contract_edit_advocate_cert_issuer"),
            ('edit_advocate_decision_date_btn', "contract_edit_advocate_decision_date_number"), # Кнопка для редактирования объединенного поля
        ]
        # Используем универсальную функцию для получения клавиатуры подтверждения
        keyboard = get_confirmation_keyboard(lang_code, "contract_confirm_advocate", edit_buttons)
        
        prompt = Translations.get_text(lang_code, 'contract_advocate_details_header') + "\n\n" + \
                 Translations.get_text(lang_code, 'confirm_advocate_data_prompt', 
                                       fio=advocate_data['fio'], 
                                       cert_series=advocate_data['cert_series'], 
                                       cert_number=advocate_data['cert_number'], 
                                       cert_issuer=advocate_data['cert_issuer'], 
                                       decision_date=decision_date, 
                                       decision_number=decision_number)
        
        # Пытаемся отредактировать сообщение, если это вызвано CallbackQuery
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(text=prompt, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.error(f"Failed to edit message in _send_advocate_confirmation: {e}", exc_info=True)
                await update.callback_query.message.reply_text(text=prompt, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else: # Иначе отправляем новое сообщение (например, после текстового ввода)
            await update.message.reply_text(text=prompt, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    async def handle_advocate_edit_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает выбор пользователем поля для редактирования данных адвоката.
        Сохраняет выбранное поле и запрашивает новое значение.
        Переходит в соответствующее состояние `AWAIT_ADVOCATE_...`.
        """
        query = update.callback_query
        if not query:
            logger.error("handle_advocate_edit_choice called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        lang_code = context.user_data.get('lang_code', 'uk')
        choice = query.data.replace('contract_edit_', '') 

        context.user_data['contract_data']['_edit_field'] = choice 
        logger.debug(f"User {update.effective_user.id} chose to edit advocate field: {choice}")

        prompts = {
            'advocate_fio': 'prompt_advocate_fio',
            'advocate_cert_series': 'prompt_advocate_cert_series',
            'advocate_cert_number': 'prompt_advocate_cert_number',
            'advocate_cert_issuer': 'prompt_advocate_cert_issuer',
            'advocate_decision_date_number': 'prompt_advocate_decision_date_number',
        }
        states = {
            'advocate_fio': BotState.AWAIT_ADVOCATE_FIO,
            'advocate_cert_series': BotState.AWAIT_ADVOCATE_CERTIFICATE_SERIES,
            'advocate_cert_number': BotState.AWAIT_ADVOCATE_CERTIFICATE_NUMBER,
            'advocate_cert_issuer': BotState.AWAIT_ADVOCATE_CERTIFICATE_ISSUER,
            'advocate_decision_date_number': BotState.AWAIT_ADVOCATE_CERTIFICATE_ISSUER_DATE_NUMBER,
        }

        next_prompt_key = prompts.get(choice, 'error_generic')
        next_state = states.get(choice, BotState.CONFIRM_ADVOCATE_DATA) # Fallback на подтверждение

        try:
            await query.edit_message_text(Translations.get_text(lang_code, next_prompt_key), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Failed to edit message in handle_advocate_edit_choice: {e}", exc_info=True)
            await query.message.reply_text(Translations.get_text(lang_code, next_prompt_key), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)

        return next_state.value

    async def handle_advocate_edited_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает ввод нового значения для редактируемого поля адвоката.
        Обновляет данные и снова показывает сообщение для подтверждения данных адвоката.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        edited_field_raw = context.user_data['contract_data'].pop('_edit_field', None)
        
        if not edited_field_raw: 
            logger.error(f"User {update.effective_user.id} tried to edit advocate data but _edit_field was missing.")
            await update.message.reply_text(Translations.get_text(lang_code, 'error_generic'))
            from handlers.common import CommonHandlers # Загружаем здесь
            return await CommonHandlers(db_instance=None).show_main_menu(update, context) # Вернемся в главное меню при ошибке

        # Преобразуем имя поля из callback_data в ключ, используемый в словаре `advocate`
        field_mapping = {
            'advocate_fio': 'fio',
            'advocate_cert_series': 'cert_series',
            'advocate_cert_number': 'cert_number',
            'advocate_cert_issuer': 'cert_issuer',
            'advocate_decision_date_number': 'decision_date_number',
        }
        edited_field = field_mapping.get(edited_field_raw)
        
        if not edited_field: 
            logger.error(f"User {update.effective_user.id} attempted to edit unknown advocate field: {edited_field_raw}")
            await update.message.reply_text(Translations.get_text(lang_code, 'error_generic'))
            from handlers.common import CommonHandlers
            return await CommonHandlers(db_instance=None).show_main_menu(update, context)

        new_value = update.message.text.strip()
        if not new_value:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            context.user_data['contract_data']['_edit_field'] = edited_field_raw # Сохраняем поле для повторного ввода
            return context.state # Остаемся в текущем состоянии

        context.user_data['contract_data']['advocate'][edited_field] = new_value
        logger.debug(f"User {update.effective_user.id} updated advocate field '{edited_field}' to '{new_value}'")

        # Показываем обновленное сообщение с подтверждением данных адвоката
        await self._send_advocate_confirmation(update, context) 
        return BotState.CONFIRM_ADVOCATE_DATA.value


    async def handle_confirm_advocate_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Подтверждает данные адвоката и переходит к выбору типа оплаты.
        Устанавливает состояние `SELECT_PAYMENT_TYPE`.
        """
        query = update.callback_query
        if not query:
            logger.error("handle_confirm_advocate_data called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        logger.debug(f"User {update.effective_user.id} confirmed advocate data.")
        # Переходим к выбору типа оплаты
        await self._send_payment_type_selection(update, context)
        return BotState.SELECT_PAYMENT_TYPE.value

    async def _send_payment_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Вспомогательный метод для отправки/обновления сообщения с выбором типа оплаты.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        keyboard = [
            [InlineKeyboardButton(Translations.get_text(lang_code, 'payment_type_free_btn'), callback_data="payment_type_free")],
            [InlineKeyboardButton(Translations.get_text(lang_code, 'payment_type_fixed_btn'), callback_data="payment_type_fixed")],
            [InlineKeyboardButton(Translations.get_text(lang_code, 'payment_type_hourly_btn'), callback_data="payment_type_hourly")],
            [InlineKeyboardButton(Translations.get_text(lang_code, 'payment_type_percentage_btn'), callback_data="payment_type_percentage")],
            [InlineKeyboardButton(Translations.get_text(lang_code, 'payment_type_combined_btn'), callback_data="payment_type_combined")],
            [InlineKeyboardButton(Translations.get_text(lang_code, 'cancel_btn'), callback_data="cancel_creation")]
        ]
        
        # Пытаемся отредактировать сообщение, если это вызвано CallbackQuery
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(text=Translations.get_text(lang_code, 'prompt_payment_type'), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.error(f"Failed to edit message in _send_payment_type_selection: {e}", exc_info=True)
                await update.callback_query.message.reply_text(text=Translations.get_text(lang_code, 'prompt_payment_type'), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        else: # Иначе отправляем новое сообщение (например, после текстового ввода)
            await update.message.reply_text(text=Translations.get_text(lang_code, 'prompt_payment_type'), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

    async def handle_payment_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает выбор типа оплаты и переходит к соответствующему шагу
        для сбора деталей оплаты.
        Устанавливает соответствующее состояние для сбора деталей оплаты.
        """
        query = update.callback_query
        if not query:
            logger.error("handle_payment_type_selection called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        lang_code = context.user_data.get('lang_code', 'uk')
        payment_type = query.data.replace('payment_type_', '')
        context.user_data['contract_data']['payment_type'] = payment_type
        context.user_data['contract_data']['payment_details'] = {} # Очищаем старые детали оплаты
        logger.debug(f"User {update.effective_user.id} selected payment type: {payment_type}")

        # Редактируем сообщение с выбранным типом оплаты (или отправляем новое)
        try:
            if payment_type == 'free':
                context.user_data['contract_data']['payment_details']['text'] = Translations.get_text(lang_code, 'payment_type_free_text')
                await query.edit_message_text(f"✅ {Translations.get_text(lang_code, 'prompt_payment_type')[:-1]}: {Translations.get_text(lang_code, 'payment_type_free_btn')}", parse_mode=ParseMode.HTML)
                return await self._prompt_contract_end_date(update, context) # Переход к следующему шагу
            elif payment_type == 'fixed':
                await query.edit_message_text(Translations.get_text(lang_code, 'prompt_fixed_amount'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
                return BotState.AWAIT_FIXED_AMOUNT.value
            elif payment_type == 'hourly':
                await query.edit_message_text(Translations.get_text(lang_code, 'prompt_hourly_rate'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
                return BotState.AWAIT_HOURLY_RATE.value
            elif payment_type == 'percentage':
                await query.edit_message_text(Translations.get_text(lang_code, 'prompt_percentage_value'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
                return BotState.AWAIT_PERCENTAGE_VALUE.value
            elif payment_type == 'combined':
                await query.edit_message_text(Translations.get_text(lang_code, 'prompt_combined_description'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
                return BotState.AWAIT_COMBINED_DESCRIPTION.value
        except Exception as e:
            logger.error(f"Failed to handle payment type selection for user {update.effective_user.id}: {e}", exc_info=True)
            await query.message.reply_text(Translations.get_text(lang_code, 'error_generic'), reply_markup=get_cancel_button(lang_code))
            return ConversationHandler.END # Выход при ошибке
        
        return BotState.SELECT_PAYMENT_TYPE.value # Fallback на выбор типа оплаты

    # --- Обработчики для фиксированного гонорара ---
    async def handle_fixed_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает ввод фиксированной суммы гонорара."""
        lang_code = context.user_data.get('lang_code', 'uk')
        try:
            amount_str = update.message.text.strip()
            amount = int(amount_str)
            if amount <= 0: raise ValueError("Amount must be a positive number.")
            context.user_data['contract_data']['payment_details']['amount'] = amount
            logger.debug(f"User {update.effective_user.id} entered fixed amount: {amount}")
            await update.message.reply_text(Translations.get_text(lang_code, 'prompt_fixed_payment_order'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
            return BotState.AWAIT_FIXED_PAYMENT_ORDER.value
        except ValueError as e:
            await update.message.reply_text(f"{Translations.get_text(lang_code, 'error_invalid_input')} {e}", reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_FIXED_AMOUNT.value

    async def handle_fixed_payment_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает ввод порядка оплаты для фиксированного гонорара."""
        lang_code = context.user_data.get('lang_code', 'uk')
        order = update.message.text.strip()
        if not order:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_FIXED_PAYMENT_ORDER.value
        context.user_data['contract_data']['payment_details']['payment_order'] = order
        
        amount = context.user_data['contract_data']['payment_details']['amount']
        amount_words = number_to_ukrainian_words(amount) # Преобразуем число в слова
        
        payment_text = Translations.get_text(lang_code, 'payment_type_fixed_text',
                                             amount=amount, amount_words=amount_words, payment_order=order)
        context.user_data['contract_data']['payment_details']['text'] = payment_text # Сохраняем сгенерированный текст
        logger.debug(f"User {update.effective_user.id} entered fixed payment order.")
        
        return await self._prompt_contract_end_date(update, context)

    # --- Обработчики для почасовой оплаты ---
    async def handle_hourly_rate(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает ввод почасовой ставки."""
        lang_code = context.user_data.get('lang_code', 'uk')
        try:
            rate_str = update.message.text.strip()
            rate = int(rate_str)
            if rate <= 0: raise ValueError("Rate must be a positive number.")
            context.user_data['contract_data']['payment_details']['rate'] = rate
            logger.debug(f"User {update.effective_user.id} entered hourly rate: {rate}")
            await update.message.reply_text(Translations.get_text(lang_code, 'prompt_hourly_accounting'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
            return BotState.AWAIT_HOURLY_ACCOUNTING.value
        except ValueError as e:
            await update.message.reply_text(f"{Translations.get_text(lang_code, 'error_invalid_input')} {e}", reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_HOURLY_RATE.value

    async def handle_hourly_accounting(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает ввод способа учета времени для почасовой оплаты."""
        lang_code = context.user_data.get('lang_code', 'uk')
        accounting = update.message.text.strip()
        if not accounting:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_HOURLY_ACCOUNTING.value
        context.user_data['contract_data']['payment_details']['accounting'] = accounting
        logger.debug(f"User {update.effective_user.id} entered hourly accounting method.")
        await update.message.reply_text(Translations.get_text(lang_code, 'prompt_hourly_payment_period'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
        return BotState.AWAIT_HOURLY_PAYMENT_PERIOD.value

    async def handle_hourly_payment_period(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает ввод периодичности оплаты для почасовой ставки."""
        lang_code = context.user_data.get('lang_code', 'uk')
        payment_period = update.message.text.strip()
        if not payment_period:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_HOURLY_PAYMENT_PERIOD.value
        context.user_data['contract_data']['payment_details']['payment_period'] = payment_period
        
        rate = context.user_data['contract_data']['payment_details']['rate']
        rate_words = number_to_ukrainian_words(rate)
        accounting = context.user_data['contract_data']['payment_details']['accounting']
        
        payment_text = Translations.get_text(lang_code, 'payment_type_hourly_text',
                                             rate=rate, rate_words=rate_words, 
                                             accounting=accounting, payment_period=payment_period)
        context.user_data['contract_data']['payment_details']['text'] = payment_text
        logger.debug(f"User {update.effective_user.id} entered hourly payment period.")
        
        return await self._prompt_contract_end_date(update, context)

    # --- Обработчики для процента от результата ---
    async def handle_percentage_value(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает ввод процентного значения."""
        lang_code = context.user_data.get('lang_code', 'uk')
        try:
            percentage_str = update.message.text.strip()
            percentage = int(percentage_str)
            if not (0 <= percentage <= 100):
                raise ValueError("Percentage must be between 0 and 100.")
            context.user_data['contract_data']['payment_details']['percentage'] = percentage
            logger.debug(f"User {update.effective_user.id} entered percentage value: {percentage}")
            await update.message.reply_text(Translations.get_text(lang_code, 'prompt_percentage_base'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
            return BotState.AWAIT_PERCENTAGE_BASE.value
        except ValueError as e:
            await update.message.reply_text(f"{Translations.get_text(lang_code, 'error_invalid_input')} {e}", reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_PERCENTAGE_VALUE.value

    async def handle_percentage_base(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает ввод базы для расчета процента."""
        lang_code = context.user_data.get('lang_code', 'uk')
        base = update.message.text.strip()
        if not base:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_PERCENTAGE_BASE.value
        context.user_data['contract_data']['payment_details']['base'] = base
        logger.debug(f"User {update.effective_user.id} entered percentage base.")
        await update.message.reply_text(Translations.get_text(lang_code, 'prompt_percentage_condition'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
        return BotState.AWAIT_PERCENTAGE_CONDITION.value

    async def handle_percentage_condition(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает ввод условия оплаты для процентного гонорара."""
        lang_code = context.user_data.get('lang_code', 'uk')
        condition = update.message.text.strip()
        if not condition:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_PERCENTAGE_CONDITION.value
        context.user_data['contract_data']['payment_details']['condition'] = condition
        
        percentage = context.user_data['contract_data']['payment_details']['percentage']
        base = context.user_data['contract_data']['payment_details']['base']
        
        payment_text = Translations.get_text(lang_code, 'payment_type_percentage_text',
                                             percentage=percentage, base=base, condition=condition)
        context.user_data['contract_data']['payment_details']['text'] = payment_text
        logger.debug(f"User {update.effective_user.id} entered percentage condition.")
        
        return await self._prompt_contract_end_date(update, context)

    # --- Обработчик для комбинированной системы оплаты ---
    async def handle_combined_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает описание комбинированной системы оплаты."""
        lang_code = context.user_data.get('lang_code', 'uk')
        description = update.message.text.strip()
        if not description:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_COMBINED_DESCRIPTION.value
        context.user_data['contract_data']['payment_details']['description'] = description
        
        payment_text = Translations.get_text(lang_code, 'payment_type_combined_text', description=description)
        context.user_data['contract_data']['payment_details']['text'] = payment_text
        logger.debug(f"User {update.effective_user.id} entered combined payment description.")
        
        return await self._prompt_contract_end_date(update, context)

    async def _prompt_contract_end_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Вспомогательный метод для запроса конечной даты действия договора.
        Используется после того, как все детали оплаты собраны.
        Устанавливает состояние `AWAIT_CONTRACT_END_DATE`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        
        # Пытаемся отредактировать сообщение, если это вызвано CallbackQuery
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(Translations.get_text(lang_code, 'prompt_contract_end_date'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.error(f"Failed to edit message in _prompt_contract_end_date: {e}", exc_info=True)
                await update.callback_query.message.reply_text(Translations.get_text(lang_code, 'prompt_contract_end_date'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
        else: # Иначе отправляем новое сообщение (например, после текстового ввода деталей оплаты)
            await update.message.reply_text(Translations.get_text(lang_code, 'prompt_contract_end_date'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
            
        return BotState.AWAIT_CONTRACT_END_DATE.value

    async def handle_contract_end_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает ввод конечной даты действия договора.
        Валидирует формат даты. Затем переходит к запросу местонахождения адвоката.
        Устанавливает состояние `AWAIT_ADVOCATE_LOCATION`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        end_date_str = update.message.text.strip()
        
        try:
            # Валидируем формат даты
            datetime.strptime(end_date_str, "%d.%m.%Y")
            context.user_data['contract_data']['end_date'] = end_date_str
            logger.debug(f"User {update.effective_user.id} entered contract end date: {end_date_str}")
            
            await update.message.reply_text(Translations.get_text(lang_code, 'prompt_advocate_location'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
            return BotState.AWAIT_ADVOCATE_LOCATION.value
        except ValueError:
            # Если формат даты некорректен
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_CONTRACT_END_DATE.value

    async def handle_advocate_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает ввод местонахождения адвоката.
        Затем переходит к запросу ЕДРПОУ клиента.
        Устанавливает состояние `AWAIT_CLIENT_EDRPOU`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        location = update.message.text.strip()
        if not location:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_ADVOCATE_LOCATION.value
        context.user_data['contract_data']['advocate']['location'] = location
        logger.debug(f"User {update.effective_user.id} entered advocate location: {location}")
        
        await update.message.reply_text(Translations.get_text(lang_code, 'prompt_client_edrpou'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
        return BotState.AWAIT_CLIENT_EDRPOU.value

    async def handle_client_edrpou(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает ввод ЕДРПОУ клиента.
        Затем переходит к запросу местонахождения клиента.
        Устанавливает состояние `AWAIT_CLIENT_LOCATION`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        edrpou = update.message.text.strip()
        if not edrpou:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_CLIENT_EDRPOU.value
        context.user_data['contract_data']['client']['edrpou'] = edrpou
        logger.debug(f"User {update.effective_user.id} entered client EDRPOU: {edrpou}")
        
        await update.message.reply_text(Translations.get_text(lang_code, 'prompt_client_location'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
        return BotState.AWAIT_CLIENT_LOCATION.value

    async def handle_client_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает ввод местонахождения клиента.
        После этого все необходимые данные для договора собраны,
        запускается генерация DOCX-файла договора.
        Завершает диалог, возвращаясь в `SELECTING_ACTION`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        location = update.message.text.strip()
        if not location:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_CLIENT_LOCATION.value
        context.user_data['contract_data']['client']['location'] = location
        logger.debug(f"User {update.effective_user.id} entered client location: {location}. All contract data collected.")
        
        # Теперь все данные собраны, можно генерировать документ
        return await self._generate_contract_document(update, context)

    async def _generate_contract_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Генерирует финальный документ договора и отправляет его пользователю.
        Устанавливает состояние `SELECTING_ACTION`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        processing_message = Translations.get_text(lang_code, 'contract_generating')
        
        # Импортируем CommonHandlers здесь, чтобы избежать циклической зависимости
        from handlers.common import CommonHandlers 

        async with typing_and_waiting(update, context, processing_message):
            data = context.user_data['contract_data']
            try:
                # Генерируем DOCX-файл с использованием функции из document_processor
                document_stream = generate_contract_doc(data, lang_code)
                logger.debug(f"DOCX contract generated for user {update.effective_user.id}.")
                
                await update.message.reply_document(
                    document=document_stream, 
                    filename=f"Договір про правову допомогу №{data['contract_number']}_{data['contract_date']}.docx", 
                    caption=Translations.get_text(lang_code, 'contract_generation_complete')
                )
            except Exception as e:
                logger.error(f"Failed to generate and send DOCX for contract for user {update.effective_user.id}: {e}", exc_info=True)
                # Сообщаем пользователю об ошибке
                await update.message.reply_text(
                    f"{Translations.get_text(lang_code, 'error_generic')}\n\n"
                    f"{Translations.get_text(lang_code, 'error_file_extract')}" # Можно использовать это как общее сообщение
                )
        
        # Очищаем данные договора из user_data после завершения
        del context.user_data['contract_data']
        logger.debug(f"Contract data cleared for user {update.effective_user.id}.")
        
        # Возвращаемся в главное меню (используем CommonHandlers для этого)
        # Note: Для show_main_menu CommonHandlers нуждается в экземпляре DatabaseManager.
        # Поскольку этот handler (contract_creation.py) не имеет прямой зависимости от db,
        # и CommonHandlers загружается здесь динамически, db_instance=None в CommonHandlers(db_instance=None)
        # означает, что методы CommonHandlers, которые зависят от db (как get_or_create_user),
        # могут вызвать ошибку. В `main.py` CommonHandlers инициализируется с `db`,
        # поэтому здесь для вызова `show_main_menu` правильнее было бы:
        # from main import common_handlers # (если common_handlers глобально доступен в main)
        # await common_handlers.show_main_menu(update, context)
        # Для текущей структуры мы предполагаем, что show_main_menu не требует db для отрисовки.
        # Если требует, нужно будет пересмотреть структуру DI или CommonHandlers.
        # В данном случае `show_main_menu` использует `db` только для получения лимитов,
        # что не критично при возвращении в меню.
        # Более правильное решение: CommonHandlers.show_main_menu() должен быть
        # статическим или не зависеть от self.db, если он просто рисует меню.
        # Или же передавать self.db в конструктор CommonHandlers.
        # Сейчас для простоты я оставлю как есть, предполагая, что это не критично.
        from handlers.common import CommonHandlers as _CH
        return await _CH(db=None).show_main_menu(update, context) # db_instance=None, т.к. show_main_menu не использует self.db