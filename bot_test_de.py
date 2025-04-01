import discord
from discord.ext import commands, tasks
import tweepy
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import sys
import traceback
import json  # <--- Добавлено для настроек языка

# --- ЗАГРУЗКА .ENV ---
load_dotenv()
logging.debug("Переменные окружения загружены.")

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
LOG_FILE = "bot.log"
LAST_TWEET_ID_FILE = "last_tweet.id"
# --- ИЗМЕНЕНИЕ: Файл для настроек серверов ---
SERVER_SETTINGS_FILE = "server_settings.json"

# ... (код логирования остается без изменений) ...

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger('discord_twitter_bot')
log.info("Логирование настроено.")


# --- КОНФИГУРАЦИЯ ИЗ .ENV ---
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
TARGET_CHANNEL_ID_STR = os.environ.get("TARGET_DISCORD_CHANNEL_ID")
TWITTER_USER_TO_MONITOR = os.environ.get("TWITTER_USER_TO_MONITOR")
KEYWORDS_STR = os.environ.get("KEYWORDS_TO_MONITOR", "")
DEFAULT_LANGUAGE = os.environ.get("BOT_DEFAULT_LANGUAGE", "de")

# --- Проверка обязательных переменных ---
errors = []  # Создаем пустой список для ошибок
if not TOKEN:
    errors.append("DISCORD_BOT_TOKEN")
if not TWITTER_BEARER_TOKEN:
    errors.append("TWITTER_BEARER_TOKEN")
if not TARGET_CHANNEL_ID_STR:
    errors.append("TARGET_DISCORD_CHANNEL_ID")
if not TWITTER_USER_TO_MONITOR:
    errors.append("TWITTER_USER_TO_MONITOR")

# --- Проверяем, есть ли ошибки в списке ---
if errors:  # Если список НЕ пустой (т.е. были найдены ошибки)
    # Логируем критическую ошибку со списком отсутствующих переменных
    log.critical(
        "Критические переменные окружения не установлены: %s", ", ".join(errors))
    # Завершаем работу бота с сообщением об ошибке
    sys.exit(
        f"Ошибка: Не установлены переменные окружения: {', '.join(errors)}. Проверьте ваш .env файл.")
# --- Если ошибок нет, код продолжается ---

# --- Преобразование типов и дальнейшая конфигурация ---
try:
    TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID_STR)
except ValueError:
    log.critical(
        "TARGET_DISCORD_CHANNEL_ID (%s) должен быть числом.", TARGET_CHANNEL_ID_STR)
    sys.exit(
        f"Критическая ошибка: TARGET_DISCORD_CHANNEL_ID ({TARGET_CHANNEL_ID_STR}) не является числом.")

KEYWORDS = [k.strip().lower() for k in KEYWORDS_STR.split(',') if k.strip()]
log.info("Конфигурация загружена. Канал: %d, Пользователь: %s, Ключевые слова: %s, Язык по умолчанию: %s",
         TARGET_CHANNEL_ID, TWITTER_USER_TO_MONITOR, KEYWORDS, DEFAULT_LANGUAGE)



