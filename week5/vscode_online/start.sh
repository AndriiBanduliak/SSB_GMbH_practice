#!/bin/bash

echo "Создание структуры проекта..."

# Создаем основные директории
mkdir -p project/bot

# Создаем пустые __init__.py для обозначения пакета
touch project/bot/__init__.py

echo "Создание файлов Python..."

# --- Файл: project/bot/config.py ---
cat << EOF > project/bot/config.py
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
EOF

# --- Файл: project/bot/translations.py ---
cat << EOF > project/bot/translations.py
import logging
from .config import CONFIG  # Импортируем словарь конфигурации

log = logging.getLogger('discord_twitter_bot.translations')

# --- Структура переводов ---
translations = {
    "de": {
        "TWITTER_INACTIVE": "❌ Fehler: Das Twitter-Modul ist derzeit nicht aktiv oder konnte nicht initialisiert werden.",
        "SEARCHING_TWEETS": "🔍 Suche die letzten {count} Tweets von @{username}...",
        "USER_NOT_FOUND": "❌ Twitter-Benutzer @{username} konnte nicht gefunden werden.",
        "LAST_TWEETS_HEADER": "📝 **Die letzten {num_tweets} Tweets von @{username}:**",
        "TWEET_LINK_TEXT": "Link",
        "TWEET_GOTO_LINK": "[Tweet ansehen]({url})",
        "NO_TWEETS_FOUND": "❌ Keine Tweets für @{username} gefunden oder API-Fehler.",
        "HELP_TITLE": "🤖 Bot-Befehlshilfe",
        "HELP_CMD_TWITTER_NAME": "`!twitter <Benutzername> [Anzahl]`",
        "HELP_CMD_TWITTER_VALUE": "Zeigt die letzten Tweets eines Benutzers an (Standard: 5, Max: 25).",
        "HELP_CMD_HELPME_NAME": "`!helpme`",
        "HELP_CMD_HELPME_VALUE": "Zeigt diese Hilfenachricht an.",
        "HELP_CMD_SETLANG_NAME": "`!setlang <Sprachcode>`",
        "HELP_CMD_SETLANG_VALUE": "Legt die Sprache des Bots für diesen Server fest (z.B. `de`, `en`). Erfordert Administratorrechte.",
        "HELP_FOOTER_SERVER": "Bot läuft auf Server {server_name}",
        "HELP_FOOTER_DM": "Bot läuft in Direktnachrichten",
        "NEW_TWEET_ALERT": "🚀 Neuer Tweet von @{username}:\n{text}\n\n🔗 {url}",
        "LANG_SET_SUCCESS": "✅ Sprache für diesen Server auf **{lang}** gesetzt.",
        "LANG_SET_FAIL_INVALID": "❌ Ungültiger Sprachcode. Verfügbare Sprachen: {available_langs}",
        "LANG_SET_FAIL_PERMISSIONS": "❌ Du benötigst Administratorrechte, um die Sprache zu ändern.",
        "LANG_SET_FAIL_DM": "❌ Dieser Befehl kann nur auf einem Server verwendet werden.",
        "LANG_INFO": "ℹ️ Die aktuelle Sprache für diesen Server ist **{lang}**.",
        "ERROR_FORBIDDEN_SEND": "Keine Rechte zum Senden von Nachrichten in Kanal #{channel_name} ({channel_id}) auf Server {server_name}. Rollen prüfen.",
        "WARN_NO_EMBED": "Keine Rechte zum Einbetten von Links in Kanal #{channel_name} ({channel_id}). Links werden möglicherweise nicht korrekt angezeigt.",
        "ERROR_TARGET_CHANNEL_NOT_FOUND": "Zielkanal Discord mit ID {channel_id} nicht найден! Überprüfe TARGET_DISCORD_CHANNEL_ID.",
        "ERROR_NO_GUILD_FOR_CHANNEL": "Konnte den Server für Kanal {channel_id} nicht bestimmen. Senden übersprungen.",
        "ERROR_UNEXPECTED_COMMAND": "Ein unerwarteter Fehler ist bei der Ausführung des Befehls aufgetreten.",
        "TASK_WAITING_BOT": "Фоновая задача: Ожидание готовности бота...",
        "TASK_BOT_READY": "Фоновая задача: Бот готов.",
        "TASK_TWITTER_INIT_FAILED": "Фоновая задача: Клиент Twitter не инициализирован, задача не будет запущена.",
        "TASK_GETTING_USER_ID": "Фоновая задача: Получение ID пользователя Twitter для @{username}...",
        "TASK_USER_ID_SUCCESS": "Фоновая задача: Получен ID пользователя Twitter: {user_id} для @{username}.",
        "TASK_USER_ID_FAIL": "Фоновая задача: Не удалось получить ID пользователя Twitter для @{username}. Проверка будет пропускаться.",
        "TASK_CHECKING_TWEETS": "Фоновая задача: Проверка новых твитов для @{username} (ID: {user_id}), since_id: {since_id}",
        "TASK_FOUND_TWEETS": "Фоновая задача: Найдено {count} новых твитов от @{username}.",
        "TASK_SENDING_TWEET": "Фоновая задача: Твит (ID: {tweet_id}) отправлен в канал {channel_id}",
        "TASK_FORBIDDEN_SEND_LOOP": "Фоновая задача: Forbidden (после проверки прав?): {error_message}",
        "TASK_ERROR_SENDING_TWEET": "Фоновая задача: Не удалось отправить сообщение с твитом ID {tweet_id} в канал {channel_id}.",
        "TASK_SKIPPING_TWEET_KEYWORDS": "Фоновая задача: Твит (ID: {tweet_id}) пропущен (не содержит ключевых слов)",
        "TASK_UPDATING_LAST_ID": "Фоновая задача: Обновление last_seen_tweet_id с {old_id} на {new_id}",
        "TASK_UNHANDLED_ERROR": "Необработанная ошибка в фоновой задаче check_twitter: {error}",
        "BOT_STARTING": "Попытка запуска бота...",
        "BOT_START_SUCCESS": "Запуск бота Discord...",
        "BOT_READY": "Бот {bot_name} (ID: {bot_id}) подключен и готов!",
        "BOT_AVAILABLE_LANGS": "Доступные языки: {langs}",
        "BOT_START_TWITTER_TASK": "Запуск фоновой задачи проверки Twitter...",
        "CRITICAL_TWITTER_INIT_FAIL": "Критическая ошибка: Не удалось инициализировать Twitter клиент. Проверьте TWITTER_BEARER_TOKEN и доступ к API.",
        "CRITICAL_LOGIN_FAIL": "Критическая ошибка: Неверный токен Discord (LoginFailure). Проверьте DISCORD_BOT_TOKEN.",
        "CRITICAL_GENERIC_FAIL": "Критическая ошибка при запуске бота:"
    },
    "en": {
        "TWITTER_INACTIVE": "❌ Error: The Twitter module is currently inactive or failed to initialize.",
        "SEARCHING_TWEETS": "🔍 Searching for the last {count} tweets from @{username}...",
        "USER_NOT_FOUND": "❌ Could not find Twitter user @{username}.",
        "LAST_TWEETS_HEADER": "📝 **Last {num_tweets} tweets from @{username}:**",
        "TWEET_LINK_TEXT": "Link",
        "TWEET_GOTO_LINK": "[Go to Tweet]({url})",
        "NO_TWEETS_FOUND": "❌ No tweets found for @{username} or API error.",
        "HELP_TITLE": "🤖 Bot Command Help",
        "HELP_CMD_TWITTER_NAME": "`!twitter <username> [count]`",
        "HELP_CMD_TWITTER_VALUE": "Shows the latest tweets from a user (Default: 5, Max: 25).",
        "HELP_CMD_HELPME_NAME": "`!helpme`",
        "HELP_CMD_HELPME_VALUE": "Shows this help message.",
        "HELP_CMD_SETLANG_NAME": "`!setlang <language_code>`",
        "HELP_CMD_SETLANG_VALUE": "Sets the bot's language for this server (e.g., `de`, `en`). Requires Administrator permissions.",
        "HELP_FOOTER_SERVER": "Bot running on server {server_name}",
        "HELP_FOOTER_DM": "Bot running in DMs",
        "NEW_TWEET_ALERT": "🚀 New tweet from @{username}:\n{text}\n\n🔗 {url}",
        "LANG_SET_SUCCESS": "✅ Language for this server set to **{lang}**.",
        "LANG_SET_FAIL_INVALID": "❌ Invalid language code. Available languages: {available_langs}",
        "LANG_SET_FAIL_PERMISSIONS": "❌ You need Administrator permissions to change the language.",
        "LANG_SET_FAIL_DM": "❌ This command can only be used on a server.",
        "LANG_INFO": "ℹ️ The current language for this server is **{lang}**.",
        "ERROR_FORBIDDEN_SEND": "No permission to send messages in channel #{channel_name} ({channel_id}) on server {server_name}. Check roles.",
        "WARN_NO_EMBED": "No permission to embed links in channel #{channel_name} ({channel_id}). Links might not display correctly.",
        "ERROR_TARGET_CHANNEL_NOT_FOUND": "Target Discord channel with ID {channel_id} not found! Check TARGET_DISCORD_CHANNEL_ID.",
        "ERROR_NO_GUILD_FOR_CHANNEL": "Could not determine the server for channel {channel_id}. Skipping send.",
        "ERROR_UNEXPECTED_COMMAND": "An unexpected error occurred while executing the command.",
        "TASK_WAITING_BOT": "Background Task: Waiting for bot to be ready...",
        "TASK_BOT_READY": "Background Task: Bot is ready.",
        "TASK_TWITTER_INIT_FAILED": "Background Task: Twitter client not initialized, task will not run.",
        "TASK_GETTING_USER_ID": "Background Task: Getting Twitter user ID for @{username}...",
        "TASK_USER_ID_SUCCESS": "Background Task: Obtained Twitter user ID: {user_id} for @{username}.",
        "TASK_USER_ID_FAIL": "Background Task: Failed to get Twitter user ID for @{username}. Skipping checks.",
        "TASK_CHECKING_TWEETS": "Background Task: Checking for new tweets for @{username} (ID: {user_id}), since_id: {since_id}",
        "TASK_FOUND_TWEETS": "Background Task: Found {count} new tweets from @{username}.",
        "TASK_SENDING_TWEET": "Background Task: Tweet (ID: {tweet_id}) sent to channel {channel_id}",
        "TASK_FORBIDDEN_SEND_LOOP": "Background Task: Forbidden (after permission check?): {error_message}",
        "TASK_ERROR_SENDING_TWEET": "Background Task: Failed to send message for tweet ID {tweet_id} to channel {channel_id}.",
        "TASK_SKIPPING_TWEET_KEYWORDS": "Background Task: Tweet (ID: {tweet_id}) skipped (doesn't contain keywords)",
        "TASK_UPDATING_LAST_ID": "Background Task: Updating last_seen_tweet_id from {old_id} to {new_id}",
        "TASK_UNHANDLED_ERROR": "Unhandled error in background task check_twitter: {error}",
        "BOT_STARTING": "Attempting to start the bot...",
        "BOT_START_SUCCESS": "Starting Discord bot...",
        "BOT_READY": "Bot {bot_name} (ID: {bot_id}) is connected and ready!",
        "BOT_AVAILABLE_LANGS": "Available languages: {langs}",
        "BOT_START_TWITTER_TASK": "Starting Twitter check background task...",
        "CRITICAL_TWITTER_INIT_FAIL": "Critical Error: Failed to initialize Twitter client. Check TWITTER_BEARER_TOKEN and API access.",
        "CRITICAL_LOGIN_FAIL": "Critical Error: Invalid Discord Token (LoginFailure). Check DISCORD_BOT_TOKEN.",
        "CRITICAL_GENERIC_FAIL": "Critical error during bot startup:"
    }
    # Добавьте сюда русский (ru) или другие языки по аналогии
}

