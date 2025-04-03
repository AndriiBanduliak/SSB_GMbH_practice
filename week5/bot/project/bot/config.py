import os
import sys
import logging
from dotenv import load_dotenv

# --- ЗАГРУЗКА .ENV ---
load_dotenv()

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
LOG_FILE = "bot.log"
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
    logging.getLogger('discord').setLevel(logging.WARNING)
    # Повысим уровень для tweepy, чтобы видеть RateLimit
    logging.getLogger('tweepy').setLevel(logging.INFO)
    log = logging.getLogger('discord_twitter_bot')
    log.info("Логирование настроено.")
    return log


# --- КОНФИГУРАЦИЯ ИЗ .ENV ---
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
TARGET_CHANNEL_ID_STR = os.environ.get("TARGET_DISCORD_CHANNEL_ID")
DEFAULT_LANGUAGE = os.environ.get(
    "BOT_DEFAULT_LANGUAGE", "en").lower()  # По умолчанию английский

# --- ФИКСИРОВАННЫЕ ХЕШТЕГИ (из ТЗ) ---
# Приводим к нижнему регистру и убираем '#' для удобства сравнения
TARGET_HASHTAGS_RAW = ["#tothemoon", "#memecoin", "#pumpit", "#space", "#10x"]
TARGET_HASHTAGS = [tag.lower().lstrip('#') for tag in TARGET_HASHTAGS_RAW]

# --- Проверка обязательных переменных ---


def check_env_vars():
    """Проверяет наличие обязательных переменных окружения."""
    errors = []
    if not TOKEN:
        errors.append("DISCORD_BOT_TOKEN")
    if not TWITTER_BEARER_TOKEN:
        errors.append("TWITTER_BEARER_TOKEN")
    if not TARGET_CHANNEL_ID_STR:
        errors.append("TARGET_DISCORD_CHANNEL_ID")
    # Убрали проверку TWITTER_USER_TO_MONITOR

    if errors:
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

    return {
        "TOKEN": TOKEN,
        "TWITTER_BEARER_TOKEN": TWITTER_BEARER_TOKEN,
        "TARGET_CHANNEL_ID": target_channel_id,
        "DEFAULT_LANGUAGE": DEFAULT_LANGUAGE,
        "TARGET_HASHTAGS": TARGET_HASHTAGS,  # Добавили хештеги в конфиг
        "LOG_FILE": LOG_FILE,
        "LOG_FORMAT": LOG_FORMAT,
    }


# Вызываем проверку при импорте
CONFIG = check_env_vars()
# Настраиваем логирование
log = setup_logging()

log.info(f"Конфигурация загружена. Канал: {CONFIG['TARGET_CHANNEL_ID']}, "
         f"Целевые хештеги: {CONFIG['TARGET_HASHTAGS']}, "
         f"Язык по умолчанию: {CONFIG['DEFAULT_LANGUAGE']}")

# --- Константы больше не нужны ---
# SERVER_SETTINGS_FILE = "server_settings.json"
# LAST_TWEET_ID_FILE = "last_tweet.id"
