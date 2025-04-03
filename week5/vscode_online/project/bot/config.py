import os
import sys
import logging
from dotenv import load_dotenv

# --- ЗАГРУЗКА .ENV ---
load_dotenv()
# logging.debug("Переменные окружения загружены.") # Логирование лучше настроить после базовой конфигурации

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
LOG_FILE = "bot.log"
# Формат логирования вынесен сюда для единообразия
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

def setup_logging():
    """Настраивает базовое логирование."""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    # Уменьшаем шум от discord.py и tweepy
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('tweepy').setLevel(logging.WARNING)
    log = logging.getLogger('discord_twitter_bot')
    log.info("Логирование настроено.")
    return log

# --- КОНФИГУРАЦИЯ ИЗ .ENV ---
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
TARGET_CHANNEL_ID_STR = os.environ.get("TARGET_DISCORD_CHANNEL_ID")
TWITTER_USER_TO_MONITOR = os.environ.get("TWITTER_USER_TO_MONITOR")
KEYWORDS_STR = os.environ.get("KEYWORDS_TO_MONITOR", "")
DEFAULT_LANGUAGE = os.environ.get("BOT_DEFAULT_LANGUAGE", "de").lower() # Приводим к нижнему регистру сразу

# --- Проверка обязательных переменных ---
def check_env_vars():
    """Проверяет наличие обязательных переменных окружения."""
    errors = []
    if not TOKEN: errors.append("DISCORD_BOT_TOKEN")
    if not TWITTER_BEARER_TOKEN: errors.append("TWITTER_BEARER_TOKEN")
    if not TARGET_CHANNEL_ID_STR: errors.append("TARGET_DISCORD_CHANNEL_ID")
    if not TWITTER_USER_TO_MONITOR: errors.append("TWITTER_USER_TO_MONITOR")

    if errors:
        # Логирование здесь еще не настроено полностью, используем print/stderr
        critical_message = f"Критическая ошибка: Не установлены переменные окружения: {', '.join(errors)}. Проверьте ваш .env файл."
        print(critical_message, file=sys.stderr)
        sys.exit(critical_message)

    # --- Преобразование типов ---
    try:
        target_channel_id = int(TARGET_CHANNEL_ID_STR)
    except (ValueError, TypeError):
        critical_message = f"Критическая ошибка: TARGET_DISCORD_CHANNEL_ID ('{TARGET_CHANNEL_ID_STR}') не является числом."
        print(critical_message, file=sys.stderr)
        sys.exit(critical_message)

    keywords = [k.strip().lower() for k in KEYWORDS_STR.split(',') if k.strip()]

    return {
        "TOKEN": TOKEN,
        "TWITTER_BEARER_TOKEN": TWITTER_BEARER_TOKEN,
        "TARGET_CHANNEL_ID": target_channel_id,
        "TWITTER_USER_TO_MONITOR": TWITTER_USER_TO_MONITOR,
        "KEYWORDS": keywords,
        "DEFAULT_LANGUAGE": DEFAULT_LANGUAGE,
        "LOG_FILE": LOG_FILE,
        "LOG_FORMAT": LOG_FORMAT,
    }

# Вызываем проверку при импорте модуля
CONFIG = check_env_vars()

# Настраиваем логирование после проверки базовых переменных
log = setup_logging()

# Логируем успешную загрузку конфигурации
log.info(f"Конфигурация загружена. Канал: {CONFIG['TARGET_CHANNEL_ID']}, "
         f"Пользователь Twitter: {CONFIG['TWITTER_USER_TO_MONITOR']}, "
         f"Ключевые слова: {CONFIG['KEYWORDS']}, "
         f"Язык по умолчанию: {CONFIG['DEFAULT_LANGUAGE']}")

# --- Константы для файлов состояния ---
# Можно оставить здесь или перенести в модули, которые их используют
SERVER_SETTINGS_FILE = "server_settings.json"
LAST_TWEET_ID_FILE = "last_tweet.id"