DEFAULT_LANGUAGE = CONFIG['DEFAULT_LANGUAGE']

# --- Функция-переводчик ---
# Принимает экземпляр SettingsManager для получения языка сервера
def get_translator(settings_manager):
    """Возвращает функцию перевода, замыкающую в себе settings_manager."""
    def _(key, guild_id=None, **kwargs):
        lang = settings_manager.get_server_language(guild_id)
        # Попытаться получить строку для нужного языка
        message = translations.get(lang, {}).get(key)
        # Если нет, попытаться получить для языка по умолчанию
        if message is None and lang != DEFAULT_LANGUAGE:
            log.debug("Key '%s' not found for lang '%s', trying default '%s'", key, lang, DEFAULT_LANGUAGE)
            message = translations.get(DEFAULT_LANGUAGE, {}).get(key)
        # Если все еще нет, вернуть сам ключ или строку ошибки
        if message is None:
            log.warning("Translation key '%s' not found for language '%s' or default language '%s'.",
                        key, lang, DEFAULT_LANGUAGE)
            return f"<{key}_TRANSLATION_MISSING>"

        # Форматировать строку, если переданы аргументы
        try:
            return message.format(**kwargs)
        except KeyError as e:
            log.error("Formatting error for key '%s' (lang '%s'): missing argument %s. Provided args: %s", key, lang, e, kwargs)
            return f"<{key}_FORMATTING_ERROR: Missing {e}>"
        except Exception as e:
            log.error("Generic formatting error for key '%s' (lang '%s'): %s. Provided args: %s", key, lang, e, kwargs)
            return f"<{key}_UNEXPECTED_FORMATTING_ERROR>"
    return _

