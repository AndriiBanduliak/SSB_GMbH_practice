import logging
import os # Для работы с путями файлов (получение расширения)
from telegram import Update
from telegram.ext import ContextTypes # Объекты ContextTypes используются для работы с контекстом
from telegram.constants import ParseMode # Для форматирования сообщений в HTML

from config import Config, Translations, BotState # Импортируем нашу конфигурацию, переводы и Enum состояний
from database import DatabaseManager # Для взаимодействия с базой данных
from openai_service import OpenAIService # Для взаимодействия с OpenAI API
from keyboards import get_main_keyboard, get_back_button # Импортируем функции для клавиатур
from utils import log_user_action, typing_and_waiting, send_long_message, markdown_to_html # Импортируем вспомогательные утилиты
from document_processor import extract_text_from_file # Для извлечения текста из документов

# Инициализируем логгер для этого модуля
logger = logging.getLogger(__name__)

class AIInteractionHandlers:
    """
    Класс, содержащий обработчики для взаимодействия с AI.
    Включает функции для ответов на юридические вопросы, анализа и редактирования документов.
    """
    def __init__(self, db: DatabaseManager, openai_service: OpenAIService):
        """
        Инициализирует AIInteractionHandlers.
        :param db: Экземпляр DatabaseManager для работы с БД.
        :param openai_service: Экземпляр OpenAIService для взаимодействия с AI.
        """
        self.db = db
        self.openai_service = openai_service
        logger.info("AIInteractionHandlers initialized.")

    async def go_to_ask_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработчик кнопки "Поставить вопрос".
        Проверяет дневной лимит пользователя на вопросы к AI и, если лимит не исчерпан,
        предлагает пользователю ввести свой вопрос.
        Устанавливает состояние `ASKING_QUESTION`.
        """
        try:
            query = update.callback_query
            if not query:
                logger.error("go_to_ask_question called without a callback query.")
                return BotState.SELECTING_ACTION.value # Вернемся в основное меню
                
            await query.answer() # Отвечаем на callback-запрос
            user = query.from_user
            
            # Получаем актуальные лимиты пользователя из БД
            q_count, _, lang_code = self.db.get_or_create_user(user.id, user.username, user.first_name)
            context.user_data['lang_code'] = lang_code # Убеждаемся, что lang_code в context.user_data актуален

            log_user_action(user.id, user.username, "go_to_ask_question")
            
            # Проверяем, не исчерпан ли дневной лимит
            if q_count >= Config.DAILY_QUESTION_LIMIT:
                try:
                    await query.edit_message_text(Translations.get_text(lang_code, 'limit_reached'), reply_markup=get_back_button(lang_code))
                except Exception as e:
                    logger.error(f"Failed to edit message in go_to_ask_question (limit reached): {e}", exc_info=True)
                    await query.message.reply_text(Translations.get_text(lang_code, 'limit_reached'), reply_markup=get_back_button(lang_code))
                return BotState.SELECTING_ACTION.value # Остаемся в главном меню
            
            # Отправляем промпт для ввода вопроса
            try:
                await query.edit_message_text(
                    Translations.get_text(lang_code, 'ask_question_prompt', remaining=Config.DAILY_QUESTION_LIMIT - q_count),
                    reply_markup=get_back_button(lang_code), 
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Failed to edit message in go_to_ask_question: {e}", exc_info=True)
                await query.message.reply_text(
                    Translations.get_text(lang_code, 'ask_question_prompt', remaining=Config.DAILY_QUESTION_LIMIT - q_count),
                    reply_markup=get_back_button(lang_code), 
                    parse_mode=ParseMode.HTML
                )

            return BotState.ASKING_QUESTION.value
            
        except Exception as e:
            logger.error(f"Unexpected error in go_to_ask_question: {e}", exc_info=True)
            # В случае ошибки возвращаемся в главное меню
            try:
                if query:
                    await query.message.reply_text(
                        Translations.get_text('uk', 'error_generic'),
                        reply_markup=get_main_keyboard('uk')
                    )
            except Exception as reply_error:
                logger.error(f"Failed to send error message: {reply_error}")
            return BotState.SELECTING_ACTION.value

    async def handle_question_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обрабатывает введенный пользователем юридический вопрос.
        Отправляет вопрос AI, получает ответ, инкрементирует счетчик использования
        и выводит результат.
        """
        lang_code = context.user_data.get('lang_code', 'uk')
        user = update.effective_user
        user_question = update.message.text.strip()
        
        if not user_question:
            await update.message.reply_text(Translations.get_text(lang_code, 'error_invalid_input'), reply_markup=get_back_button(lang_code))
            return BotState.ASKING_QUESTION.value # Остаемся в том же состоянии, чтобы пользователь мог ввести вопрос
        
        log_user_action(user.id, user.username, "submit_question", user_question)
        processing_message = Translations.get_text(lang_code, 'processing_query')
        
        ai_answer = Translations.get_text(lang_code, "error_generic") # Инициализируем с ошибкой по умолчанию

        # Используем контекстный менеджер для отображения "печатает..." и сообщения ожидания
        async with typing_and_waiting(update, context, processing_message):
            try:
                ai_answer = await self.openai_service.get_ai_response(
                    "ai_system_prompt_general", user_question, lang_code
                )
            except Exception as e:
                logger.error(f"Error getting AI response for question: {e}", exc_info=True)
                # ai_answer уже содержит generic_error_message

        # Инкрементируем счетчик использования вопросов, даже если AI вернул ошибку
        # (AI-вызов был сделан, лимит должен засчитаться)
        self.db.increment_usage(user.id, "question")
        
        # Форматируем финальный ответ с AI-подвалом (дисклеймером)
        final_response_text = f"{markdown_to_html(ai_answer)}\n\n{Translations.get_text(lang_code, 'ai_response_footer')}"
        
        # Отправляем ответ, разбивая его на части, если он слишком длинный
        await send_long_message(update, final_response_text)
        
        # Возвращаемся в главное меню
        await update.message.reply_text(Translations.get_text(lang_code, 'main_menu'), reply_markup=get_main_keyboard(lang_code), parse_mode=ParseMode.HTML)
        return BotState.SELECTING_ACTION.value

    async def go_to_analyze_doc(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработчик кнопки "Анализировать документ".
        Проверяет дневной лимит пользователя на обработку документов и предлагает
        загрузить документ для анализа.
        Устанавливает состояние `ANALYZING_DOC`.
        """
        try:
            query = update.callback_query
            if not query:
                logger.error("go_to_analyze_doc called without a callback query.")
                return BotState.SELECTING_ACTION.value
                
            await query.answer()
            user = query.from_user
            
            # Получаем актуальные лимиты пользователя из БД
            _, d_count, lang_code = self.db.get_or_create_user(user.id, user.username, user.first_name)
            context.user_data['lang_code'] = lang_code

            log_user_action(user.id, user.username, "go_to_analyze_doc")
            
            # Проверяем лимит
            if d_count >= Config.DAILY_DOCUMENT_LIMIT:
                try:
                    await query.edit_message_text(Translations.get_text(lang_code, 'limit_reached'), reply_markup=get_back_button(lang_code))
                except Exception as e:
                    logger.error(f"Failed to edit message in go_to_analyze_doc (limit reached): {e}", exc_info=True)
                    await query.message.reply_text(Translations.get_text(lang_code, 'limit_reached'), reply_markup=get_back_button(lang_code))
                return BotState.SELECTING_ACTION.value
            
            # Сохраняем тип действия с документом в user_data
            context.user_data['doc_action'] = 'analyze'
            
            # Отправляем промпт для загрузки документа
            try:
                await query.edit_message_text(
                    Translations.get_text(lang_code, 'analyze_doc_prompt', remaining=Config.DAILY_DOCUMENT_LIMIT - d_count),
                    reply_markup=get_back_button(lang_code), 
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Failed to edit message in go_to_analyze_doc: {e}", exc_info=True)
                await query.message.reply_text(
                    Translations.get_text(lang_code, 'analyze_doc_prompt', remaining=Config.DAILY_DOCUMENT_LIMIT - d_count),
                    reply_markup=get_back_button(lang_code), 
                    parse_mode=ParseMode.HTML
                )
            
            return BotState.ANALYZING_DOC.value
            
        except Exception as e:
            logger.error(f"Unexpected error in go_to_analyze_doc: {e}", exc_info=True)
            # В случае ошибки возвращаемся в главное меню
            try:
                if query:
                    await query.message.reply_text(
                        Translations.get_text('uk', 'error_generic'),
                        reply_markup=get_main_keyboard('uk')
                    )
            except Exception as reply_error:
                logger.error(f"Failed to send error message: {reply_error}")
            return BotState.SELECTING_ACTION.value

    async def go_to_edit_doc(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработчик кнопки "Редактировать документ".
        Аналогично анализу, но для редактирования.
        Устанавливает состояние `EDITING_DOC`.
        """
        try:
            query = update.callback_query
            if not query:
                logger.error("go_to_edit_doc called without a callback query.")
                return BotState.SELECTING_ACTION.value

            await query.answer()
            user = query.from_user
            
            # Получаем актуальные лимиты пользователя из БД
            _, d_count, lang_code = self.db.get_or_create_user(user.id, user.username, user.first_name)
            context.user_data['lang_code'] = lang_code

            log_user_action(user.id, user.username, "go_to_edit_doc")
            
            # Проверяем лимит
            if d_count >= Config.DAILY_DOCUMENT_LIMIT:
                try:
                    await query.edit_message_text(Translations.get_text(lang_code, 'limit_reached'), reply_markup=get_back_button(lang_code))
                except Exception as e:
                    logger.error(f"Failed to edit message in go_to_edit_doc (limit reached): {e}", exc_info=True)
                    await query.message.reply_text(Translations.get_text(lang_code, 'limit_reached'), reply_markup=get_back_button(lang_code))
                return BotState.SELECTING_ACTION.value
            
            # Сохраняем тип действия с документом
            context.user_data['doc_action'] = 'edit'
            
            # Отправляем промпт для загрузки документа с инструкцией по подписи
            try:
                await query.edit_message_text(
                    Translations.get_text(lang_code, 'edit_doc_prompt', remaining=Config.DAILY_DOCUMENT_LIMIT - d_count),
                    reply_markup=get_back_button(lang_code), 
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Failed to edit message in go_to_edit_doc: {e}", exc_info=True)
                await query.message.reply_text(
                    Translations.get_text(lang_code, 'edit_doc_prompt', remaining=Config.DAILY_DOCUMENT_LIMIT - d_count),
                    reply_markup=get_back_button(lang_code), 
                    parse_mode=ParseMode.HTML
                )
            
            return BotState.EDITING_DOC.value
            
        except Exception as e:
            logger.error(f"Unexpected error in go_to_edit_doc: {e}", exc_info=True)
            # В случае ошибки возвращаемся в главное меню
            try:
                if query:
                    await query.message.reply_text(
                        Translations.get_text('uk', 'error_generic'),
                        reply_markup=get_main_keyboard('uk')
                    )
            except Exception as reply_error:
                logger.error(f"Failed to send error message: {reply_error}")
            return BotState.SELECTING_ACTION.value

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
        """
        Обрабатывает загруженный пользователем документ.
        Извлекает текст, отправляет его AI с соответствующим промптом
        (анализ или редактирование), и выводит результат.
        """
        user = update.effective_user
        document = update.message.document
        lang_code = context.user_data.get('lang_code', 'uk')
        doc_action = context.user_data.get('doc_action') # 'analyze' or 'edit'

        if not document:
            await update.message.reply_text(Translations.get_text(lang_code, "error_invalid_input"))
            return None # Остаемся в текущем состоянии, ждем корректный документ
            
        file_ext = os.path.splitext(document.file_name)[1].lower()

        # Проверка формата файла
        if file_ext not in ['.txt', '.docx', '.pdf']:
            await update.message.reply_text(Translations.get_text(lang_code, "error_file_format"))
            return None # Остаемся в текущем состоянии
        
        # Проверка размера файла (20 MB)
        if document.file_size > 20 * 1024 * 1024:
            await update.message.reply_text(Translations.get_text(lang_code, "error_file_size"))
            return None # Остаемся в текущем состоянии

        log_user_action(user.id, user.username, f"submit_document_for_{doc_action}", f"File: {document.file_name}")
        processing_message = Translations.get_text(lang_code, 'processing_doc')
        
        ai_response_content = Translations.get_text(lang_code, "error_generic") # Инициализируем с ошибкой

        async with typing_and_waiting(update, context, processing_message):
            try:
                # Скачиваем файл
                file_obj = await context.bot.get_file(document.file_id)
                doc_bytes = await file_obj.download_as_bytearray()
                
                # Извлекаем текст из файла
                doc_text = extract_text_from_file(doc_bytes, file_ext)

                if not doc_text.strip(): 
                    raise ValueError(Translations.get_text(lang_code, "error_file_extract"))
                
                # Обрезаем текст документа, чтобы не превышать лимит токенов AI
                # Модель Config.OPENAI_MODEL имеет ограничение на контекст.
                # 12000 символов - это грубая оценка, может быть настроена.
                # Более точно нужно считать токены, а не символы.
                max_doc_length = 12000 
                if len(doc_text) > max_doc_length:
                    doc_text = doc_text[:max_doc_length] + "\n\n... (Документ обрезан из-за размера)"

                # Формируем пользовательский промпт в зависимости от действия
                user_prompt = ""
                if doc_action == 'analyze':
                    user_prompt = "Проанализируйте приложенный юридический документ и предоставьте краткое изложение его ключевых моментов, потенциальных рисков и обязательств для участвующих сторон."
                elif doc_action == 'edit':
                    # Инструкции для редактирования берутся из подписи к файлу
                    user_prompt_caption = update.message.caption or ""
                    if not user_prompt_caption.strip():
                         user_prompt = "Пожалуйста, исправьте любые грамматические ошибки, улучшите ясность и обеспечьте профессиональный юридический тон в приложенном документе."
                    else:
                         user_prompt = f"Пожалуйста, примените следующие изменения к приложенному документу: {user_prompt_caption}"
                
                # Получаем ответ от AI
                ai_response_content = await self.openai_service.get_ai_response(
                    "ai_system_prompt_document", user_prompt, lang_code, doc_text
                )
            
            except ValueError as e: 
                # Ошибка извлечения текста или невалидный ввод
                await update.message.reply_text(str(e))
                return None # Остаемся в текущем состоянии, чтобы пользователь мог попробовать снова
            except Exception as e:
                logger.error(f"Critical error during document processing for user {user.id}: {e}", exc_info=True)
                # ai_response_content уже содержит generic_error_message

        # Инкрементируем счетчик использования документов
        self.db.increment_usage(user.id, "document")
        
        # Форматируем и отправляем финальный ответ
        final_response_text = f"<b>{Translations.get_text(lang_code, 'doc_result_header')}</b>\n\n{markdown_to_html(ai_response_content)}\n\n{Translations.get_text(lang_code, 'ai_response_footer')}"
        await send_long_message(update, final_response_text)
        
        # Возвращаемся в главное меню
        await update.message.reply_text(Translations.get_text(lang_code, 'main_menu'), reply_markup=get_main_keyboard(lang_code), parse_mode=ParseMode.HTML)
        return BotState.SELECTING_ACTION.value