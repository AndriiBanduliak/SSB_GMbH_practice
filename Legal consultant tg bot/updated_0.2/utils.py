import re
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction

from num2words import num2words # Для преобразования чисел в слова
from config import Translations # Для доступа к переведенным текстам и сообщениям

# Инициализируем логгер для этого модуля
# (Настройка логирования происходит в `config.py` и вызывается в `main.py`)
logger = logging.getLogger(__name__)

def log_user_action(user_id: int, username: str | None, action: str, details: str = ""):
    """
    Утилитарная функция для логирования действий пользователя в консоль/файлы.
    Это помогает отслеживать поведение бота и пользователей для отладки или аналитики.

    :param user_id: Уникальный ID пользователя Telegram.
    :param username: Имя пользователя Telegram (может быть None).
    :param action: Краткое описание действия (например, "start", "submit_question").
    :param details: Дополнительные детали, связанные с действием (например, текст вопроса).
    """
    # Ограничиваем длину деталей, чтобы логи не были слишком длинными
    details_truncated = details[:200] + '...' if len(details) > 200 else details
    logger.info(f"User {user_id} ({username or 'N/A'}) | Action: {action} | Details: {details_truncated}")

def markdown_to_html(text: str) -> str:
    """
    Конвертирует упрощенный Markdown-формат в HTML, поддерживаемый Telegram
    (ParseMode.HTML). Поддерживает: жирный текст (**bold**), курсив (*italic*),
    моноширинный текст (`code`) и заголовки (### Heading -> <b>Heading</b>).

    :param text: Входной текст с Markdown-разметкой.
    :return: Текст, преобразованный в HTML.
    """
    # Замена жирного текста: **текст** -> <b>текст</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Замена курсива: *текст* -> <i>текст</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Замена моноширинного текста: `текст` -> <code>текст</code>
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Замена заголовков (например, ### Заголовок) на жирный текст
    text = re.sub(r'#{1,6}\s*(.*)', r'<b>\1</b>', text) # Поддержка H1-H6
    return text.strip()

@asynccontextmanager
async def typing_and_waiting(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str) -> AsyncIterator[None]:
    """
    Контекстный менеджер для улучшения пользовательского опыта.
    Отправляет сообщение "печатает..." в чат и дополнительное сообщение
    с индикатором ожидания, а затем удаляет его после выполнения блока кода.

    Пример использования:
    async with typing_and_waiting(update, context, "⏳ Обрабатываю..."):
        await some_long_running_task()

    :param update: Объект Update из python-telegram-bot.
    :param context: Объект ContextTypes.DEFAULT_TYPE из python-telegram-bot.
    :param message: Текст сообщения, которое будет отображаться во время ожидания.
    """
    waiting_message = None
    try:
        # Отправляем сообщение об ожидании
        if update.effective_message:
            waiting_message = await update.effective_message.reply_text(message)
        else:
            # Если update.effective_message нет (например, из callback_query),
            # пытаемся использовать update.effective_chat
            if update.effective_chat:
                waiting_message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message
                )
            else:
                logger.warning("Could not find effective message or chat to send waiting message.")

        # Отправляем действие "печатает..."
        # asyncio.create_task() позволяет запустить эту задачу в фоне, не дожидаясь ее завершения.
        # Telegram самостоятельно отменяет действие "печатает...", как только бот отправит следующее сообщение
        # или через 5 секунд.
        if update.effective_chat:
            asyncio.create_task(
                context.bot.send_chat_action(
                    chat_id=update.effective_chat.id,
                    action=ChatAction.TYPING
                )
            )
        
        yield # Выполнение основного блока кода

    except Exception as e:
        logger.error(f"Error within typing_and_waiting context: {e}", exc_info=True)
        # Важно пробросить исключение дальше, чтобы основной обработчик мог его перехватить
        raise
    finally:
        # Пытаемся удалить сообщение об ожидании
        if waiting_message:
            try:
                await waiting_message.delete()
            except Exception as e:
                # Часто это исключение означает, что сообщение уже было удалено (например,
                # пользователем вручную или новым сообщением от бота)
                logger.debug(f"Could not delete waiting message (possibly already deleted or replaced): {e}")


async def send_long_message(update: Update, text: str):
    """
    Отправляет сообщение пользователю, разбивая его на части, если длина текста
    превышает максимальный лимит Telegram (4096 символов для HTML).

    :param update: Объект Update из python-telegram-bot.
    :param text: Полный текст сообщения для отправки.
    """
    if not text:
        logger.warning("Attempted to send an empty message.")
        return

    max_len = 4000 # Максимальная длина сообщения для ParseMode.HTML в Telegram
    
    if len(text) <= max_len:
        # Если текст короткий, отправляем как есть
        try:
            await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Failed to send short HTML message: {e} - Content: {text[:100]}...", exc_info=True)
            # Fallback к обычному тексту, если HTML не прошел
            try:
                await update.effective_message.reply_text(text, disable_web_page_preview=True)
            except Exception as inner_e:
                logger.critical(f"Failed to send message even as plain text: {inner_e}", exc_info=True)
    else:
        # Если текст длинный, разбиваем на части
        # Простая стратегия разбиения по символам, можно улучшить,
        # чтобы разбивать по параграфам или предложениям, чтобы не обрезать слова
        # и HTML-теги посередине. Для текущих нужд достаточно.
        parts = []
        current_part = ""
        # Попытка разбить по абзацам для сохранения структуры
        for line in text.split('\n'):
            # Учитываем +1 за потенциальный перенос строки
            if len(current_part) + len(line) + 1 > max_len:
                if current_part:
                    parts.append(current_part)
                current_part = line
            else:
                current_part += "\n" + line if current_part else line
        if current_part:
            parts.append(current_part)

        for i, part in enumerate(parts):
            try:
                await update.effective_message.reply_text(part, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                # Небольшая задержка между отправкой частей, чтобы избежать rate limits
                await asyncio.sleep(0.5) 
            except Exception as e:
                logger.error(f"Failed to send part {i+1}/{len(parts)} of long HTML message: {e} - Content start: {part[:100]}...", exc_info=True)
                # Fallback к обычному тексту для этой части
                try:
                    await update.effective_message.reply_text(part, disable_web_page_preview=True)
                    await asyncio.sleep(0.5)
                except Exception as inner_e:
                    logger.critical(f"Failed to send part {i+1}/{len(parts)} even as plain text: {inner_e}", exc_info=True)
                    # Если отправка части сообщения не удалась даже после fallback,
                    # есть смысл выйти, чтобы не спамить ошибками
                    break


def number_to_ukrainian_words(number: int) -> str:
    """
    Преобразует целое число в его текстовое представление на украинском языке.
    Возвращает только слова для числа, без суффиксов валют (например, "гривень").

    :param number: Целое число для преобразования.
    :return: Строковое представление числа прописью на украинском языке.
             Возвращает исходное число как строку в случае ошибки.
    """
    try:
        # Используем библиотеку num2words. `lang='uk'` для украинского языка.
        # Часто num2words при использовании валюты добавляет название валюты,
        # поэтому убираем его, если оно есть.
        words = num2words(number, lang='uk')
        # Убираем возможные суффиксы валюты, которые могли быть добавлены num2words
        words = words.replace(' гривень', '').replace(' гривня', '').replace(' копійки', '').replace(' копійка', '').strip()
        return words
    except Exception as e:
        logger.error(f"Failed to convert number {number} to Ukrainian words: {e}", exc_info=True)
        return str(number) # В случае ошибки возвращаем число как строку