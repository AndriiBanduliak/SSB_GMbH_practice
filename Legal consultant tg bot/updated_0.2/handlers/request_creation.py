import logging
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup # Импорт InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from config import Translations, BotState # Импортируем BotState Enum
from openai_service import OpenAIService # Для взаимодействия с OpenAI API
from document_processor import generate_advocate_request_doc # Для генерации DOCX файла
from keyboards import get_cancel_button # Импортируем функцию для кнопки отмены
from utils import typing_and_waiting, send_long_message # Импортируем вспомогательные утилиты

# Инициализируем логгер для этого модуля
logger = logging.getLogger(__name__)

# Дефолтные данные для запроса (полезно для инициализации context.user_data)
DEFAULT_REQUEST_DATA = {
    'legal_form_text': '',
    'bureau_name': 'N/A', # По умолчанию, если не бюро/объединение
    'legal_address': '',
    'mailing_address': '',
    'advocate_name': '',
    'advocate_phone': '',
    'advocate_email': '',
    'certificate_details': '',
    'certificate_issuer': '',
    'order_details': '',
    'client_type': '', # 'phys' или 'legal'
    'client_name': '',
    'client_address': '',
    'client_id': 'N/A', # Для юр. лиц (ЕДРПОУ)
    'contract_details': '',
    'legal_aid_subject': '',
    'recipient_details': '',
    'outgoing_number': 'N/A', # Может быть пропущено
    'request_body': '',
}

