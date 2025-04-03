import logging
from .config import CONFIG

log = logging.getLogger('discord_twitter_bot.translations')

# Используем язык по умолчанию глобально
DEFAULT_LANGUAGE = CONFIG['DEFAULT_LANGUAGE']

# --- Структура переводов ---
translations = {
    "en": {
        # --- Логи и статусы задачи ---
        "TASK_WAITING_BOT": "Background Task: Waiting for bot to be ready...",
        "TASK_BOT_READY": "Background Task: Bot is ready.",
        "TASK_TWITTER_INIT_FAILED": "Background Task: Twitter client not initialized, task will not run.",
        "TASK_STARTING_SEARCH": "Background Task: Starting search for hashtags: {hashtags}",
        "TASK_SEARCH_QUERY": "Background Task: Using Twitter query: {query}",
        "TASK_SEARCH_API_ERROR": "Background Task: Twitter API search error: {error}",
        "TASK_SEARCH_UNEXPECTED_ERROR": "Background Task: Unexpected error during Twitter search: {error}",
        "TASK_NO_TWEETS_FOUND": "Background Task: No recent tweets found for the target hashtags.",
        "TASK_PROCESSING_TWEETS": "Background Task: Processing {tweet_count} found tweets...",
        "TASK_FOUND_BEST_HASHTAG": "Background Task: Found best hashtag '{hashtag}' from tweet by @{username} ({followers} followers).",
        "TASK_NO_SUITABLE_TWEET": "Background Task: No suitable tweet found (missing follower data or target hashtag in text).",
        "TASK_SENDING_HASHTAG": "Background Task: Sending hashtag '{hashtag}' to channel {channel_id}.",
        "TASK_SEND_SUCCESS": "Background Task: Hashtag '{hashtag}' successfully sent.",
        "TASK_SEND_FORBIDDEN": "Background Task: Failed to send hashtag to channel {channel_id} - Forbidden (Check permissions).",
        "TASK_SEND_ERROR": "Background Task: Failed to send hashtag to channel {channel_id} - Error: {error}",
        "TASK_TARGET_CHANNEL_ERROR": "Background Task: Target channel {channel_id} not found or inaccessible. Task cannot run.",
        "TASK_UNHANDLED_ERROR": "Unhandled error in background task check_twitter: {error}",

        # --- Сообщения бота (если нужны) ---
        # "POPULAR_HASHTAG_MESSAGE": "🔥 Today's popular hashtag: {hashtag}", # Пример сообщения для канала

        # --- Общие ошибки и статусы ---
        "BOT_STARTING": "Attempting to start the bot...",
        "BOT_START_SUCCESS": "Starting Discord bot...",
        "BOT_READY": "Bot {bot_name} (ID: {bot_id}) is connected and ready!",
        # Если будут разные языки
        "BOT_AVAILABLE_LANGS": "Available languages: {langs}",
        "CRITICAL_TWITTER_INIT_FAIL": "Critical Error: Failed to initialize Twitter client. Check TWITTER_BEARER_TOKEN and API access.",
        "CRITICAL_LOGIN_FAIL": "Critical Error: Invalid Discord Token (LoginFailure). Check DISCORD_BOT_TOKEN.",
        "CRITICAL_GENERIC_FAIL": "Critical error during bot startup:"
    },
    "de": {  # Пример немецкого перевода
        "TASK_WAITING_BOT": "Hintergrundaufgabe: Warte auf Bot-Bereitschaft...",
        "TASK_BOT_READY": "Hintergrundaufgabe: Bot ist bereit.",
        "TASK_TWITTER_INIT_FAILED": "Hintergrundaufgabe: Twitter-Client nicht initialisiert, Aufgabe wird nicht ausgeführt.",
        "TASK_STARTING_SEARCH": "Hintergrundaufgabe: Starte Suche nach Hashtags: {hashtags}",
        "TASK_SEARCH_QUERY": "Hintergrundaufgabe: Verwende Twitter-Abfrage: {query}",
        "TASK_SEARCH_API_ERROR": "Hintergrundaufgabe: Twitter API Suchfehler: {error}",
        "TASK_SEARCH_UNEXPECTED_ERROR": "Hintergrundaufgabe: Unerwarteter Fehler bei Twitter-Suche: {error}",
        "TASK_NO_TWEETS_FOUND": "Hintergrundaufgabe: Keine kürzlichen Tweets für die Ziel-Hashtags gefunden.",
        "TASK_PROCESSING_TWEETS": "Hintergrundaufgabe: Verarbeite {tweet_count} gefundene Tweets...",
        "TASK_FOUND_BEST_HASHTAG": "Hintergrundaufgabe: Bester Hashtag '{hashtag}' gefunden, aus Tweet von @{username} ({followers} Follower).",
        "TASK_NO_SUITABLE_TWEET": "Hintergrundaufgabe: Kein passender Tweet gefunden (fehlende Follower-Daten oder Ziel-Hashtag im Text).",
        "TASK_SENDING_HASHTAG": "Hintergrundaufgabe: Sende Hashtag '{hashtag}' an Kanal {channel_id}.",
        "TASK_SEND_SUCCESS": "Hintergrundaufgabe: Hashtag '{hashtag}' erfolgreich gesendet.",
        "TASK_SEND_FORBIDDEN": "Hintergrundaufgabe: Senden des Hashtags an Kanal {channel_id} fehlgeschlagen - Verboten (Berechtigungen prüfen).",
        "TASK_SEND_ERROR": "Hintergrundaufgabe: Senden des Hashtags an Kanal {channel_id} fehlgeschlagen - Fehler: {error}",
        "TASK_TARGET_CHANNEL_ERROR": "Hintergrundaufgabe: Zielkanal {channel_id} nicht gefunden oder unzugänglich. Aufgabe kann nicht ausgeführt werden.",
        "TASK_UNHANDLED_ERROR": "Unbehandelter Fehler in Hintergrundaufgabe check_twitter: {error}",
        "BOT_STARTING": "Versuche, den Bot zu starten...",
        "BOT_START_SUCCESS": "Starte Discord-Bot...",
        "BOT_READY": "Bot {bot_name} (ID: {bot_id}) ist verbunden und bereit!",
        "BOT_AVAILABLE_LANGS": "Verfügbare Sprachen: {langs}",
        "CRITICAL_TWITTER_INIT_FAIL": "Kritischer Fehler: Twitter-Client konnte nicht initialisiert werden. Überprüfe TWITTER_BEARER_TOKEN und API-Zugang.",
        "CRITICAL_LOGIN_FAIL": "Kritischer Fehler: Ungültiger Discord-Token (LoginFailure). Überprüfe DISCORD_BOT_TOKEN.",
        "CRITICAL_GENERIC_FAIL": "Kritischer Fehler beim Bot-Start:"
    }
}

