import os
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
LOG_FILE = "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger('discord_twitter_bot')

# Загрузка необходимых переменных
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
TARGET_CHANNEL_ID_STR = os.environ.get("TARGET_DISCORD_CHANNEL_ID")
TWITTER_USER_TO_MONITOR = os.environ.get("TWITTER_USER_TO_MONITOR")
KEYWORDS_STR = os.environ.get("KEYWORDS_TO_MONITOR", "")
BOT_DEFAULT_LANGUAGE = os.environ.get("BOT_DEFAULT_LANGUAGE", "de")

# Валидация и преобразование
if not DISCORD_BOT_TOKEN or not TWITTER_BEARER_TOKEN or not TARGET_CHANNEL_ID_STR or not TWITTER_USER_TO_MONITOR:
    log.critical("Отсутствуют обязательные переменные окружения.")
    raise SystemExit("Ошибка: Отсутствуют обязательные переменные окружения.")

try:
    TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID_STR)
except ValueError:
    log.critical("TARGET_DISCORD_CHANNEL_ID должен быть числом.")
    raise SystemExit("Ошибка: TARGET_DISCORD_CHANNEL_ID не является числом.")

KEYWORDS = [k.strip().lower() for k in KEYWORDS_STR.split(',') if k.strip()]
