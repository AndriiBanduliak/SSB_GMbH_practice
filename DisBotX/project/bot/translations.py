# Словари переводов
translations = {
    "de": {
        "TWITTER_INACTIVE": "❌ Fehler: Das Twitter-Modul ist derzeit nicht aktiv.",
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
        "LANG_SET_SUCCESS": "✅ Sprache für diesen Server auf **{lang}** gesetzt.",
        "LANG_SET_FAIL_INVALID": "❌ Ungültiger Sprachcode. Verfügbare Sprachen: {available_langs}",
        "LANG_SET_FAIL_PERMISSIONS": "❌ Du benötigst Administratorrechte, um die Sprache zu ändern.",
        "LANG_INFO": "ℹ️ Die aktuelle Sprache für diesen Server ist **{lang}**.",
    },
    "en": {
        "TWITTER_INACTIVE": "❌ Error: The Twitter module is currently inactive.",
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
        "LANG_SET_SUCCESS": "✅ Language for this server set to **{lang}**.",
        "LANG_SET_FAIL_INVALID": "❌ Invalid language code. Available languages: {available_langs}",
        "LANG_SET_FAIL_PERMISSIONS": "❌ You need Administrator permissions to change the language.",
        "LANG_INFO": "ℹ️ The current language for this server is **{lang}**.",
    }
}
DEFAULT_LANGUAGE = "de"

def translate(key, guild_id=None, lang=None, **kwargs):
    language = lang or DEFAULT_LANGUAGE
    message = translations.get(language, {}).get(key)
    if message is None:
        message = translations.get(DEFAULT_LANGUAGE, {}).get(key, f"<{key}_MISSING>")
    try:
        return message.format(**kwargs)
    except Exception as e:
        return f"<{key}_FORMAT_ERROR>"