# --- Функция-переводчик ---
# Упрощена, т.к. SettingsManager удален, всегда использует DEFAULT_LANGUAGE


def get_translator():
    """Возвращает функцию перевода, использующую язык по умолчанию."""
    lang = DEFAULT_LANGUAGE

    def _(key, **kwargs):
        message = translations.get(lang, {}).get(key)
        # Если нет даже в языке по умолчанию (что странно), вернуть ключ
        if message is None:
            # Попробуем английский как fallback, если дефолтный язык другой
            if lang != 'en':
                message = translations.get('en', {}).get(key)
            if message is None:
                log.warning(
                    "Translation key '%s' not found for default language '%s' or fallback 'en'.", key, lang)
                return f"<{key}_TRANSLATION_MISSING>"

        try:
            return message.format(**kwargs)
        except KeyError as e:
            log.error(
                "Formatting error for key '%s' (lang '%s'): missing argument %s. Provided args: %s", key, lang, e, kwargs)
            return f"<{key}_FORMATTING_ERROR: Missing {e}>"
        except Exception as e:
            log.error(
                "Generic formatting error for key '%s' (lang '%s'): %s. Provided args: %s", key, lang, e, kwargs)
            return f"<{key}_UNEXPECTED_FORMATTING_ERROR>"
    return _


def get_available_languages():
    """Возвращает список кодов доступных языков."""
    return list(translations.keys())
