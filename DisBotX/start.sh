#!/bin/bash

# Создаем корневую директорию проекта
PROJECT_DIR="project"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir "$PROJECT_DIR"
fi

# Создаем директорию для бота
BOT_DIR="$PROJECT_DIR/bot"
mkdir -p "$BOT_DIR"

# 1. Файл __init__.py (пустой, чтобы пометить папку как пакет)
cat << 'EOF' > "$BOT_DIR/__init__.py"
# Этот файл оставлен пустым, чтобы указать, что эта директория является пакетом.
EOF

# 2. Файл config.py
cat << 'EOF' > "$BOT_DIR/config.py"
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
EOF

# 3. Файл twitter_client.py
cat << 'EOF' > "$BOT_DIR/twitter_client.py"
import tweepy
import logging
from bot.config import TWITTER_BEARER_TOKEN

log = logging.getLogger('twitter_client')

# Инициализация клиента Twitter
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)

async def get_user_id(username: str):
    try:
        response = client.get_user(username=username)
        if response.data:
            return response.data.id
    except Exception as e:
        log.exception("Ошибка получения user id для %s", username)
    return None

async def get_tweets(user_id, count=5, since_id=None):
    try:
        response = client.get_users_tweets(id=user_id, max_results=count, since_id=since_id)
        return response.data
    except Exception as e:
        log.exception("Ошибка получения твитов для user_id %s", user_id)
    return None
EOF

# 4. Файл settings.py
cat << 'EOF' > "$BOT_DIR/settings.py"
import os
import json
import logging

log = logging.getLogger('settings')
SETTINGS_FILE = "server_settings.json"
server_settings = {}

def load_settings():
    global server_settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                server_settings = json.load(f)
        except Exception as e:
            log.exception("Ошибка загрузки настроек")
            server_settings = {}
    else:
        server_settings = {}

def save_settings():
    global server_settings
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(server_settings, f, indent=4)
    except Exception as e:
        log.exception("Ошибка сохранения настроек")

def get_server_language(guild_id, default_language):
    return server_settings.get(str(guild_id), {}).get("language", default_language)

def set_server_language(guild_id, lang_code):
    guild_id_str = str(guild_id)
    if guild_id_str not in server_settings:
        server_settings[guild_id_str] = {}
    server_settings[guild_id_str]["language"] = lang_code
    save_settings()
    return True
EOF

# 5. Файл translations.py
cat << 'EOF' > "$BOT_DIR/translations.py"
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
EOF

# 6. Файл commands.py
cat << 'EOF' > "$BOT_DIR/commands.py"
import discord
from discord.ext import commands
from bot.translations import translate
from bot.settings import set_server_language, get_server_language
from bot.twitter_client import get_user_id, get_tweets

bot = commands.Bot(command_prefix="!")