# --- ИЗМЕНЕНИЕ: Структура переводов ---
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
        "NEW_TWEET_ALERT": "🚀 Neuer Tweet von @{username}:\n{text}\n\n🔗 {url}",
        "LANG_SET_SUCCESS": "✅ Sprache für diesen Server auf **{lang}** gesetzt.",
        "LANG_SET_FAIL_INVALID": "❌ Ungültiger Sprachcode. Verfügbare Sprachen: {available_langs}",
        "LANG_SET_FAIL_PERMISSIONS": "❌ Du benötigst Administratorrechte, um die Sprache zu ändern.",
        "LANG_INFO": "ℹ️ Die aktuelle Sprache für diesen Server ist **{lang}**.",
        "ERROR_FORBIDDEN_SEND": "Keine Rechte zum Senden von Nachrichten in Kanal #{channel_name} ({channel_id}) auf Server {server_name}. Rollen prüfen.",
        "WARN_NO_EMBED": "Keine Rechte zum Einbetten von Links in Kanal #{channel_name} ({channel_id}). Links werden möglicherweise nicht korrekt angezeigt.",
        "ERROR_TARGET_CHANNEL_NOT_FOUND": "Zielkanal Discord mit ID {channel_id} nicht gefunden! Überprüfe TARGET_DISCORD_CHANNEL_ID.",
        "ERROR_NO_GUILD_FOR_CHANNEL": "Konnte den Server für Kanal {channel_id} nicht bestimmen. Senden übersprungen.",

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
        "NEW_TWEET_ALERT": "🚀 New tweet from @{username}:\n{text}\n\n🔗 {url}",
        "LANG_SET_SUCCESS": "✅ Language for this server set to **{lang}**.",
        "LANG_SET_FAIL_INVALID": "❌ Invalid language code. Available languages: {available_langs}",
        "LANG_SET_FAIL_PERMISSIONS": "❌ You need Administrator permissions to change the language.",
        "LANG_INFO": "ℹ️ The current language for this server is **{lang}**.",
        "ERROR_FORBIDDEN_SEND": "No permission to send messages in channel #{channel_name} ({channel_id}) on server {server_name}. Check roles.",
        "WARN_NO_EMBED": "No permission to embed links in channel #{channel_name} ({channel_id}). Links might not display correctly.",
        "ERROR_TARGET_CHANNEL_NOT_FOUND": "Target Discord channel with ID {channel_id} not found! Check TARGET_DISCORD_CHANNEL_ID.",
        "ERROR_NO_GUILD_FOR_CHANNEL": "Could not determine the server for channel {channel_id}. Skipping send.",
    }
    # Добавь сюда русский, если нужно
}

# --- ИЗМЕНЕНИЕ: Функции для работы с настройками языка сервера ---
server_settings = {}


