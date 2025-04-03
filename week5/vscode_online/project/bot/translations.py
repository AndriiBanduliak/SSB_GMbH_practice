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
        "HELP_CMD_TWITTER_NAME": "",
        "HELP_CMD_TWITTER_VALUE": "Zeigt die letzten Tweets eines Benutzers an (Standard: 5, Max: 25).",
        "HELP_CMD_HELPME_NAME": "",
        "HELP_CMD_HELPME_VALUE": "Zeigt diese Hilfenachricht an.",
        "HELP_CMD_SETLANG_NAME": "",
        "HELP_CMD_SETLANG_VALUE": "Legt die Sprache des Bots für diesen Server fest (z.B. , ). Erfordert Administratorrechte.",
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
        "HELP_CMD_TWITTER_NAME": "",
        "HELP_CMD_TWITTER_VALUE": "Shows the latest tweets from a user (Default: 5, Max: 25).",
        "HELP_CMD_HELPME_NAME": "",
        "HELP_CMD_HELPME_VALUE": "Shows this help message.",
        "HELP_CMD_SETLANG_NAME": "",
        "HELP_CMD_SETLANG_VALUE": "Sets the bot's language for this server (e.g., , ). Requires Administrator permissions.",
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