@bot.command(name="setlang", help="Legt die Sprache des Bots für diesen Server fest.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def setlang_command(ctx, lang_code: str):
    lang_code = lang_code.lower()
    available_langs = ", ".join(["de", "en"])
    if set_server_language(ctx.guild.id, lang_code):
        await ctx.send(translate("LANG_SET_SUCCESS", ctx.guild.id, lang=lang_code))
    else:
        await ctx.send(translate("LANG_SET_FAIL_INVALID", ctx.guild.id, available_langs=available_langs))

@bot.command(name="twitter", help="Zeigt die letzten Tweets eines Benutzers an.")
async def twitter_command(ctx, username: str, count: int = 5):
    guild_id = ctx.guild.id if ctx.guild else None
    await ctx.send(translate("SEARCHING_TWEETS", guild_id, count=count, username=username))
    user_id = await get_user_id(username)
    if not user_id:
        await ctx.send(translate("USER_NOT_FOUND", guild_id, username=username))
        return
    tweets = await get_tweets(user_id, count=count)
    if tweets:
        await ctx.send(translate("LAST_TWEETS_HEADER", guild_id, num_tweets=len(tweets), username=username))
        for tweet in tweets:
            tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
            embed = discord.Embed(description=tweet.text, color=discord.Color.blue())
            embed.set_author(name=f"@{username}", url=tweet_url, icon_url=ctx.author.display_avatar.url)
            embed.add_field(name=translate("TWEET_LINK_TEXT", guild_id), value=translate("TWEET_GOTO_LINK", guild_id, url=tweet_url), inline=False)
            if tweet.created_at:
                embed.timestamp = tweet.created_at
            await ctx.send(embed=embed)
    else:
        await ctx.send(translate("NO_TWEETS_FOUND", guild_id, username=username))

@bot.command(name="helpme", help="Zeigt diese Hilfenachricht an.")
async def helpme_command(ctx):
    guild_id = ctx.guild.id if ctx.guild else None
    embed = discord.Embed(title=translate("HELP_TITLE", guild_id), color=discord.Color.green())
    embed.add_field(name=translate("HELP_CMD_TWITTER_NAME", guild_id), value=translate("HELP_CMD_TWITTER_VALUE", guild_id), inline=False)
    embed.add_field(name=translate("HELP_CMD_SETLANG_NAME", guild_id), value=translate("HELP_CMD_SETLANG_VALUE", guild_id), inline=False)
    embed.add_field(name=translate("HELP_CMD_HELPME_NAME", guild_id), value=translate("HELP_CMD_HELPME_VALUE", guild_id), inline=False)
    current_lang = get_server_language(guild_id, "de")
    embed.add_field(name="---", value=translate("LANG_INFO", guild_id, lang=current_lang), inline=False)
    footer_text = translate("HELP_FOOTER_SERVER", guild_id, server_name=ctx.guild.name) if ctx.guild else translate("HELP_FOOTER_DM", guild_id)
    footer_text += f" | Bot ID: {bot.user.id}"
    embed.set_footer(text=footer_text)
    await ctx.send(embed=embed)
EOF

# 7. Файл tasks.py
cat << 'EOF' > "$BOT_DIR/tasks.py"
from discord.ext import tasks
import logging
from bot.twitter_client import get_tweets, get_user_id
from bot.config import TWITTER_USER_TO_MONITOR, TARGET_CHANNEL_ID
from bot.translations import translate

log = logging.getLogger('tasks')

last_seen_tweet_id = None
target_user_id = None

@tasks.loop(minutes=15)
async def check_twitter():
    global last_seen_tweet_id, target_user_id
    # Здесь должна быть логика проверки новых твитов
    pass

@check_twitter.before_loop
async def before_check_twitter():
    # Ожидание готовности бота, получение target_user_id и т.д.
    pass
EOF

# 8. Файл main.py
cat << 'EOF' > "$BOT_DIR/main.py"
import logging
from bot.config import DISCORD_BOT_TOKEN
from bot.settings import load_settings
from bot.commands import bot
from bot.tasks import check_twitter

logging.basicConfig(level=logging.INFO)

def main():
    load_settings()
    
    @bot.event
    async def on_ready():
        logging.info("Бот %s (ID: %s) готов!", bot.user.name, bot.user.id)
        check_twitter.start()
    
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()
EOF

# 9. Файл .env (пример заполнения, замените значения на реальные)
cat << 'EOF' > "$PROJECT_DIR/.env"
DISCORD_BOT_TOKEN=your_discord_bot_token
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TARGET_DISCORD_CHANNEL_ID=your_target_channel_id
TWITTER_USER_TO_MONITOR=twitter_username
KEYWORDS_TO_MONITOR=keyword1,keyword2
BOT_DEFAULT_LANGUAGE=en
EOF

# 10. Файл requirements.txt
cat << 'EOF' > "$PROJECT_DIR/requirements.txt"
discord.py
tweepy
python-dotenv
EOF

# 11. Скрипт setup.sh для создания виртуального окружения
cat << 'EOF' > "$PROJECT_DIR/setup.sh"
#!/bin/bash

if ! command -v python3 &>/dev/null; then
    echo "Python3 не установлен. Установите Python3 и повторите попытку."
    exit 1
fi

python3 -m venv venv
source venv/Scripts/activate
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Файл requirements.txt не найден!"
    exit 1
fi

echo "Виртуальное окружение успешно настроено и зависимости установлены."
EOF

# Делаем setup.sh исполняемым
chmod +x "$PROJECT_DIR/setup.sh"

echo "Проект успешно создан в каталоге '$PROJECT_DIR'."