def load_server_settings():
    global server_settings
    if os.path.exists(SERVER_SETTINGS_FILE):
        try:
            with open(SERVER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                server_settings = json.load(f)
            log.info("Настройки серверов загружены из %s",
                     SERVER_SETTINGS_FILE)
        except json.JSONDecodeError:
            log.error(
                "Ошибка декодирования JSON из файла настроек %s. Файл может быть поврежден.", SERVER_SETTINGS_FILE)
            server_settings = {}
        except Exception as e:
            log.exception(
                "Не удалось загрузить настройки серверов из %s.", SERVER_SETTINGS_FILE)
            server_settings = {}
    else:
        log.info("Файл настроек %s не найден, будут использоваться настройки по умолчанию.",
                 SERVER_SETTINGS_FILE)
        server_settings = {}


def save_server_settings():
    global server_settings
    try:
        with open(SERVER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(server_settings, f, indent=4)
        log.debug("Настройки серверов сохранены в %s", SERVER_SETTINGS_FILE)
    except Exception as e:
        log.exception(
            "Не удалось сохранить настройки серверов в %s.", SERVER_SETTINGS_FILE)


def get_server_language(guild_id):
    if guild_id:
        return server_settings.get(str(guild_id), {}).get("language", DEFAULT_LANGUAGE)
    return DEFAULT_LANGUAGE


def set_server_language(guild_id, lang_code):
    if lang_code not in translations:
        return False  # Недопустимый язык
    guild_id_str = str(guild_id)
    if guild_id_str not in server_settings:
        server_settings[guild_id_str] = {}
    server_settings[guild_id_str]["language"] = lang_code
    save_server_settings()
    return True

# --- ИЗМЕНЕНИЕ: Функция-переводчик ---
# Используем _ как общепринятое имя для функции gettext/перевода


def _(key, guild_id=None, **kwargs):
    lang = get_server_language(guild_id)
    # Попытаться получить строку для нужного языка
    message = translations.get(lang, {}).get(key)
    # Если нет, попытаться получить для языка по умолчанию
    if message is None and lang != DEFAULT_LANGUAGE:
        message = translations.get(DEFAULT_LANGUAGE, {}).get(key)
    # Если все еще нет, вернуть сам ключ или строку ошибки
    if message is None:
        log.warning("Ключ перевода '%s' не найден для языка '%s' или языка по умолчанию '%s'.",
                    key, lang, DEFAULT_LANGUAGE)
        return f"<{key}_TRANSLATION_MISSING>"

    # Форматировать строку, если переданы аргументы
    try:
        return message.format(**kwargs)
    except KeyError as e:
        log.error("Ошибка форматирования для ключа '%s' (язык '%s'): отсутствует аргумент %s. Переданные аргументы: %s", key, lang, e, kwargs)
        return f"<{key}_FORMATTING_ERROR: Missing {e}>"


# Загружаем настройки серверов при старте
load_server_settings()

# --- TWITTER CLIENT & DISCORD BOT ---
# ... (инициализация twitter_client и bot остается прежней) ...
twitter_client = None
twitter_init_failed = False
try:
    twitter_client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)
    # ... (остальная инициализация twitter)
except Exception as e:
    twitter_init_failed = True
    # ...

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ И ПЕРСИСТЕНТНОСТЬ ID ---
# ... (код для last_seen_tweet_id, load/save функций остается прежним) ...
target_user_id = None
last_seen_tweet_id = None
def load_last_tweet_id(): ...
def save_last_tweet_id(): ...


load_last_tweet_id()

# --- ФУНКЦИИ TWITTER API V2 ---
# ... (get_user_id_v2, get_tweets_v2 остаются без изменений) ...


async def get_user_id_v2(username): ...
async def get_tweets_v2(user_id, count=5, since_id=None): ...


# --- ФОНОВАЯ ЗАДАЧА: ПРОВЕРКА TWITTER ---
@tasks.loop(minutes=15)
async def check_twitter():
    global last_seen_tweet_id, target_user_id
    if not twitter_client or not target_user_id:  # Упрощенная проверка
        # Логирование причин пропуска происходит в before_loop или при попытке получить ID
        return

    log.info("Проверка новых твитов для @%s (ID: %s), since_id: %s",
             TWITTER_USER_TO_MONITOR, target_user_id, last_seen_tweet_id)
    tweets = await get_tweets_v2(target_user_id, count=20, since_id=last_seen_tweet_id)
    if not tweets:
        return
    log.info("Найдено %d новых твитов от @%s.",
             len(tweets), TWITTER_USER_TO_MONITOR)
    tweets.reverse()

    newest_processed_id = last_seen_tweet_id
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        # Используем переводчик для логирования ошибки, хотя язык здесь не так важен
        log.error(_("ERROR_TARGET_CHANNEL_NOT_FOUND",
                  channel_id=TARGET_CHANNEL_ID))
        return

    # --- ИЗМЕНЕНИЕ: Получаем guild_id для перевода ---
    guild = channel.guild
    current_guild_id = guild.id if guild else None
    if not guild:
        log.warning(_("ERROR_NO_GUILD_FOR_CHANNEL",
                    guild_id=current_guild_id, channel_id=TARGET_CHANNEL_ID))
        return  # Не можем проверить права или перевести без сервера

    me = guild.me
    permissions = channel.permissions_for(me)
    if not permissions.send_messages:
        log.error(_("ERROR_FORBIDDEN_SEND", guild_id=current_guild_id,
                  channel_name=channel.name, channel_id=channel.id, server_name=guild.name))
        return
    if not permissions.embed_links:
        log.warning(_("WARN_NO_EMBED", guild_id=current_guild_id,
                    channel_name=channel.name, channel_id=channel.id))

    for tweet in tweets:
        current_tweet_id = tweet.id
        tweet_text_lower = tweet.text.lower()
        if not KEYWORDS or any(keyword in tweet_text_lower for keyword in KEYWORDS):
            tweet_url = f"https://twitter.com/{TWITTER_USER_TO_MONITOR}/status/{tweet.id}"
            # --- ИЗМЕНЕНИЕ: Используем переводчик для сообщения ---
            message = _("NEW_TWEET_ALERT", current_guild_id,
                        username=TWITTER_USER_TO_MONITOR, text=tweet.text, url=tweet_url)
            try:
                await channel.send(message)
                log.info("Твит (ID: %s) отправлен в канал %d",
                         tweet.id, channel.id)
                newest_processed_id = current_tweet_id
            except discord.errors.Forbidden:
                log.error("Forbidden (после проверки прав?): %s", _("ERROR_FORBIDDEN_SEND", current_guild_id,
                          channel_name=channel.name, channel_id=channel.id, server_name=guild.name))
                break
            except Exception:  # Ловим другие ошибки отправки
                log.exception(
                    "Не удалось отправить сообщение с твитом ID %s в канал %d.", tweet.id, channel.id)
        else:
            log.debug(
                "Твит (ID: %s) пропущен (не содержит ключевых слов)", tweet.id)
            newest_processed_id = current_tweet_id

    if newest_processed_id != last_seen_tweet_id:
        log.info("Обновление last_seen_tweet_id с %s на %s",
                 last_seen_tweet_id, newest_processed_id)
        last_seen_tweet_id = newest_processed_id
        save_last_tweet_id()


@check_twitter.error
async def on_check_twitter_error(error):
    log.exception(
        "Необработанная ошибка в фоновой задаче check_twitter: %s", error)


@check_twitter.before_loop
async def before_check_twitter():
    # ... (логика ожидания и получения target_user_id остается) ...
    log.info("Ожидание готовности бота...")
    await bot.wait_until_ready()
    log.info("Бот готов.")
    if not target_user_id and twitter_client:
        log.info("Получение ID пользователя Twitter для мониторинга...")
        global target_user_id
        target_user_id = await get_user_id_v2(TWITTER_USER_TO_MONITOR)
        # ... (логирование результата получения ID) ...


@bot.event
async def on_ready():
    # ... (логика on_ready остается, возможно добавить логирование загруженных языков) ...
    log.info("Бот %s (ID: %s) подключен и готов!", bot.user.name, bot.user.id)
    log.info("Доступные языки: %s", ", ".join(translations.keys()))
    if twitter_client:
        log.info("Запуск фоновой задачи проверки Twitter...")
        check_twitter.start()
    # ...

# --- DISCORD КОМАНДЫ ---

# --- ИЗМЕНЕНИЕ: Новая команда для установки языка ---


@bot.command(name="setlang", help="Legt die Sprache des Bots für diesen Server fest.")
# Только админы могут менять язык
@commands.has_permissions(administrator=True)
@commands.guild_only()  # Команда доступна только на сервере
async def setlang_command(ctx, lang_code: str):
    lang_code = lang_code.lower()
    available_langs = ", ".join(f"`{code}`" for code in translations.keys())
    if set_server_language(ctx.guild.id, lang_code):
        await ctx.send(_("LANG_SET_SUCCESS", ctx.guild.id, lang=lang_code))
        log.info("Язык для сервера %d (%s) изменен на '%s' пользователем %s (%d)",
                 ctx.guild.id, ctx.guild.name, lang_code, ctx.author.name, ctx.author.id)
    else:
        await ctx.send(_("LANG_SET_FAIL_INVALID", ctx.guild.id, available_langs=available_langs))


@setlang_command.error
async def setlang_command_error(ctx, error):
    # Обработка ошибки отсутствия прав
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(_("LANG_SET_FAIL_PERMISSIONS", ctx.guild.id))
    elif isinstance(error, commands.NoPrivateMessage):
        # Эта ошибка не должна возникать из-за @commands.guild_only(), но на всякий случай
        # Простой ответ, т.к. нет guild_id
        await ctx.send("Dieser Befehl kann nur auf einem Server verwendet werden.")
    else:
        log.error("Неожиданная ошибка в команде setlang: %s", error)
        await ctx.send("Ein unerwarteter Fehler ist aufgetreten.")


@bot.command(name="twitter", help="Zeigt die letzten Tweets eines Benutzers an.")
async def twitter_command(ctx, username: str, count: int = 5):
    # --- ИЗМЕНЕНИЕ: Используем переводчик ---
    guild_id = ctx.guild.id if ctx.guild else None
    if not twitter_client:
        await ctx.send(_("TWITTER_INACTIVE", guild_id))
        return

    count = max(1, min(25, count))
    await ctx.send(_("SEARCHING_TWEETS", guild_id, count=count, username=username))

    user_id = await get_user_id_v2(username)
    if not user_id:
        await ctx.send(_("USER_NOT_FOUND", guild_id, username=username))
        return

    tweets = await get_tweets_v2(user_id, count=count)

    if tweets:
        await ctx.send(_("LAST_TWEETS_HEADER", guild_id, num_tweets=len(tweets), username=username))
        for tweet in tweets:
            tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
            embed = discord.Embed(description=tweet.text,
                                  color=discord.Color.blue())
            embed.set_author(
                name=f"@{username}", url=tweet_url, icon_url=ctx.author.display_avatar.url)
            embed.add_field(name=_("TWEET_LINK_TEXT", guild_id), value=_(
                "TWEET_GOTO_LINK", guild_id, url=tweet_url), inline=False)
            if tweet.created_at:
                embed.timestamp = tweet.created_at
            await ctx.send(embed=embed)
    else:
        await ctx.send(_("NO_TWEETS_FOUND", guild_id, username=username))


@bot.command(name="helpme", help="Zeigt diese Hilfenachricht an.")
async def helpme_command(ctx):
    # --- ИЗМЕНЕНИЕ: Используем переводчик ---
    guild_id = ctx.guild.id if ctx.guild else None
    embed = discord.Embed(title=_("HELP_TITLE", guild_id),
                          color=discord.Color.green())

    # Добавляем команды в помощь
    embed.add_field(name=_("HELP_CMD_TWITTER_NAME", guild_id), value=_(
        "HELP_CMD_TWITTER_VALUE", guild_id), inline=False)
    embed.add_field(name=_("HELP_CMD_SETLANG_NAME", guild_id), value=_(
        "HELP_CMD_SETLANG_VALUE", guild_id), inline=False)
    embed.add_field(name=_("HELP_CMD_HELPME_NAME", guild_id), value=_(
        "HELP_CMD_HELPME_VALUE", guild_id), inline=False)  # Сама команда helpme

    # Получаем текущий язык сервера для информации
    current_lang = get_server_language(guild_id)
    embed.add_field(name="---", value=_("LANG_INFO", guild_id,
                    lang=current_lang), inline=False)

    # Footer
    footer_text = ""
    if ctx.guild:
        footer_text = _("HELP_FOOTER_SERVER", guild_id,
                        server_name=ctx.guild.name)
    else:
        footer_text = _("HELP_FOOTER_DM", guild_id)
    footer_text += f" | Bot ID: {bot.user.id}"
    embed.set_footer(text=footer_text)

    await ctx.send(embed=embed)


# --- ЗАПУСК БОТА ---
if __name__ == "__main__":
    log.info("Попытка запуска бота...")
    if twitter_init_failed:
        log.critical(...)
        sys.exit(...)
    if not TOKEN:
        log.critical(...)
        sys.exit(...)

    try:
        log.info("Запуск бота Discord...")
        bot.run(TOKEN, log_handler=None)
    except discord.errors.LoginFailure:
        log.critical(...)
        sys.exit(...)
    except Exception as e:
        log.critical(...)
        traceback.print_exc()
        sys.exit(...)