def get_available_languages():
    """Возвращает список кодов доступных языков."""
    return list(translations.keys())
EOF

# --- Файл: project/bot/settings.py ---
cat << EOF > project/bot/settings.py
import json
import os
import logging
from .config import CONFIG, SERVER_SETTINGS_FILE  # Импортируем дефолтный язык и имя файла

log = logging.getLogger('discord_twitter_bot.settings')

class SettingsManager:
    """Класс для управления настройками серверов (язык и т.д.)."""
    def __init__(self, file_path=SERVER_SETTINGS_FILE, default_lang=CONFIG['DEFAULT_LANGUAGE']):
        self.file_path = file_path
        self.default_lang = default_lang
        self.server_settings = self._load_settings()

    def _load_settings(self):
        """Загружает настройки из JSON файла."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                log.info("Настройки серверов загружены из %s", self.file_path)
                return settings
            except json.JSONDecodeError:
                log.error("Ошибка декодирования JSON из %s. Файл может быть поврежден. Используются настройки по умолчанию.", self.file_path)
            except Exception:
                log.exception("Не удалось загрузить настройки серверов из %s. Используются настройки по умолчанию.", self.file_path)
        else:
            log.info("Файл настроек %s не найден, используются настройки по умолчанию.", self.file_path)
        return {} # Возвращаем пустой словарь в случае ошибки или отсутствия файла

    def _save_settings(self):
        """Сохраняет текущие настройки в JSON файл."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.server_settings, f, indent=4)
            log.debug("Настройки серверов сохранены в %s", self.file_path)
        except Exception:
            log.exception("Не удалось сохранить настройки серверов в %s.", self.file_path)

    def get_server_language(self, guild_id):
        """Получает язык для сервера или язык по умолчанию."""
        if guild_id:
            return self.server_settings.get(str(guild_id), {}).get("language", self.default_lang)
        return self.default_lang # Для DM или если guild_id не предоставлен

    def set_server_language(self, guild_id, lang_code):
        """Устанавливает язык для сервера и сохраняет настройки."""
        # Валидацию языка лучше проводить перед вызовом этого метода,
        # но можно добавить и сюда, если нужно.
        # from .translations import get_available_languages # Импорт внутри для избежания цикла
        # if lang_code not in get_available_languages():
        #    return False

        guild_id_str = str(guild_id)
        if guild_id_str not in self.server_settings:
            self.server_settings[guild_id_str] = {}
        self.server_settings[guild_id_str]["language"] = lang_code
        self._save_settings()
        log.info("Язык для сервера %s изменен на '%s'", guild_id_str, lang_code)
        return True

# Пример создания экземпляра менеджера настроек (обычно делается в main.py)
# settings_manager = SettingsManager()
EOF

# --- Файл: project/bot/twitter_client.py ---
cat << EOF > project/bot/twitter_client.py
import tweepy
import logging
from typing import Optional, List, Dict, Any

log = logging.getLogger('discord_twitter_bot.twitter')

class TwitterService:
    """Класс для взаимодействия с Twitter API v2."""
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.client: Optional[tweepy.Client] = None
        self.init_failed: bool = False
        self._initialize_client()

    def _initialize_client(self):
        """Инициализирует клиент Tweepy."""
        if not self.bearer_token:
            log.error("Bearer token для Twitter не предоставлен.")
            self.init_failed = True
            return
        try:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                wait_on_rate_limit=True # Ожидать, если достигнут лимит запросов
            )
            # Пробный запрос для проверки аутентификации (например, информация о себе)
            # Это необязательно, но может помочь выявить проблемы раньше
            # self.client.get_me()
            log.info("Клиент Tweepy успешно инициализирован.")
        except tweepy.errors.TweepyException as e:
            log.exception("Ошибка инициализации клиента Tweepy: %s", e)
            self.init_failed = True
        except Exception as e:
            log.exception("Неожиданная ошибка при инициализации клиента Tweepy: %s", e)
            self.init_failed = True

    async def get_user_id_v2(self, username: str) -> Optional[int]:
        """Получает ID пользователя Twitter по его имени пользователя (v2 API)."""
        if self.init_failed or not self.client:
            log.warning("Попытка получить ID пользователя, но клиент Twitter не инициализирован.")
            return None
        try:
            log.debug("Запрос ID для пользователя @%s", username)
            response = self.client.get_user(username=username)
            if response.data:
                user_id = response.data.id
                log.debug("Найден ID %d для пользователя @%s", user_id, username)
                return user_id
            else:
                log.warning("Пользователь @%s не найден через API v2.", username)
                return None
        except tweepy.errors.NotFound:
             log.warning("Пользователь @%s не найден (404).", username)
             return None
        except tweepy.errors.TweepyException as e:
            log.error("Ошибка API Twitter при получении ID для @%s: %s", username, e)
            return None
        except Exception as e:
            log.exception("Неожиданная ошибка при получении ID для @%s: %s", username, e)
            return None

    async def get_tweets_v2(self, user_id: int, count: int = 5, since_id: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """Получает последние твиты пользователя по ID (v2 API)."""
        if self.init_failed or not self.client:
            log.warning("Попытка получить твиты, но клиент Twitter не инициализирован.")
            return None
        try:
            log.debug("Запрос %d твитов для user_id %d, since_id: %s", count, user_id, since_id)
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=max(5, min(100, count)), # API v2 имеет min 5 для max_results
                since_id=since_id,
                tweet_fields=["created_at", "public_metrics"] # Запрашиваем доп. поля
            )
            if response.data:
                # Преобразуем в более удобный формат словаря для совместимости
                tweets_data = []
                for tweet in response.data:
                    tweets_data.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        # Можно добавить другие поля при необходимости
                        # 'retweet_count': tweet.public_metrics['retweet_count'] if tweet.public_metrics else 0,
                    })
                log.debug("Получено %d твитов для user_id %d", len(tweets_data), user_id)
                return tweets_data
            else:
                log.debug("Новых твитов не найдено для user_id %d (since_id: %s)", user_id, since_id)
                return [] # Возвращаем пустой список, если твитов нет
        except tweepy.errors.TweepyException as e:
            log.error("Ошибка API Twitter при получении твитов для user_id %d: %s", user_id, e)
            return None
        except Exception as e:
            log.exception("Неожиданная ошибка при получении твитов для user_id %d: %s", user_id, e)
            return None