class RequestCreationHandlers:
    """
    Класс, содержащий обработчики для пошагового создания адвокатского запроса.
    """
    def __init__(self, openai_service: OpenAIService):
        """
        Инициализирует RequestCreationHandlers.
        :param openai_service: Экземпляр OpenAIService для взаимодействия с AI.
        """
        self.openai_service = openai_service
        logger.info("RequestCreationHandlers initialized.")

    async def create_request_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начинает диалог создания адвокатского запроса.
        Предлагает пользователю выбрать форму адвокатской деятельности.
        Устанавливает состояние `AWAIT_LEGAL_FORM`.
        """
        query = update.callback_query
        if not query:
            logger.error("create_request_start called without a callback query.")
            return ConversationHandler.END # Или вернуться в SELECTING_ACTION

        await query.answer() # Отвечаем на callback-запрос
        lang_code = context.user_data.get('lang_code', 'uk')
        
        # Инициализируем данные для запроса в context.user_data
        context.user_data['request_data'] = DEFAULT_REQUEST_DATA.copy()
        logger.debug(f"User {update.effective_user.id} started request creation. Initializing request_data.")
        
        # Создаем кнопки для выбора формы адвокатской деятельности
        legal_form_keys = ['self', 'fop', 'bureau', 'union']
        keyboard = [
            [InlineKeyboardButton(Translations.get_text(lang_code, f'legal_form_{key}'), callback_data=f"req_form_{key}")]
            for key in legal_form_keys
        ]
        keyboard.append([InlineKeyboardButton(Translations.get_text(lang_code, 'cancel_btn'), callback_data="cancel_creation")])
        
        try:
            await query.edit_message_text(
                text=Translations.get_text(lang_code, 'request_start'), 
                reply_markup=InlineKeyboardMarkup(keyboard), 
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to edit message in create_request_start: {e}", exc_info=True)
            await query.message.reply_text(
                text=Translations.get_text(lang_code, 'request_start'), 
                reply_markup=InlineKeyboardMarkup(keyboard), 
                parse_mode=ParseMode.HTML
            )

        return BotState.AWAIT_LEGAL_FORM.value

    async def handle_legal_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает выбор формы адвокатской деятельности.
        В зависимости от выбора, переходит к следующему шагу:
        запрос имени бюро/объединения или юридического адреса.
        Устанавливает состояние `AWAIT_BUREAU_NAME` или `AWAIT_LEGAL_ADDRESS`.
        """
        query = update.callback_query
        if not query:
            logger.error("handle_legal_form called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        lang_code = context.user_data['lang_code']
        form_key = query.data.split('_')[-1] # Извлекаем 'self', 'fop', 'bureau', 'union'
        
        form_text = Translations.get_text(lang_code, f'legal_form_{form_key}')
        context.user_data['request_data']['legal_form_text'] = form_text
        logger.debug(f"User {update.effective_user.id} selected legal form: {form_key}")
        
        try:
            # Редактируем предыдущее сообщение, чтобы показать подтверждение выбора
            await query.edit_message_text(f"✅ {Translations.get_text(lang_code, 'request_start')[:-1]}: <b>{form_text}</b>", parse_mode=ParseMode.HTML)
            
            if form_key in ['bureau', 'union']:
                await query.message.reply_text(Translations.get_text(lang_code, 'prompt_bureau_name'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
                return BotState.AWAIT_BUREAU_NAME.value
            else:
                context.user_data['request_data']['bureau_name'] = "N/A" # Для физ. лиц и ФОП название бюро неактуально
                await query.message.reply_text(Translations.get_text(lang_code, 'prompt_legal_address'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
                return BotState.AWAIT_LEGAL_ADDRESS.value
        except Exception as e:
            logger.error(f"Failed to handle legal form selection for user {update.effective_user.id}: {e}", exc_info=True)
            await query.message.reply_text(Translations.get_text(lang_code, 'error_generic'), reply_markup=get_cancel_button(lang_code))
            return ConversationHandler.END # Выход из диалога при серьезной ошибке


    # --- Вспомогательный метод для обработки простого текстового ввода ---
    async def _generic_text_input_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data_key: str, next_prompt_key: str, next_state: BotState) -> int:
        """
        Универсальный обработчик для текстовых полей, которые просто запрашивают текст
        и переходят к следующему промпту.
        :param data_key: Ключ в словаре `request_data` для сохранения введенного текста.
        :param next_prompt_key: Ключ для получения текста следующего вопроса из `Translations`.
        :param next_state: Следующее состояние `ConversationHandler` после этого шага.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        user_input = update.message.text.strip()

        if not user_input:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return context.state # Остаемся в текущем состоянии
        
        context.user_data['request_data'][data_key] = user_input
        logger.debug(f"User {update.effective_user.id} entered data for '{data_key}'. Next prompt: '{next_prompt_key}'")
        
        await update.message.reply_text(
            Translations.get_text(lang_code, next_prompt_key), 
            reply_markup=get_cancel_button(lang_code), 
            parse_mode=ParseMode.HTML
        )
        return next_state.value

    # --- Обработчики для каждого шага адвокатского запроса ---

    async def handle_bureau_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self._generic_text_input_handler(update, context, 'bureau_name', 'prompt_legal_address', BotState.AWAIT_LEGAL_ADDRESS)

    async def handle_legal_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает юридический адрес и предлагает ввести адрес для переписки,
        с опцией "Такой же, как юридический".
        Устанавливает состояние `AWAIT_MAILING_ADDRESS`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        user_input = update.message.text.strip()
        
        if not user_input:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_LEGAL_ADDRESS.value # Остаемся в текущем состоянии
            
        context.user_data['request_data']['legal_address'] = user_input
        
        keyboard = [
            [InlineKeyboardButton(Translations.get_text(lang_code, 'same_as_legal_btn'), callback_data="req_addr_same")], 
            [InlineKeyboardButton(Translations.get_text(lang_code, 'cancel_btn'), callback_data="cancel_creation")]
        ]
        await update.message.reply_text(
            Translations.get_text(lang_code, 'prompt_mailing_address'), 
            reply_markup=InlineKeyboardMarkup(keyboard), 
            parse_mode=ParseMode.HTML
        )
        return BotState.AWAIT_MAILING_ADDRESS.value

    async def handle_same_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает выбор "Такой же, как юридический" для адреса для переписки.
        Копирует юридический адрес в поле адреса для переписки.
        Устанавливает состояние `AWAIT_ADVOCATE_NAME`.
        """
        query = update.callback_query
        if not query:
            logger.error("handle_same_address called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        lang_code = context.user_data['lang_code']
        legal_address = context.user_data['request_data']['legal_address']
        context.user_data['request_data']['mailing_address'] = legal_address
        logger.debug(f"User {update.effective_user.id} set mailing address same as legal: {legal_address}")
        
        try:
            await query.edit_message_text(f"✅ {Translations.get_text(lang_code, 'prompt_mailing_address')[:-1]}: {legal_address}", parse_mode=ParseMode.HTML)
            await query.message.reply_text(Translations.get_text(lang_code, 'prompt_advocate_name'), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Failed to handle same address for user {update.effective_user.id}: {e}", exc_info=True)
            await query.message.reply_text(Translations.get_text(lang_code, 'error_generic'), reply_markup=get_cancel_button(lang_code))
            return ConversationHandler.END

        return BotState.AWAIT_ADVOCATE_NAME.value
        
    async def handle_mailing_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self._generic_text_input_handler(update, context, 'mailing_address', 'prompt_advocate_name', BotState.AWAIT_ADVOCATE_NAME)
    
    async def handle_advocate_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self._generic_text_input_handler(update, context, 'advocate_name', 'prompt_advocate_phone', BotState.AWAIT_ADVOCATE_PHONE)
    
    async def handle_advocate_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self._generic_text_input_handler(update, context, 'advocate_phone', 'prompt_advocate_email', BotState.AWAIT_ADVOCATE_EMAIL)
    
    async def handle_advocate_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self._generic_text_input_handler(update, context, 'advocate_email', 'prompt_certificate_details', BotState.AWAIT_CERTIFICATE_DETAILS)
    
    async def handle_certificate_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self._generic_text_input_handler(update, context, 'certificate_details', 'prompt_certificate_issuer', BotState.AWAIT_CERTIFICATE_ISSUER)
    
    async def handle_certificate_issuer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self._generic_text_input_handler(update, context, 'certificate_issuer', 'prompt_order_details', BotState.AWAIT_ORDER_DETAILS)

    async def handle_order_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает данные ордера и предлагает выбрать тип клиента (физ./юр. лицо).
        Устанавливает состояние `AWAIT_CLIENT_TYPE`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        user_input = update.message.text.strip()

        if not user_input:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_ORDER_DETAILS.value # Остаемся в текущем состоянии

        context.user_data['request_data']['order_details'] = user_input
        
        keyboard = [
            [InlineKeyboardButton(Translations.get_text(lang_code, 'client_type_physical'), callback_data="req_client_phys")],
            [InlineKeyboardButton(Translations.get_text(lang_code, 'client_type_legal'), callback_data="req_client_legal")],
            [InlineKeyboardButton(Translations.get_text(lang_code, 'cancel_btn'), callback_data="cancel_creation")]
        ]
        await update.message.reply_text(
            Translations.get_text(lang_code, 'prompt_client_type'), 
            reply_markup=InlineKeyboardMarkup(keyboard), 
            parse_mode=ParseMode.HTML
        )
        return BotState.AWAIT_CLIENT_TYPE.value

    async def handle_client_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает выбор типа клиента и переходит к запросу соответствующих данных.
        Устанавливает состояние `AWAIT_CLIENT_PHYSICAL_NAME` или `AWAIT_CLIENT_LEGAL_NAME`.
        """
        query = update.callback_query
        if not query:
            logger.error("handle_client_type called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        client_type = query.data.split('_')[-1] # 'phys' или 'legal'
        context.user_data['request_data']['client_type'] = client_type
        lang_code = context.user_data['lang_code']
        logger.debug(f"User {update.effective_user.id} selected client type: {client_type}")
        
        next_prompt = 'prompt_client_physical_name' if client_type == 'phys' else 'prompt_client_legal_name'
        next_state = BotState.AWAIT_CLIENT_PHYSICAL_NAME if client_type == 'phys' else BotState.AWAIT_CLIENT_LEGAL_NAME
        
        try:
            await query.edit_message_text(Translations.get_text(lang_code, next_prompt), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Failed to edit message in handle_client_type: {e}", exc_info=True)
            await query.message.reply_text(Translations.get_text(lang_code, next_prompt), reply_markup=get_cancel_button(lang_code), parse_mode=ParseMode.HTML)

        return next_state.value

    async def handle_client_physical_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
        return await self._generic_text_input_handler(update, context, 'client_name', 'prompt_client_physical_address', BotState.AWAIT_CLIENT_PHYSICAL_ADDRESS)
        
    async def handle_client_physical_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
        context.user_data['request_data']['client_id'] = "N/A" # Для физ. лиц ЕДРПОУ неактуален
        return await self._generic_text_input_handler(update, context, 'client_address', 'prompt_contract_details', BotState.AWAIT_CONTRACT_DETAILS)
        
    async def handle_client_legal_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
        return await self._generic_text_input_handler(update, context, 'client_name', 'prompt_client_legal_edrpou', BotState.AWAIT_CLIENT_LEGAL_EDRPOU)
        
    async def handle_client_legal_edrpou(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
        return await self._generic_text_input_handler(update, context, 'client_id', 'prompt_client_legal_address', BotState.AWAIT_CLIENT_LEGAL_ADDRESS)
        
    async def handle_client_legal_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
        return await self._generic_text_input_handler(update, context, 'client_address', 'prompt_contract_details', BotState.AWAIT_CONTRACT_DETAILS)
        
    async def handle_contract_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
        return await self._generic_text_input_handler(update, context, 'contract_details', 'prompt_legal_aid_subject', BotState.AWAIT_LEGAL_AID_SUBJECT)
        
    async def handle_legal_aid_subject(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
        return await self._generic_text_input_handler(update, context, 'legal_aid_subject', 'prompt_recipient_details', BotState.AWAIT_RECIPIENT_DETAILS)
        
    async def handle_recipient_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
        return await self._generic_text_input_handler(update, context, 'recipient_details', 'prompt_outgoing_number', BotState.AWAIT_OUTGOING_NUMBER)
        
    async def handle_outgoing_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
        """
        Обрабатывает исходящий номер запроса.
        Если пользователь ввел /skip, то поле помечается как "N/A".
        Устанавливает состояние `AWAIT_REQUEST_BODY`.
        """
        return await self._generic_text_input_handler(update, context, 'outgoing_number', 'prompt_request_body', BotState.AWAIT_REQUEST_BODY)
        
    async def skip_outgoing_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает команду /skip для исходящего номера запроса.
        Устанавливает `outgoing_number` как "N/A".
        Устанавливает состояние `AWAIT_REQUEST_BODY`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        context.user_data['request_data']['outgoing_number'] = "N/A"
        logger.debug(f"User {update.effective_user.id} skipped outgoing number.")
        
        await update.message.reply_text(
            Translations.get_text(lang_code, 'prompt_request_body'), 
            reply_markup=get_cancel_button(lang_code), 
            parse_mode=ParseMode.HTML
        )
        return BotState.AWAIT_REQUEST_BODY.value

    async def handle_request_body(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает основной текст запроса от пользователя, формирует полный промпт для AI,
        получает ответ AI, генерирует DOCX-файл и отправляет его пользователю.
        Завершает диалог, возвращаясь в `SELECTING_ACTION`.
        """
        lang_code = context.user_data['lang_code']
        user_request_body = update.message.text.strip()

        if not user_request_body:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_cancel_button(lang_code))
            return BotState.AWAIT_REQUEST_BODY.value # Остаемся в текущем состоянии

        context.user_data['request_data']['request_body'] = user_request_body
        logger.debug(f"User {update.effective_user.id} provided request body. Initiating AI generation.")
        
        processing_message = Translations.get_text(lang_code, 'request_generating')
        
        # Импортируем CommonHandlers здесь, чтобы избежать циклического импорта
        # (request_creation импортирует utils, который импортирует translations, config)
        # Если CommonHandlers импортирует request_creation, то будет цикл.
        from handlers.common import CommonHandlers 
        
        ai_response_text = Translations.get_text(lang_code, "error_generic") # Инициализация

        async with typing_and_waiting(update, context, processing_message):
            data = context.user_data['request_data']
            T = lambda key: Translations.get_text(lang_code, key) # Сокращенная функция для переводов

            # Формируем полный промпт для AI на основе всех собранных данных.
            # Заголовки (prompt_header_...) берутся из Translations, чтобы AI мог их понять.
            full_prompt = f"""
**{T('prompt_header_recipient')}:**
{data.get('recipient_details', 'N/A')}

**{T('prompt_header_sender')}:**
- {T('prompt_header_form')}: {data.get('legal_form_text', 'N/A')}
- {T('prompt_header_bureau')}: {data.get('bureau_name', 'N/A')}
- {T('prompt_header_advocate_name')}: {data.get('advocate_name', 'N/A')}
- {T('prompt_header_address')}: {data.get('mailing_address', 'N/A')}
- {T('prompt_header_phone')}: {data.get('advocate_phone', 'N/A')}
- {T('prompt_header_email')}: {data.get('advocate_email', 'N/A')}
- {T('prompt_header_certificate')}: {data.get('certificate_details', '')}, {data.get('certificate_issuer', '')}
- {T('prompt_header_order')}: {data.get('order_details', 'N/A')}

**{T('prompt_header_client')}:**
- {T('prompt_header_client_type_legal') if data.get('client_type') == 'legal' else T('prompt_header_client_type_phys')}: {data.get('client_name', 'N/A')}, {data.get('client_id', '')}, {T('prompt_header_address')}: {data.get('client_address', 'N/A')}

**{T('prompt_header_basis')}:**
- {T('prompt_header_contract')}: {data.get('contract_details', 'N/A')}
- {T('prompt_header_subject')}: {data.get('legal_aid_subject', 'N/A')}

**{T('prompt_header_request_details')}:**
- {T('prompt_header_number')}: {data.get('outgoing_number', 'N/A')}
- {T('prompt_header_date')}: {date.today().strftime('%d.%m.%Y')}

**{T('prompt_header_body')}:**
{data.get('request_body', 'N/A')}

**{T('prompt_header_liability')}:**
{T(f'advocate_request_liability_clause_{lang_code}')}
"""
            # Выбираем системный промпт для AI в зависимости от языка
            system_prompt_key = f"ai_system_prompt_advocate_request_{lang_code}"
            
            try:
                ai_response_text = await self.openai_service.get_ai_response(system_prompt_key, full_prompt, lang_code)
                logger.debug(f"AI response received for advocate request. Length: {len(ai_response_text)} characters.")
                
                # Генерируем DOCX-файл с использованием функции из document_processor
                document_stream = generate_advocate_request_doc(data, lang_code, ai_response_text)
                
                await update.message.reply_document(
                    document=document_stream, 
                    filename=f"Advocate_Request_{date.today().strftime('%Y-%m-%d')}.docx", 
                    caption=T('request_generation_complete')
                )
            except Exception as e:
                logger.error(f"Failed to generate and send DOCX for advocate request for user {update.effective_user.id}: {e}", exc_info=True)
                # Если создание файла или отправка не удалась, сообщаем пользователю об ошибке
                await update.message.reply_text(
                    f"{Translations.get_text(lang_code, 'error_generic')}\n\n"
                    f"{Translations.get_text(lang_code, 'error_file_extract')}" # Используем это как общее сообщение
                )
                # Как запасной вариант, можно отправить пользователю сырой текст ответа AI
                if ai_response_text and ai_response_text != Translations.get_text(lang_code, "error_generic"):
                    await send_long_message(update, f"{Translations.get_text(lang_code, 'doc_result_header')}\n\n{ai_response_text}")

        # Очищаем данные запроса из user_data после завершения
        del context.user_data['request_data']
        logger.debug(f"Request data cleared for user {update.effective_user.id}.")
        
        # Возвращаемся в главное меню (используем CommonHandlers для этого)
        return await CommonHandlers(self.db).show_main_menu(update, context)