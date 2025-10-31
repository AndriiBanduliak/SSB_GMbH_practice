"""
Модуль для централизованной обработки ошибок в Telegram боте.
Содержит декораторы и утилиты для улучшения стабильности.
"""

import logging
import functools
import asyncio
from typing import Callable, Any
from telegram import Update
from telegram.ext import ContextTypes
from config import Translations

logger = logging.getLogger(__name__)

def safe_async_handler(func: Callable) -> Callable:
    """
    Декоратор для безопасного выполнения асинхронных обработчиков.
    Перехватывает все исключения и логирует их, предотвращая падение бота.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in handler {func.__name__}: {e}", exc_info=True)
            
            # Пытаемся отправить сообщение об ошибке пользователю
            try:
                update = None
                context = None
                
                # Ищем объекты Update и Context в аргументах
                for arg in args:
                    if isinstance(arg, Update):
                        update = arg
                    elif isinstance(arg, ContextTypes.DEFAULT_TYPE):
                        context = arg
                
                if update and context:
                    lang_code = 'uk'  # По умолчанию украинский
                    if hasattr(context, 'user_data') and context.user_data:
                        lang_code = context.user_data.get('lang_code', 'uk')
                    
                    error_message = Translations.get_text(lang_code, 'error_generic')
                    
                    if update.effective_message:
                        await update.effective_message.reply_text(error_message)
                    elif update.effective_chat:
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=error_message
                        )
            except Exception as reply_error:
                logger.error(f"Failed to send error message to user: {reply_error}")
            
            # Возвращаем безопасное состояние
            return None
            
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Декоратор для повторных попыток выполнения функции при ошибках.
    
    :param max_retries: Максимальное количество попыток
    :param delay: Задержка между попытками в секундах
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
            
            # Если все попытки неудачны, поднимаем последнее исключение
            raise last_exception
            
        return wrapper
    return decorator

def validate_user_input(func: Callable) -> Callable:
    """
    Декоратор для валидации пользовательского ввода.
    Проверяет наличие необходимых данных в Update объекте.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Ищем Update в аргументах
        update = None
        for arg in args:
            if isinstance(arg, Update):
                update = arg
                break
        
        if not update:
            logger.error(f"No Update object found in {func.__name__}")
            return None
        
        # Проверяем наличие пользователя
        if not update.effective_user:
            logger.error(f"No effective user in {func.__name__}")
            return None
        
        # Проверяем наличие сообщения или callback_query
        if not update.effective_message and not update.callback_query:
            logger.error(f"No effective message or callback query in {func.__name__}")
            return None
        
        return await func(*args, **kwargs)
        
    return wrapper

class ErrorHandler:
    """
    Класс для централизованной обработки ошибок.
    """
    
    @staticmethod
    async def handle_database_error(error: Exception, user_id: int = None) -> None:
        """
        Обрабатывает ошибки базы данных.
        """
        logger.error(f"Database error for user {user_id}: {error}", exc_info=True)
        # Здесь можно добавить логику восстановления или уведомления администраторов
    
    @staticmethod
    async def handle_openai_error(error: Exception, user_id: int = None) -> None:
        """
        Обрабатывает ошибки OpenAI API.
        """
        logger.error(f"OpenAI API error for user {user_id}: {error}", exc_info=True)
        # Здесь можно добавить логику повторных попыток или fallback
    
    @staticmethod
    async def handle_telegram_error(error: Exception, user_id: int = None) -> None:
        """
        Обрабатывает ошибки Telegram API.
        """
        logger.error(f"Telegram API error for user {user_id}: {error}", exc_info=True)
        # Здесь можно добавить логику обработки rate limits и других ошибок
    
    @staticmethod
    def log_user_error(user_id: int, username: str, error: Exception, context: str = "") -> None:
        """
        Логирует ошибку пользователя с контекстом.
        """
        logger.error(f"User error - ID: {user_id}, Username: {username}, Context: {context}, Error: {error}", exc_info=True)

def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """
    Безопасно выполняет функцию с обработкой ошибок.
    Возвращает результат функции или None в случае ошибки.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in safe_execute for {func.__name__}: {e}", exc_info=True)
        return None