# Пример создания экземпляра сервиса (обычно делается в main.py)
# twitter_service = TwitterService(CONFIG['TWITTER_BEARER_TOKEN'])
EOF

# --- Файл: project/bot/commands.py ---
cat << EOF > project/bot/commands.py
import discord
from discord.ext import commands
import logging
from typing import TYPE_CHECKING

# Используем TYPE_CHECKING для избежания цикличных импортов при проверке типов
if TYPE_CHECKING:
    from .twitter_client import TwitterService
    from .settings import SettingsManager
    from .translations import get_translator # Функция для получения функции _

log = logging.getLogger('discord_twitter_bot.commands')

class CommandsCog(commands.Cog, name="Основные команды"):
    """Ког, содержащий основные команды бота."""

    def __init__(self, bot: commands.Bot, twitter_service: 'TwitterService', settings_manager: 'SettingsManager', translator_func):
        self.bot = bot
        self.twitter_service = twitter_service
        self.settings_manager = settings_manager
        self._ = translator_func # Сохраняем функцию перевода
        from .translations import get_available_languages # Импортируем здесь
        self.available_langs = get_available_languages()
        log.info("Ког команд инициализирован.")

    # --- Команда !setlang ---
    @commands.command(name="setlang")
    @commands.has_permissions(administrator=True)
    @commands.guild_only() # Команда доступна только на сервере
    async def setlang_command(self, ctx: commands.Context, lang_code: str):
        """Устанавливает язык бота для текущего сервера."""
        guild_id = ctx.guild.id
        lang_code = lang_code.lower()
        available_langs_str = ", ".join(f"`{code}`" for code in self.available_langs)

        if lang_code not in self.available_langs:
            await ctx.send(self._("LANG_SET_FAIL_INVALID", guild_id, available_langs=available_langs_str))
            return

        if self.settings_manager.set_server_language(guild_id, lang_code):
            await ctx.send(self._("LANG_SET_SUCCESS", guild_id, lang=lang_code))
            log.info("Язык для сервера %d (%s) изменен на '%s' пользователем %s (%d)",
                     guild_id, ctx.guild.name, lang_code, ctx.author.name, ctx.author.id)
        else:
            # Эта ветка может быть недостижима из-за _save_settings, но на всякий случай
             await ctx.send(self._("ERROR_UNEXPECTED_COMMAND", guild_id))


    @setlang_command.error
    async def setlang_command_error(self, ctx: commands.Context, error):
        """Обработчик ошибок для команды !setlang."""
        guild_id = ctx.guild.id if ctx.guild else None
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(self._("LANG_SET_FAIL_PERMISSIONS", guild_id))
        elif isinstance(error, commands.NoPrivateMessage):
            # Используем перевод по умолчанию, т.к. нет guild_id
            await ctx.send(self._("LANG_SET_FAIL_DM", None))
        elif isinstance(error, commands.MissingRequiredArgument):
             await ctx.send(self._("LANG_SET_FAIL_INVALID", guild_id, available_langs=", ".join(f"`{code}`" for code in self.available_langs)))
        else:
            log.error("Неожиданная ошибка в команде setlang для сервера %s: %s", guild_id, error, exc_info=error)
            await ctx.send(self._("ERROR_UNEXPECTED_COMMAND", guild_id))


    # --- Команда !twitter ---
    @commands.command(name="twitter")
    async def twitter_command(self, ctx: commands.Context, username: str, count: int = 5):
        """Показывает последние твиты указанного пользователя Twitter."""
        guild_id = ctx.guild.id if ctx.guild else None

        if self.twitter_service.init_failed:
            await ctx.send(self._("TWITTER_INACTIVE", guild_id))
            return

        # Ограничиваем количество твитов
        count = max(1, min(25, count)) # Ограничение discord на эмбеды тоже есть

        # Отправляем сообщение о поиске
        try:
            processing_msg = await ctx.send(self._("SEARCHING_TWEETS", guild_id, count=count, username=username))
        except discord.Forbidden:
             log.warning(f"Нет прав на отправку сообщения в канале {ctx.channel.id} ({ctx.channel.name}) сервера {ctx.guild.name if ctx.guild else 'DM'}")
             return # Не можем даже сообщить об ошибке
        except Exception as e:
            log.error(f"Ошибка отправки 'searching' сообщения: {e}")
            processing_msg = None # Продолжаем, но не сможем редактировать

        user_id = await self.twitter_service.get_user_id_v2(username)
        if not user_id:
            error_message = self._("USER_NOT_FOUND", guild_id, username=username)
            if processing_msg: await processing_msg.edit(content=error_message)
            else: await ctx.send(error_message)
            return

        tweets = await self.twitter_service.get_tweets_v2(user_id, count=count)

        if tweets is None: # Ошибка API
             error_message = self._("NO_TWEETS_FOUND", guild_id, username=username) # Используем общий ключ
             if processing_msg: await processing_msg.edit(content=error_message)
             else: await ctx.send(error_message)
             return

        if not tweets: # Пустой список (нет твитов)
            message = self._("NO_TWEETS_FOUND", guild_id, username=username)
            if processing_msg: await processing_msg.edit(content=message)
            else: await ctx.send(message)
            return

        # Удаляем сообщение "Searching..." если оно было
        if processing_msg:
            try:
                await processing_msg.delete()
            except discord.NotFound:
                pass # Уже удалено кем-то другим?
            except discord.Forbidden:
                 log.warning(f"Нет прав на удаление сообщения в канале {ctx.channel.id}")


        # Отправляем заголовок
        await ctx.send(self._("LAST_TWEETS_HEADER", guild_id, num_tweets=len(tweets), username=username))

        # Отправляем твиты в отдельных эмбедах
        for tweet in tweets:
            tweet_url = f"https://twitter.com/{username}/status/{tweet['id']}"
            embed = discord.Embed(description=tweet['text'], color=discord.Color.blue())
            # Пытаемся установить аватар автора команды как иконку, если возможно
            icon_url = ctx.author.display_avatar.url if ctx.author.display_avatar else None
            embed.set_author(name=f"@{username}", url=tweet_url, icon_url=icon_url)
            embed.add_field(name=self._("TWEET_LINK_TEXT", guild_id), value=self._("TWEET_GOTO_LINK", guild_id, url=tweet_url), inline=False)
            if tweet.get('created_at'):
                embed.timestamp = tweet['created_at']

            try:
                await ctx.send(embed=embed)
            except discord.Forbidden:
                 log.error(f"Нет прав на отправку embed в канале {ctx.channel.id}. Отправка твитов прервана.")
                 await ctx.send(self._("ERROR_FORBIDDEN_SEND", guild_id, channel_name=ctx.channel.name, channel_id=ctx.channel.id, server_name=ctx.guild.name if ctx.guild else "DM"))
                 break # Прерываем отправку остальных твитов
            except Exception as e:
                 log.exception(f"Ошибка при отправке embed твита {tweet['id']}: {e}")


    # --- Команда !helpme ---
    @commands.command(name="helpme")
    async def helpme_command(self, ctx: commands.Context):
        """Показывает справочное сообщение со списком команд."""
        guild_id = ctx.guild.id if ctx.guild else None
        current_lang = self.settings_manager.get_server_language(guild_id)

        embed = discord.Embed(title=self._("HELP_TITLE", guild_id), color=discord.Color.green())

        # Добавляем команды динамически (если они есть в коге)
        if self.get_command('twitter'):
             embed.add_field(name=self._("HELP_CMD_TWITTER_NAME", guild_id), value=self._("HELP_CMD_TWITTER_VALUE", guild_id), inline=False)
        if self.get_command('setlang'):
             embed.add_field(name=self._("HELP_CMD_SETLANG_NAME", guild_id), value=self._("HELP_CMD_SETLANG_VALUE", guild_id), inline=False)
        if self.get_command('helpme'):
            embed.add_field(name=self._("HELP_CMD_HELPME_NAME", guild_id), value=self._("HELP_CMD_HELPME_VALUE", guild_id), inline=False)

        # Информация о текущем языке
        embed.add_field(name="---", value=self._("LANG_INFO", guild_id, lang=current_lang), inline=False)

        # Footer
        footer_text = ""
        if ctx.guild:
            footer_text = self._("HELP_FOOTER_SERVER", guild_id, server_name=ctx.guild.name)
        else:
            footer_text = self._("HELP_FOOTER_DM", guild_id)
        if self.bot.user:
             footer_text += f" | Bot ID: {self.bot.user.id}"
        embed.set_footer(text=footer_text)

        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            log.error(f"Нет прав на отправку embed в канале {ctx.channel.id} для команды help.")
            # Попытка отправить простое текстовое сообщение
            try:
                 await ctx.send(f"Не могу отправить справку (нет прав на Embed). Текущий язык: {current_lang}")
            except discord.Forbidden:
                pass # Совсем нет прав


