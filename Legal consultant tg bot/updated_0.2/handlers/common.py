import logging
import re # Для использования регулярных выражений, например, для кнопки "Назад" на ReplyKeyboard
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton # Добавлен KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler # Импортируем ConversationHandler для возврата к его состояниям
from telegram.constants import ParseMode # Для форматирования сообщений

from config import Config, Translations, BotState # Импортируем нашу конфигурацию, переводы и Enum состояний
from database import DatabaseManager # Для взаимодействия с базой данных
from keyboards import get_main_keyboard, get_back_button, get_contact_request_keyboard # Импортируем функции для клавиатур
from utils import log_user_action # Импортируем утилиту для логирования

# Инициализируем логгер для этого модуля
logger = logging.getLogger(__name__)

class CommonHandlers:
    """
    Класс, содержащий обработчики для общих команд и состояний бота.
    """
    def __init__(self, db: DatabaseManager):
        """
        Инициализирует CommonHandlers.
        :param db: Экземпляр DatabaseManager для работы с БД.
        """
        self.db = db
        logger.info("CommonHandlers initialized.")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработчик команды /start.
        Приветствует пользователя и предлагает выбрать язык.
        Устанавливает начальное состояние `SELECTING_LANG`.
        """
        user = update.effective_user
        if user:
            # Получаем или создаем пользователя в БД
            self.db.get_or_create_user(user.id, user.username, user.first_name)
            log_user_action(user.id, user.username, "start")
        else:
            logger.warning("Start command received without effective user info.")
            # Можно отправить сообщение по умолчанию или попросить перезапустить бота
            if update.message:
                await update.message.reply_text("👋 Hello! Please use /start command.")
            return ConversationHandler.END # Завершаем, если нет пользователя
            
        # Формируем клавиатуру для выбора языка
        keyboard = [[InlineKeyboardButton(name, callback_data=f"lang_{code}")] 
                    for code, name in Translations.LANGUAGES.items()]
        
        if update.message: # Проверяем, что сообщение существует (не всегда так, например, при редактировании)
            await update.message.reply_text(
                Translations.get_text('uk', 'welcome_choose_lang'), # Используем украинский по умолчанию для этого шага
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            logger.warning("Attempted to send language selection message but no message object.")
            # Если это callback, то update.callback_query.message будет существовать
            if update.callback_query and update.callback_query.message:
                await update.callback_query.message.reply_text(
                    Translations.get_text('uk', 'welcome_choose_lang'),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        return BotState.SELECTING_LANG.value

    async def select_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработчик выбора языка.
        Устанавливает выбранный язык для пользователя и показывает главное меню.
        Устанавливает состояние `SELECTING_ACTION`.
        """
        query = update.callback_query
        if not query:
            logger.error("select_language called without a callback query.")
            return ConversationHandler.END

        await query.answer() # Отвечаем на callback-запрос
        lang_code = query.data.split('_')[1]
        user = query.from_user
        
        self.db.set_user_language(user.id, lang_code)
        context.user_data['lang_code'] = lang_code # Сохраняем язык в user_data для текущей сессии
        log_user_action(user.id, user.username, "select_language", lang_code)
        
        try:
            await query.edit_message_text(
                text=Translations.get_text(lang_code, 'welcome'),
                reply_markup=get_main_keyboard(lang_code),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to edit message in select_language: {e}", exc_info=True)
            # В случае ошибки редактирования, можно отправить новое сообщение
            await query.message.reply_text(
                text=Translations.get_text(lang_code, 'welcome'),
                reply_markup=get_main_keyboard(lang_code),
                parse_mode=ParseMode.HTML
            )
            
        return BotState.SELECTING_ACTION.value

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Показывает главное меню бота.
        Сбрасывает все данные, связанные с текущим диалогом (запрос, договор).
        Возвращает состояние `SELECTING_ACTION`.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        # Очищаем данные активных диалогов при возвращении в главное меню
        context.user_data.pop('request_data', None)
        context.user_data.pop('contract_data', None)
        logger.debug(f"User {update.effective_user.id} returned to main menu. Dialogue data cleared.")
        
        effective_message_to_reply = update.effective_message 
        if not effective_message_to_reply and update.callback_query:
             effective_message_to_reply = update.callback_query.message

        if effective_message_to_reply:
            await effective_message_to_reply.reply_text(
                text=Translations.get_text(lang_code, 'main_menu'),
                reply_markup=get_main_keyboard(lang_code),
                parse_mode=ParseMode.HTML
            )
        else:
            logger.error("Could not find effective message/chat to reply to for main menu.")
            # В крайнем случае, если нет ни update.message, ни update.callback_query.message
            # (что маловероятно для обычных взаимодействий), можно попытаться отправить
            # сообщение напрямую в чат, если update.effective_chat доступен.
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=Translations.get_text(lang_code, 'main_menu'),
                    reply_markup=get_main_keyboard(lang_code),
                    parse_mode=ParseMode.HTML
                )
        return BotState.SELECTING_ACTION.value

    async def back_to_main_menu_from_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработчик кнопки "Назад" из любого состояния.
        Пытается удалить предыдущее сообщение с кнопками и переходит в главное меню.
        """
        query = update.callback_query
        if query:
            await query.answer()
            try:
                # Пытаемся удалить сообщение, из которого была нажата кнопка "Назад".
                # Это делает интерфейс чище.
                await query.delete_message()
            except Exception as e:
                # Если сообщение уже было удалено или не существует (например, устаревший callback),
                # мы просто логируем это и продолжаем.
                logger.debug(f"Could not delete message on back_to_main: {e}")
        else:
            logger.warning("back_to_main_menu_from_button called without a callback query.")
        
        log_user_action(update.effective_user.id, update.effective_user.username, "back_to_main_menu")
        return await self.show_main_menu(update, context)

    async def cancel_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработчик кнопки "Отмена" во время активного диалога (создание запроса/договора).
        Очищает пользовательские данные для текущего диалога и возвращается в главное меню.
        """
        query = update.callback_query
        if not query:
            logger.error("cancel_creation called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        lang_code = context.user_data.get('lang_code', 'uk')
        
        # Очищаем данные текущего активного диалога
        context.user_data.pop('request_data', None)
        context.user_data.pop('contract_data', None)
        logger.debug(f"User {update.effective_user.id} cancelled creation. Dialogue data cleared.")

        try:
            await query.edit_message_text(Translations.get_text(lang_code, "request_cancelled"))
        except Exception as e:
            logger.warning(f"Could not edit message on cancel_creation: {e}. Sending new message instead.")
            # Если не удалось отредактировать, отправляем новое сообщение
            await query.message.reply_text(Translations.get_text(lang_code, "request_cancelled"))

        log_user_action(update.effective_user.id, update.effective_user.username, "cancel_dialog")
        return await self.show_main_menu(update, context)

    async def show_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Показывает информацию о боте и текущих лимитах использования для пользователя.
        """
        query = update.callback_query
        if not query:
            logger.error("show_info called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        user = query.from_user
        
        # Получаем актуальные лимиты пользователя из БД (с возможным сбросом)
        q_count, d_count, lang_code = self.db.get_or_create_user(user.id, user.username, user.first_name)
        context.user_data['lang_code'] = lang_code # Убеждаемся, что lang_code в context.user_data актуален
        
        log_user_action(user.id, user.username, "show_info")

        try:
            await query.edit_message_text(
                Translations.get_text(lang_code, 'info_text', 
                                    q_count=q_count, q_limit=Config.DAILY_QUESTION_LIMIT, 
                                    d_count=d_count, d_limit=Config.DAILY_DOCUMENT_LIMIT),
                reply_markup=get_back_button(lang_code), 
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to edit message in show_info: {e}", exc_info=True)
            await query.message.reply_text(
                Translations.get_text(lang_code, 'info_text', 
                                    q_count=q_count, q_limit=Config.DAILY_QUESTION_LIMIT, 
                                    d_count=d_count, d_limit=Config.DAILY_DOCUMENT_LIMIT),
                reply_markup=get_back_button(lang_code), 
                parse_mode=ParseMode.HTML
            )
        
        return BotState.SELECTING_ACTION.value # Остаемся в главном меню после показа инфо

    async def go_to_request_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Отправляет пользователю сообщение с запросом на предоставление номера телефона
        через ReplyKeyboard.
        """
        query = update.callback_query
        if not query:
            logger.error("go_to_request_contact called without a callback query.")
            return ConversationHandler.END

        await query.answer()
        lang_code = context.user_data.get('lang_code', 'uk')
        log_user_action(update.effective_user.id, update.effective_user.username, "request_contact")
        
        try:
            # Удаляем инлайн-клавиатуру, чтобы ReplyKeyboard стала заметной
            await query.delete_message()
            await query.message.reply_text(
                text=Translations.get_text(lang_code, 'contact_request'), 
                reply_markup=get_contact_request_keyboard(lang_code)
            )
        except Exception as e:
            logger.error(f"Failed to send contact request message: {e}", exc_info=True)
            # В случае ошибки удаления/отправки, просто отправляем сообщение, не удаляя старое
            if query.message:
                await query.message.reply_text(
                    text=Translations.get_text(lang_code, 'contact_request'), 
                    reply_markup=get_contact_request_keyboard(lang_code)
                )

        return BotState.AWAITING_CONTACT.value

    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает полученный номер телефона пользователя.
        Сохраняет номер в БД и возвращает в главное меню.
        """
        contact = update.message.contact
        lang_code = context.user_data.get('lang_code', 'uk')
        
        if contact and contact.user_id == update.effective_user.id:
            self.db.set_user_phone(contact.user_id, contact.phone_number)
            log_user_action(update.effective_user.id, update.effective_user.username, "contact_received", contact.phone_number)
            await update.message.reply_text(
                text=Translations.get_text(lang_code, 'contact_received'), 
                reply_markup=ReplyKeyboardRemove() # Убираем Reply-клавиатуру
            )
        else:
            # Если контакт не отправлен или отправлен чужой контакт (что маловероятно через request_contact)
            logger.warning(f"Invalid contact received from user {update.effective_user.id}.")
            await update.message.reply_text(
                Translations.get_text(lang_code, 'error_invalid_input'), 
                reply_markup=ReplyKeyboardRemove()
            )
            
        return await self.show_main_menu(update, context)

    async def back_from_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработчик кнопки "Назад" с Reply-клавиатуры запроса контакта.
        Удаляет Reply-клавиатуру и возвращает в главное меню.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        log_user_action(update.effective_user.id, update.effective_user.username, "back_from_contact")
        
        if update.message:
            await update.message.reply_text(
                text=Translations.get_text(lang_code, 'back_to_menu_message'), 
                reply_markup=ReplyKeyboardRemove() # Убираем Reply-клавиатуру
            )
        else:
            # Если это был не Message, а что-то другое, логгируем и переходим
            logger.warning("back_from_contact called without an effective message.")
        
        return await self.show_main_menu(update, context)
    
    async def prompt_to_use_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Отвечает пользователю, если он вводит текст вместо использования кнопок в главном меню.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        log_user_action(update.effective_user.id, update.effective_user.username, "wrong_input_main_menu", update.message.text)
        await update.message.reply_text(
            text=Translations.get_text(lang_code, 'prompt_use_buttons'), 
            reply_markup=get_main_keyboard(lang_code), 
            parse_mode=ParseMode.HTML
        )