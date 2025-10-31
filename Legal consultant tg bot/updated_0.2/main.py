import os
import logging
import re 
# ... другие импорты ...
from dotenv import load_dotenv
load_dotenv()

# --- Настройка логирования ---
# Логгер теперь настраивается и инициализируется в config.py
import logging
from config import Config, BotState, Translations, setup_logging # Импортируем BotState и setup_logging
# Инициализируем логгер. Он будет доступен в других модулях после их импорта.
logger = setup_logging()

# --- Импорты Telegram.ext ---
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
# Импорты ParseMode, ChatAction, ReplyKeyboardRemove и т.д. теперь не нужны здесь,
# так как они используются в соответствующих модулях обработчиков или утилит.

# --- Импорты внутренних модулей ---
from database import DatabaseManager          # Для работы с базой данных
from openai_service import openai_service      # Для взаимодействия с OpenAI API (уже инициализирован)
# Импортируем классы обработчиков, которые содержат логику различных этапов
from handlers.common import CommonHandlers
from handlers.ai_interaction import AIInteractionHandlers
from handlers.request_creation import RequestCreationHandlers
from handlers.contract_creation import ContractCreationHandlers

def main():
    """
    Главная функция, запускающая Telegram-бота.
    Отвечает за инициализацию зависимостей, регистрацию обработчиков
    и запуск процесса опроса (polling).
    """
    try:
        # 1. Проверка наличия обязательных переменных окружения
        if not Config.TELEGRAM_BOT_TOKEN or not Config.OPENAI_API_KEY:
            logger.critical("TELEGRAM_BOT_TOKEN or OPENAI_API_KEY not found in .env! Exiting.")
            return

        # 2. Инициализация зависимостей (сервисов)
        # Менеджер базы данных
        db = DatabaseManager(Config.DB_NAME)
        # Сервис OpenAI уже инициализирован при импорте `openai_service`,
        # так как он stateless (не зависит от состояния).

        # 3. Инициализация классов обработчиков
        # Передаем зависимости (db, openai_service) в конструкторы обработчиков,
        # которым они требуются. Это называется "внедрение зависимостей" (Dependency Injection).
        common_handlers = CommonHandlers(db)
        ai_handlers = AIInteractionHandlers(db, openai_service)
        request_handlers_obj = RequestCreationHandlers(openai_service)
        contract_handlers_obj = ContractCreationHandlers() # В текущей реализации не требует прямых зависимостей в конструкторе

        # 4. Создание объекта Application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

        # 5. Определение общих fallbacks для ConversationHandler
        # Эти обработчики будут доступны из любого состояния, если не сработают другие.
        common_fallbacks = [
            CallbackQueryHandler(common_handlers.back_to_main_menu_from_button, pattern="^back_to_main$"),
            CallbackQueryHandler(common_handlers.cancel_creation, pattern="^cancel_creation$"),
            # /start должен быть доступен из любого состояния для сброса диалога
            CommandHandler("start", common_handlers.start) 
        ]

        # 6. Регистрация ConversationHandler
        # Используем значения из Enum BotState для четкости.
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", common_handlers.start)],
            states={
                BotState.SELECTING_LANG.value: [
                    CallbackQueryHandler(common_handlers.select_language, pattern="^lang_")
                ],
                BotState.SELECTING_ACTION.value: [
                    CallbackQueryHandler(ai_handlers.go_to_ask_question, pattern="^ask_question$"),
                    CallbackQueryHandler(ai_handlers.go_to_analyze_doc, pattern="^analyze_document$"),
                    CallbackQueryHandler(ai_handlers.go_to_edit_doc, pattern="^edit_document$"),
                    CallbackQueryHandler(request_handlers_obj.create_request_start, pattern="^create_request$"),
                    CallbackQueryHandler(contract_handlers_obj.create_contract_start, pattern="^create_contract$"),
                    CallbackQueryHandler(common_handlers.show_info, pattern="^info$"),
                    CallbackQueryHandler(common_handlers.go_to_request_contact, pattern="^request_contact$"),
                    # Этот MessageHandler обрабатывает любой текст, введенный в главном меню
                    MessageHandler(filters.TEXT & ~filters.COMMAND, common_handlers.prompt_to_use_buttons),
                ],
                # --- Состояния для взаимодействия с AI (вопросы и документы) ---
                BotState.ASKING_QUESTION.value: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, ai_handlers.handle_question_message),
                    *common_fallbacks # Применяем общие fallbacks
                ],
                BotState.ANALYZING_DOC.value: [
                    MessageHandler(filters.Document.ALL, ai_handlers.handle_document),
                    *common_fallbacks
                ],
                BotState.EDITING_DOC.value: [
                    MessageHandler(filters.Document.ALL, ai_handlers.handle_document),
                    *common_fallbacks
                ],
                # --- Состояние для запроса контакта ---
                BotState.AWAITING_CONTACT.value: [
                    MessageHandler(filters.CONTACT, common_handlers.handle_contact),
                    # Отдельный обработчик для кнопки "Назад" на ReplyKeyboard
                    MessageHandler(filters.TEXT & filters.Regex(
                        f"^({re.escape(Translations.get_text('uk', 'back_btn'))}|"
                        f"{re.escape(Translations.get_text('en', 'back_btn'))}|"
                        f"{re.escape(Translations.get_text('de', 'back_btn'))})$"), common_handlers.back_from_contact),
                    # Любой другой текст в этом состоянии также вернет в меню
                    MessageHandler(filters.TEXT & ~filters.COMMAND, common_handlers.back_from_contact),
                    *common_fallbacks # Также применяем общие fallbacks
                ],
                
                # --- Состояния для создания адвокатского запроса ---
                # Здесь мы используем методы из request_handlers_obj
                BotState.AWAIT_LEGAL_FORM.value: [CallbackQueryHandler(request_handlers_obj.handle_legal_form, pattern="^req_form_")],
                BotState.AWAIT_BUREAU_NAME.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_bureau_name)],
                BotState.AWAIT_LEGAL_ADDRESS.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_legal_address)],
                BotState.AWAIT_MAILING_ADDRESS.value: [
                    CallbackQueryHandler(request_handlers_obj.handle_same_address, pattern="^req_addr_same$"),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_mailing_address),
                ],
                BotState.AWAIT_ADVOCATE_NAME.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_advocate_name)],
                BotState.AWAIT_ADVOCATE_PHONE.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_advocate_phone)],
                BotState.AWAIT_ADVOCATE_EMAIL.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_advocate_email)],
                BotState.AWAIT_CERTIFICATE_DETAILS.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_certificate_details)],
                BotState.AWAIT_CERTIFICATE_ISSUER.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_certificate_issuer)],
                BotState.AWAIT_ORDER_DETAILS.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_order_details)],
                BotState.AWAIT_CLIENT_TYPE.value: [CallbackQueryHandler(request_handlers_obj.handle_client_type, pattern="^req_client_")],
                BotState.AWAIT_CLIENT_PHYSICAL_NAME.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_client_physical_name)],
                BotState.AWAIT_CLIENT_PHYSICAL_ADDRESS.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_client_physical_address)],
                BotState.AWAIT_CLIENT_LEGAL_NAME.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_client_legal_name)],
                BotState.AWAIT_CLIENT_LEGAL_EDRPOU.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_client_legal_edrpou)],
                BotState.AWAIT_CLIENT_LEGAL_ADDRESS.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_client_legal_address)],
                BotState.AWAIT_CONTRACT_DETAILS.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_contract_details)],
                BotState.AWAIT_LEGAL_AID_SUBJECT.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_legal_aid_subject)],
                BotState.AWAIT_RECIPIENT_DETAILS.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_recipient_details)],
                BotState.AWAIT_OUTGOING_NUMBER.value: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_outgoing_number),
                    CommandHandler("skip", request_handlers_obj.skip_outgoing_number),
                ],
                BotState.AWAIT_REQUEST_BODY.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_handlers_obj.handle_request_body)],

                # --- Состояния для создания договора ---
                # Здесь мы используем методы из contract_handlers_obj
                BotState.AWAIT_CONTRACT_NUMBER_DATE.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_contract_number_date)],
                BotState.CONFIRM_CLIENT_DATA.value: [
                    CallbackQueryHandler(contract_handlers_obj.handle_confirm_client_data, pattern="^contract_confirm_client$"),
                    CallbackQueryHandler(contract_handlers_obj.handle_client_edit_choice, pattern="^contract_edit_client_"),
                ],
                # Обработчик для всех полей редактирования клиента
                BotState.AWAIT_CLIENT_NAME.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_client_edited_data)],
                BotState.AWAIT_CLIENT_POSITION.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_client_edited_data)],
                BotState.AWAIT_CLIENT_BASIS.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_client_edited_data)],
                
                BotState.CONFIRM_ADVOCATE_DATA.value: [
                    CallbackQueryHandler(contract_handlers_obj.handle_confirm_advocate_data, pattern="^contract_confirm_advocate$"),
                    CallbackQueryHandler(contract_handlers_obj.handle_advocate_edit_choice, pattern="^contract_edit_advocate_"),
                ],
                # Обработчик для всех полей редактирования адвоката
                BotState.AWAIT_ADVOCATE_FIO.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_advocate_edited_data)],
                BotState.AWAIT_ADVOCATE_CERTIFICATE_SERIES.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_advocate_edited_data)],
                BotState.AWAIT_ADVOCATE_CERTIFICATE_NUMBER.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_advocate_edited_data)],
                BotState.AWAIT_ADVOCATE_CERTIFICATE_ISSUER.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_advocate_edited_data)],
                BotState.AWAIT_ADVOCATE_CERTIFICATE_ISSUER_DATE_NUMBER.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_advocate_edited_data)],
                
                BotState.SELECT_PAYMENT_TYPE.value: [CallbackQueryHandler(contract_handlers_obj.handle_payment_type_selection, pattern="^payment_type_")],
                BotState.AWAIT_FIXED_AMOUNT.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_fixed_amount)],
                BotState.AWAIT_FIXED_PAYMENT_ORDER.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_fixed_payment_order)],
                BotState.AWAIT_HOURLY_RATE.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_hourly_rate)],
                BotState.AWAIT_HOURLY_ACCOUNTING.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_hourly_accounting)],
                BotState.AWAIT_HOURLY_PAYMENT_PERIOD.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_hourly_payment_period)],
                BotState.AWAIT_PERCENTAGE_VALUE.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_percentage_value)],
                BotState.AWAIT_PERCENTAGE_BASE.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_percentage_base)],
                BotState.AWAIT_PERCENTAGE_CONDITION.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_percentage_condition)],
                BotState.AWAIT_COMBINED_DESCRIPTION.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_combined_description)],
                
                BotState.AWAIT_CONTRACT_END_DATE.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_contract_end_date)],
                BotState.AWAIT_ADVOCATE_LOCATION.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_advocate_location)],
                BotState.AWAIT_CLIENT_EDRPOU.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_client_edrpou)],
                BotState.AWAIT_CLIENT_LOCATION.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_handlers_obj.handle_client_location)],
            },
            # Общие fallbacks, которые будут применяться, если ни один из обработчиков текущего состояния не сработал.
            fallbacks=[
                *common_fallbacks # Применяем общие fallbacks ко всему ConversationHandler
            ],
        )
        
        application.add_handler(conv_handler)
        
        # 7. Настройка хука завершения работы
        # Этот метод будет вызван перед завершением работы приложения,
        # чтобы корректно закрыть ресурсы, например, соединение с базой данных.
        async def on_shutdown(app: Application):
            logger.info("Bot is shutting down...")
            db.close() # Закрываем соединение с БД
            logger.info("Database connection closed.")
            
        application.post_shutdown = on_shutdown

        # 8. Запуск бота
        logger.info("Bot is starting polling...")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Critical error during bot initialization: {e}", exc_info=True)
        print(f"❌ Critical error: {e}")
        print("Please check your configuration and try again.")
    finally:
        # Убеждаемся, что соединение с БД закрыто даже при ошибке
        try:
            if 'db' in locals():
                db.close()
                logger.info("Database connection closed in finally block.")
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {cleanup_error}")

if __name__ == '__main__':
    main()