# Функция setup для загрузки кога ботом
# Передаем сюда зависимости, созданные в main.py
async def setup(bot: commands.Bot, twitter_service: 'TwitterService', settings_manager: 'SettingsManager', translator_func):
    await bot.add_cog(CommandsCog(bot, twitter_service, settings_manager, translator_func))
    log.info("Ког CommandsCog успешно загружен.")

EOF

# --- Файл: project/bot/tasks.py ---
cat << EOF > project/bot/tasks.py
import discord
from discord.ext import commands, tasks
import logging
import os
from typing import Optional, TYPE_CHECKING

# Используем TYPE_CHECKING для избежания цикличных импортов
if TYPE_CHECKING:
    from .twitter_client import TwitterService
    from .settings import SettingsManager
    from .config import CONFIG # Словарь конфигурации
    from .translations import get_translator # Функция для получения функции _

# Импортируем имя файла для last_tweet_id
from .config import LAST_TWEET_ID_FILE

log = logging.getLogger('discord_twitter_bot.tasks')

class TasksCog(commands.Cog, name="Фоновые задачи"):
    """Ког, содержащий фоновые задачи, такие как проверка Twitter."""

    def __init__(self, bot: commands.Bot, config: dict, twitter_service: 'TwitterService', settings_manager: 'SettingsManager', translator_func):
        self.bot = bot
        self.config = config # Сохраняем всю конфигурацию
        self.twitter_service = twitter_service
        self.settings_manager = settings_manager
        self._ = translator_func # Функция перевода
        self.target_user_id: Optional[int] = None
        self.last_seen_tweet_id: Optional[int] = self._load_last_tweet_id()
        self.target_channel: Optional[discord.TextChannel] = None # Кэшируем целевой канал
        log.info("Ког задач инициализирован. Last seen tweet ID: %s", self.last_seen_tweet_id)
        self.check_twitter.start() # Запускаем задачу при инициализации кога

    def cog_unload(self):
        """Вызывается при выгрузке кога."""
        self.check_twitter.cancel()
        log.info("Фоновая задача check_twitter остановлена.")

    def _load_last_tweet_id(self) -> Optional[int]:
        """Загружает ID последнего виденного твита из файла."""
        try:
            if os.path.exists(LAST_TWEET_ID_FILE):
                with open(LAST_TWEET_ID_FILE, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return int(content)
                    else:
                        log.warning(f"Файл {LAST_TWEET_ID_FILE} пуст.")
                        return None
            else:
                log.info(f"Файл {LAST_TWEET_ID_FILE} не найден. Будут обработаны последние твиты при первом запуске.")
                return None # Нет файла - значит, не видели еще твитов
        except ValueError:
            log.error(f"Некорректное значение в файле {LAST_TWEET_ID_FILE}. Ожидалось число.")
            return None
        except Exception as e:
            log.exception(f"Ошибка при загрузке ID последнего твита из {LAST_TWEET_ID_FILE}: {e}")
            return None

    def _save_last_tweet_id(self):
        """Сохраняет ID последнего обработанного твита в файл."""
        if self.last_seen_tweet_id is None:
            return # Нечего сохранять
        try:
            with open(LAST_TWEET_ID_FILE, 'w') as f:
                f.write(str(self.last_seen_tweet_id))
            log.debug(f"ID последнего твита ({self.last_seen_tweet_id}) сохранен в {LAST_TWEET_ID_FILE}")
        except Exception as e:
            log.exception(f"Ошибка при сохранении ID последнего твита ({self.last_seen_tweet_id}) в {LAST_TWEET_ID_FILE}: {e}")

    @tasks.loop(minutes=15) # Интервал проверки
    async def check_twitter(self):
        """Периодически проверяет новые твиты целевого пользователя."""
        # Проверяем, инициализирован ли Twitter клиент и получен ли ID пользователя
        if self.twitter_service.init_failed or not self.target_user_id:
            # Логирование причин пропуска происходит в before_loop или при инициализации TwitterService
            return

        if not self.target_channel:
             log.warning("Целевой канал не найден или не кэширован. Пропуск проверки.")
             # Попытаться найти канал снова (возможно, бот переподключился)
             self.target_channel = self.bot.get_channel(self.config['TARGET_CHANNEL_ID'])
             if not self.target_channel:
                 log.error(self._("ERROR_TARGET_CHANNEL_NOT_FOUND", None, channel_id=self.config['TARGET_CHANNEL_ID']))
                 return # Все еще не можем найти канал
             else:
                 log.info(f"Целевой канал {self.target_channel.name} ({self.target_channel.id}) найден.")


        log.info(self._("TASK_CHECKING_TWEETS", None, # Логируем на языке по умолчанию
                      username=self.config['TWITTER_USER_TO_MONITOR'],
                      user_id=self.target_user_id,
                      since_id=self.last_seen_tweet_id))

        # Получаем твиты СТРОГО новее последнего виденного
        tweets = await self.twitter_service.get_tweets_v2(self.target_user_id, count=20, since_id=self.last_seen_tweet_id)

        if tweets is None: # Ошибка API
            log.error("Ошибка API Twitter при получении твитов в фоновой задаче.")
            return
        if not tweets: # Нет новых твитов
            log.info("Новых твитов не найдено.")
            return

        log.info(self._("TASK_FOUND_TWEETS", None, count=len(tweets), username=self.config['TWITTER_USER_TO_MONITOR']))

        # Твиты приходят от новых к старым, переворачиваем для обработки от старых к новым
        tweets.reverse()

        newest_processed_id = self.last_seen_tweet_id # Запоминаем ID до начала обработки
        guild = self.target_channel.guild
        current_guild_id = guild.id if guild else None

        if not guild:
            # Это не должно произойти для TextChannel, но на всякий случай
            log.warning(self._("ERROR_NO_GUILD_FOR_CHANNEL", None, channel_id=self.target_channel.id))
            return # Не можем проверить права или перевести без сервера

        # Проверяем права перед циклом (немного оптимизации)
        me = guild.me
        permissions = self.target_channel.permissions_for(me)
        can_send = permissions.send_messages
        can_embed = permissions.embed_links

        if not can_send:
            err_msg = self._("ERROR_FORBIDDEN_SEND", current_guild_id,
                             channel_name=self.target_channel.name, channel_id=self.target_channel.id, server_name=guild.name)
            log.error(err_msg)
            # Возможно, стоит остановить задачу или выдать более серьезное предупреждение?
            return

        if not can_embed:
             log.warning(self._("WARN_NO_EMBED", current_guild_id,
                                channel_name=self.target_channel.name, channel_id=self.target_channel.id))

        # --- Обработка найденных твитов ---
        for tweet in tweets:
            current_tweet_id = tweet['id']
            tweet_text_lower = tweet['text'].lower()

            # Проверка ключевых слов (если они заданы)
            keywords = self.config['KEYWORDS']
            if not keywords or any(keyword in tweet_text_lower for keyword in keywords):
                tweet_url = f"https://twitter.com/{self.config['TWITTER_USER_TO_MONITOR']}/status/{tweet['id']}"

                # --- Используем переводчик с ID сервера канала ---
                message = self._("NEW_TWEET_ALERT", current_guild_id,
                                 username=self.config['TWITTER_USER_TO_MONITOR'], text=tweet['text'], url=tweet_url)
                try:
                    # Отправляем сообщение (без embed, если нет прав)
                    await self.target_channel.send(message, suppress_embeds=not can_embed)
                    log.info(self._("TASK_SENDING_TWEET", None, tweet_id=tweet['id'], channel_id=self.target_channel.id))
                    newest_processed_id = current_tweet_id # Обновляем ID только после успешной отправки

                except discord.errors.Forbidden:
                    # Эта ошибка не должна возникать после проверки прав, но может быть из-за временных проблем
                    err_msg = self._("ERROR_FORBIDDEN_SEND", current_guild_id,
                                     channel_name=self.target_channel.name, channel_id=self.target_channel.id, server_name=guild.name)
                    log.error(self._("TASK_FORBIDDEN_SEND_LOOP", None, error_message=err_msg))
                    break # Прерываем обработку, т.к. вероятно, проблема сохранится
                except Exception:
                    log.exception(self._("TASK_ERROR_SENDING_TWEET", None, tweet_id=tweet['id'], channel_id=self.target_channel.id))
                    # Не обновляем newest_processed_id, попробуем отправить этот твит в следующий раз
                    # Но прерываем текущий цикл, чтобы избежать спама ошибками
                    break
            else:
                log.debug(self._("TASK_SKIPPING_TWEET_KEYWORDS", None, tweet_id=tweet['id']))
                # Важно обновить ID, даже если твит пропущен по ключевым словам,
                # чтобы не проверять его снова
                newest_processed_id = current_tweet_id

        # --- Сохраняем ID последнего *обработанного* или *пропущенного* твита ---
        if newest_processed_id != self.last_seen_tweet_id:
             log.info(self._("TASK_UPDATING_LAST_ID", None, old_id=self.last_seen_tweet_id, new_id=newest_processed_id))
             self.last_seen_tweet_id = newest_processed_id
             self._save_last_tweet_id()


    @check_twitter.before_loop
    async def before_check_twitter(self):
        """Выполняется перед каждым запуском цикла проверки."""
        log.info(self._("TASK_WAITING_BOT", None))
        await self.bot.wait_until_ready() # Ждем полной готовности бота
        log.info(self._("TASK_BOT_READY", None))

        # Проверяем инициализацию Twitter клиента один раз перед запуском цикла
        if self.twitter_service.init_failed:
             log.warning(self._("TASK_TWITTER_INIT_FAILED", None))
             self.check_twitter.stop() # Останавливаем задачу, если Twitter недоступен
             return

        # Получаем ID пользователя, если еще не получили
        if not self.target_user_id:
            log.info(self._("TASK_GETTING_USER_ID", None, username=self.config['TWITTER_USER_TO_MONITOR']))
            self.target_user_id = await self.twitter_service.get_user_id_v2(self.config['TWITTER_USER_TO_MONITOR'])
            if self.target_user_id:
                log.info(self._("TASK_USER_ID_SUCCESS", None, user_id=self.target_user_id, username=self.config['TWITTER_USER_TO_MONITOR']))
            else:
                log.error(self._("TASK_USER_ID_FAIL", None, username=self.config['TWITTER_USER_TO_MONITOR']))
                self.check_twitter.stop() # Останавливаем задачу, если не можем получить ID
                return

        # Кэшируем целевой канал
        if not self.target_channel:
            self.target_channel = self.bot.get_channel(self.config['TARGET_CHANNEL_ID'])
            if not self.target_channel:
                 log.error(self._("ERROR_TARGET_CHANNEL_NOT_FOUND", None, channel_id=self.config['TARGET_CHANNEL_ID']))
                 # Не останавливаем задачу, она сама будет проверять канал в цикле
            elif not isinstance(self.target_channel, discord.TextChannel):
                 log.error(f"Канал с ID {self.config['TARGET_CHANNEL_ID']} не является текстовым каналом!")
                 self.target_channel = None # Сбрасываем, чтобы не использовать неверный тип
            else:
                 log.info(f"Целевой канал для отправки твитов: #{self.target_channel.name} ({self.target_channel.id})")


    @check_twitter.error
    async def on_check_twitter_error(self, error):
        """Обработчик необработанных ошибок в цикле задачи."""
        log.exception(self._("TASK_UNHANDLED_ERROR", None, error=error))
        # Здесь можно добавить логику перезапуска задачи или уведомления администратора


# Функция setup для загрузки кога ботом
async def setup(bot: commands.Bot, config: dict, twitter_service: 'TwitterService', settings_manager: 'SettingsManager', translator_func):
    await bot.add_cog(TasksCog(bot, config, twitter_service, settings_manager, translator_func))
    log.info("Ког TasksCog успешно загружен.")

EOF

# --- Файл: project/bot/main.py ---
cat << EOF > project/bot/main.py
import discord
from discord.ext import commands
import asyncio
import logging
import sys
import traceback

# --- Импорты из нашего пакета ---
# Порядок важен: сначала config и logger
from .config import CONFIG, log, check_env_vars
# Затем остальные компоненты
from .settings import SettingsManager
from .twitter_client import TwitterService
from .translations import get_translator, get_available_languages # Функции, не сам словарь

# --- Основная асинхронная функция ---
async def main():
    """Основная функция для инициализации и запуска бота."""

    # 1. Проверка переменных окружения (уже выполняется при импорте config)
    # check_env_vars() # Можно вызвать повторно для ясности, но не обязательно

    # 2. Инициализация менеджера настроек
    settings_manager = SettingsManager()

    # 3. Инициализация сервиса Twitter
    twitter_service = TwitterService(CONFIG['TWITTER_BEARER_TOKEN'])
    if twitter_service.init_failed:
         log.critical(get_translator(settings_manager)("CRITICAL_TWITTER_INIT_FAIL", None))
         # Решаем, стоит ли продолжать без Twitter или выйти
         # sys.exit("Критическая ошибка: Не удалось инициализировать Twitter клиент.") # Раскомментировать для выхода

    # 4. Получение функции-переводчика
    # Передаем settings_manager в фабрику переводчиков
    _ = get_translator(settings_manager)

    # 5. Настройка намерений (Intents) Discord
    intents = discord.Intents.default()
    intents.guilds = True       # Для работы с серверами (роли, каналы)
    intents.messages = True     # Для чтения сообщений (команды)
    intents.message_content = True # ВАЖНО: Для чтения содержимого сообщений (префиксные команды)
    # Убедитесь, что этот Intent включен в настройках вашего бота на портале разработчиков Discord!

    # 6. Создание экземпляра бота
    bot = commands.Bot(
        command_prefix="!",     # Префикс команд
        intents=intents,
        help_command=None       # Отключаем встроенную команду help, т.к. у нас своя (!helpme)
    )

    # --- Обработчики событий бота ---
    @bot.event
    async def on_ready():
        """Вызывается, когда бот успешно подключился и готов к работе."""
        log.info(_("BOT_READY", None, bot_name=bot.user.name, bot_id=bot.user.id))
        log.info(_("BOT_AVAILABLE_LANGS", None, langs=", ".join(get_available_languages())))
        # Запуск фоновой задачи (теперь происходит при загрузке кога TasksCog)
        # if not twitter_service.init_failed:
        #    log.info(_("BOT_START_TWITTER_TASK", None))
        #    # Запуск задачи происходит в TasksCog.__init__

    @bot.event
    async def on_command_error(ctx: commands.Context, error):
        """Глобальный обработчик ошибок команд (если не обработаны в коге)."""
        guild_id = ctx.guild.id if ctx.guild else None
        if isinstance(error, commands.CommandNotFound):
            # Игнорируем неизвестные команды, чтобы не спамить в лог
            log.debug(f"Неизвестная команда: {ctx.message.content}")
            return
        elif isinstance(error, commands.CommandInvokeError):
            # Ошибка внутри самой команды
            original_error = error.original
            log.exception(f"Ошибка при выполнении команды '{ctx.command.qualified_name}': {original_error}", exc_info=original_error)
            await ctx.send(_("ERROR_UNEXPECTED_COMMAND", guild_id))
        elif isinstance(error, commands.MissingRequiredArgument):
            # Не хватает аргументов
            await ctx.send(f"Не хватает аргумента: `{error.param.name}`. Используйте `!helpme` для справки.")
        elif isinstance(error, commands.CheckFailure):
            # Общая ошибка проверки (например, не админ, не на сервере)
            # Эти ошибки лучше обрабатывать в @command.error внутри кога
            log.warning(f"Ошибка проверки для команды '{ctx.command.qualified_name}': {error}")
            # Можно отправить общее сообщение об отказе в доступе, если не обработано локально
            # await ctx.send("У вас нет прав для выполнения этой команды или она недоступна здесь.")
        else:
            # Другие необработанные ошибки discord.py
            log.exception(f"Необработанная ошибка команды: {error}", exc_info=error)
            await ctx.send(_("ERROR_UNEXPECTED_COMMAND", guild_id))


    # 7. Загрузка когов (модулей с командами и задачами)
    async with bot:
        try:
            log.info("Загрузка когов...")
            # Передаем зависимости в setup функции когов
            # Используем await, так как setup когов асинхронный
            await commands.setup(bot, twitter_service, settings_manager, _) # Ког команд
            # Передаем также config в ког задач, т.к. он использует много параметров
            await tasks.setup(bot, CONFIG, twitter_service, settings_manager, _) # Ког задач
            log.info("Все коги успешно загружены.")
        except Exception as e:
             log.exception(f"Ошибка при загрузке когов: {e}")
             await bot.close() # Закрываем бота, если коги не загрузились
             return # Выходим из main

        # 8. Запуск бота
        log.info(_("BOT_START_SUCCESS", None))
        try:
            await bot.start(CONFIG['TOKEN'])
        except discord.errors.LoginFailure:
            log.critical(_("CRITICAL_LOGIN_FAIL", None))
            sys.exit("Критическая ошибка: Неверный токен Discord.")
        except Exception as e:
            log.critical(_("CRITICAL_GENERIC_FAIL", None))
            log.exception(e) # Логируем полное исключение
            sys.exit(f"Критическая ошибка при запуске бота: {e}")


# --- Точка входа ---
if __name__ == "__main__":
    # Запускаем асинхронную функцию main
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Бот остановлен вручную (KeyboardInterrupt).")
    except Exception as e:
        # Ловим любые другие ошибки на самом верхнем уровне
        print(f"Фатальная ошибка вне цикла событий asyncio: {e}", file=sys.stderr)
        traceback.print_exc()

EOF

echo "Создание файла requirements.txt..."
# --- Файл: project/requirements.txt ---
cat << EOF > project/requirements.txt
discord.py>=2.0.0 # Указываем версию 2.x для поддержки Intents и Cogs
python-dotenv
tweepy>=4.0.0 # Указываем версию 4.x для API v2
EOF

echo "Создание файла .gitignore..."
# --- Файл: project/.gitignore ---
cat << EOF > project/.gitignore
# Python
__pycache__/
*.py[cod]
*$py.class

# Virtual environment
venv/
.venv/
env/
ENV/
# Если вы используете другое имя для venv, добавьте его

# Environment variables
.env

# Log files
*.log
logs/

# Runtime files
*.pid
*.seed
*.db
*.sqlite*

# Bot specific state files
last_tweet.id
server_settings.json

# OS generated files
.DS_Store
Thumbs.db
EOF

echo "Создание файла .env.example (ШАБЛОН)..."
# --- Файл: project/.env.example ---
# ВАЖНО: Переименуйте этот файл в .env и заполните своими значениями!
cat << EOF > project/.env.example
# --- Discord Bot Token ---
# Получите его здесь: https://discord.com/developers/applications
DISCORD_BOT_TOKEN=ВАШ_ДИСКОРД_БОТ_ТОКЕН

# --- Twitter API v2 Bearer Token ---
# Получите его из вашего проекта на Twitter Developer Portal
TWITTER_BEARER_TOKEN=ВАШ_ТВИТТЕР_BEARER_ТОКЕН

# --- Target Discord Channel ID ---
# ID канала, куда бот будет постить новые твиты (включите режим разработчика в Discord)
TARGET_DISCORD_CHANNEL_ID=ID_ВАШЕГО_ДИСКОРД_КАНАЛА

# --- Twitter User to Monitor ---
# Имя пользователя Twitter (без @), за которым нужно следить
TWITTER_USER_TO_MONITOR=имя_пользователя_твиттер

# --- Keywords to Monitor (Optional) ---
# Ключевые слова через запятую. Если пусто, будут поститься все твиты.
# Регистр не важен. Пример: KEYWORDS_TO_MONITOR=новость, обновление, релиз
KEYWORDS_TO_MONITOR=

# --- Bot Default Language (Optional) ---
# Язык по умолчанию (коды: de, en). По умолчанию 'de', если не указано.
BOT_DEFAULT_LANGUAGE=de
EOF

echo "Настройка виртуального окружения и установка зависимостей..."

# Переходим в директорию проекта
cd project || exit

# Создаем виртуальное окружение
if ! python3 -m venv venv; then
    echo "Ошибка: Не удалось создать виртуальное окружение 'venv'. Убедитесь, что python3 и модуль venv установлены."
    exit 1
fi

# Активируем и устанавливаем зависимости (показываем команды пользователю)
echo ""
echo "--------------------------------------------------"
echo "Структура проекта создана в папке 'project'."
echo "Виртуальное окружение 'venv' создано."
echo ""
echo "Чтобы продолжить:"
echo "1. Переименуйте '.env.example' в '.env' и заполните его вашими токенами и ID:"
echo "   mv .env.example .env"
echo "   nano .env  # или используйте ваш любимый редактор"
echo ""
echo "2. Активируйте виртуальное окружение:"
echo "   Для Linux/macOS: source venv/bin/activate"
echo "   Для Windows PowerShell: .\\venv\\Scripts\\activate"
echo "   Для Windows cmd.exe: venv\\Scripts\\activate.bat"
echo ""
echo "3. Установите зависимости (после активации окружения):"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Запустите бота (после активации окружения):"
echo "   python -m bot.main"
echo "--------------------------------------------------"

# Закомментировано, чтобы пользователь сам активировал и установил
# echo "Активация venv и установка зависимостей..."
#source venv/Scripts/activate && pip install -r requirements.txt

# if [ $? -ne 0 ]; then
#    echo "Ошибка: Не удалось установить зависимости из requirements.txt."
#    exit 1
# fi

echo "Настройка завершена."