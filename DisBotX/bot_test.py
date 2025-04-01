import discord
from discord.ext import commands, tasks
import tweepy
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import sys
import traceback # Для вывода трассировки в обработчике ошибок задачи

# --- ЗАГРУЗКА .ENV ---
load_dotenv()
# ИЗМЕНЕНИЕ 3: Замена print на logging.debug
logging.debug("Переменные окружения загружены.")

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
LOG_FILE = "bot.log"
LAST_TWEET_ID_FILE = "last_tweet.id" # ИЗМЕНЕНИЕ 2: Имя файла для ID

# Переименование старого лог-файла
if os.path.exists(LOG_FILE):
    if os.access(LOG_FILE, os.W_OK) and os.access(".", os.W_OK):
        try:
            new_log_name = LOG_FILE + ".old." + datetime.now().strftime("%Y%m%d%H%M%S")
            os.rename(LOG_FILE, new_log_name)
            # ИЗМЕНЕНИЕ 3: Замена print на logging.info (т.к. это важное событие при запуске)
            logging.info(f"Старый лог файл переименован в {new_log_name}")
        except OSError as e:
            # ИЗМЕНЕНИЕ 3: Замена print на logging.warning
            logging.warning(f"Не удалось переименовать лог файл {LOG_FILE}: {e}")
    else:
        # ИЗМЕНЕНИЕ 3: Замена print на logging.warning
        logging.warning(f"Нет прав на переименование {LOG_FILE} или запись в текущую директорию.")

logging.basicConfig(
    level=logging.INFO, # Установите DEBUG, если хотите видеть debug-сообщения
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", # Добавил %(name)s для ясности
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
# Получаем логгер для нашего бота, чтобы различать сообщения от библиотек
log = logging.getLogger('discord_twitter_bot')
log.info("Логирование настроено.")

# --- КОНФИГУРАЦИЯ ИЗ .ENV ---
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
TARGET_CHANNEL_ID_STR = os.environ.get("TARGET_DISCORD_CHANNEL_ID")
TWITTER_USER_TO_MONITOR = os.environ.get("TWITTER_USER_TO_MONITOR")
KEYWORDS_STR = os.environ.get("KEYWORDS_TO_MONITOR", "")

# Проверка обязательных переменных
errors = []
if not TOKEN: errors.append("DISCORD_BOT_TOKEN")
if not TWITTER_BEARER_TOKEN: errors.append("TWITTER_BEARER_TOKEN")
if not TARGET_CHANNEL_ID_STR: errors.append("TARGET_DISCORD_CHANNEL_ID")
if not TWITTER_USER_TO_MONITOR: errors.append("TWITTER_USER_TO_MONITOR")

if errors:
    log.critical("Критические переменные окружения не установлены: %s", ", ".join(errors))
    sys.exit(f"Критическая ошибка: Не установлены переменные окружения: {', '.join(errors)}. Проверьте .env файл и перезапустите.")

try:
    TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID_STR)
except ValueError:
    log.critical("TARGET_DISCORD_CHANNEL_ID (%s) должен быть числом.", TARGET_CHANNEL_ID_STR)
    sys.exit(f"Критическая ошибка: TARGET_DISCORD_CHANNEL_ID ({TARGET_CHANNEL_ID_STR}) не является числом.")

KEYWORDS = [k.strip().lower() for k in KEYWORDS_STR.split(',') if k.strip()]
log.info("Конфигурация загружена. Канал: %d, Пользователь: %s, Ключевые слова: %s",
             TARGET_CHANNEL_ID, TWITTER_USER_TO_MONITOR, KEYWORDS)

# --- TWITTER (X) API V2 CLIENT ---
twitter_client = None # Инициализируем как None
twitter_init_failed = False # Флаг для проверки в блоке запуска
try:
    twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True) # wait_on_rate_limit полезен
    log.info("Клиент Twitter API v2 создан.")
    me_user = twitter_client.get_me()
    if me_user.data:
        log.info("Аутентификация Twitter Bearer Token успешна (ID приложения: %s)", me_user.data.id)
    else:
        # Это не критическая ошибка, просто предупреждение
        log.warning("Не удалось проверить аутентификацию Twitter Bearer Token (get_me не вернул данные).")
except tweepy.errors.TweepyException as e:
    log.error("Критическая ошибка инициализации клиента Twitter API v2: %s", e)
    twitter_init_failed = True # ИЗМЕНЕНИЕ 1: Устанавливаем флаг ошибки
except Exception as e:
    log.exception("Неожиданная критическая ошибка при инициализации клиента Twitter.") # Используем exception для трассировки
    twitter_init_failed = True # ИЗМЕНЕНИЕ 1: Устанавливаем флаг ошибки

# --- DISCORD BOT EINSTELLUNGEN ---
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
log.info("Discord Intents настроены.")

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ И ПЕРСИСТЕНТНОСТЬ ---
target_user_id = None
last_seen_tweet_id = None

# ИЗМЕНЕНИЕ 2: Функция загрузки ID из файла
def load_last_tweet_id():
    global last_seen_tweet_id
    try:
        if os.path.exists(LAST_TWEET_ID_FILE):
            with open(LAST_TWEET_ID_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    last_seen_tweet_id = int(content)
                    log.info("Загружен last_seen_tweet_id: %s из файла %s", last_seen_tweet_id, LAST_TWEET_ID_FILE)
                else:
                    log.warning("Файл %s пуст, last_seen_tweet_id не загружен.", LAST_TWEET_ID_FILE)

        else:
            log.info("Файл %s не найден, last_seen_tweet_id не загружен.", LAST_TWEET_ID_FILE)
    except ValueError:
        log.error("Ошибка преобразования ID из файла %s. Файл может быть поврежден.", LAST_TWEET_ID_FILE)
    except Exception as e:
        log.exception("Ошибка при загрузке last_seen_tweet_id из файла %s.", LAST_TWEET_ID_FILE)

# ИЗМЕНЕНИЕ 2: Функция сохранения ID в файл
def save_last_tweet_id():
    global last_seen_tweet_id
    if last_seen_tweet_id is None:
        return # Нечего сохранять
    try:
        with open(LAST_TWEET_ID_FILE, 'w') as f:
            f.write(str(last_seen_tweet_id))
        log.debug("Сохранен last_seen_tweet_id: %s в файл %s", last_seen_tweet_id, LAST_TWEET_ID_FILE)
    except Exception as e:
        log.exception("Ошибка при сохранении last_seen_tweet_id в файл %s.", LAST_TWEET_ID_FILE)

# Загружаем ID при старте скрипта
load_last_tweet_id()
log.info("Глобальные переменные инициализированы.")

# --- ФУНКЦИИ TWITTER API V2 ---
# Функции get_user_id_v2 и get_tweets_v2 остаются без изменений,
# они уже используют logging и обрабатывают ошибки tweepy
async def get_user_id_v2(username):
    if not twitter_client:
        log.warning("Попытка получить ID пользователя, но Twitter клиент не инициализирован.")
        return None
    try:
        response = twitter_client.get_user(username=username)
        if response.data:
            log.debug("Найден ID (%s) для пользователя %s", response.data.id, username)
            return response.data.id
        else:
            log.warning("Пользователь Twitter @%s не найден.", username)
            return None
    except tweepy.errors.TweepyException as e:
        log.error("Ошибка Twitter API при получении ID пользователя @%s: %s", username, e)
        return None
    except Exception as e:
        log.exception("Неожиданная ошибка при получении ID пользователя @%s.", username)
        return None

async def get_tweets_v2(user_id, count=5, since_id=None):
    if not twitter_client:
        log.warning("Попытка получить твиты, но Twitter клиент не инициализирован.")
        return []
    if not user_id:
        log.warning("Попытка получить твиты, но не указан user_id.")
        return []

    try:
        log.debug("Запрос твитов для user_id=%s, count=%d, since_id=%s", user_id, count, since_id)
        response = twitter_client.get_users_tweets(
            id=user_id,
            max_results=max(5, min(100, count)),
            since_id=since_id,
            tweet_fields=["created_at", "public_metrics"]
        )
        tweets_data = response.data or []
        if tweets_data:
             log.debug("Получено %d твитов", len(tweets_data))
        else:
             log.debug("Новых твитов не найдено (since_id=%s)", since_id)
        if response.meta:
             log.debug("Meta информация от Twitter API: %s", response.meta)

        return tweets_data

    except tweepy.errors.TweepyException as e:
        log.error("Ошибка Twitter API при получении твитов для user_id %s: %s", user_id, e)
        return []
    except Exception as e:
        log.exception("Неожиданная ошибка при получении твитов для user_id %s.", user_id)
        return []

# --- ФОНОВАЯ ЗАДАЧА: ПРОВЕРКА TWITTER ---
@tasks.loop(minutes=15)
async def check_twitter():
    global last_seen_tweet_id
    global target_user_id

    if not twitter_client:
        # log.warning("Пропуск проверки Twitter: клиент не инициализирован.") # Уже логируется при запуске
        return
    if not target_user_id:
        log.warning("Пропуск проверки Twitter: ID целевого пользователя %s неизвестен. Попытка получить...", TWITTER_USER_TO_MONITOR)
        new_id = await get_user_id_v2(TWITTER_USER_TO_MONITOR)
        if new_id:
            target_user_id = new_id
            log.info("ID целевого пользователя %s успешно получен: %s", TWITTER_USER_TO_MONITOR, target_user_id)
        else:
            log.warning("Не удалось получить ID для %s в цикле. Пропуск.", TWITTER_USER_TO_MONITOR)
            return

    log.info("Проверка новых твитов для @%s (ID: %s), since_id: %s",
                 TWITTER_USER_TO_MONITOR, target_user_id, last_seen_tweet_id)

    tweets = await get_tweets_v2(target_user_id, count=20, since_id=last_seen_tweet_id)

    if not tweets:
        log.info("Новых твитов от @%s не найдено.", TWITTER_USER_TO_MONITOR)
        return

    log.info("Найдено %d новых твитов от @%s.", len(tweets), TWITTER_USER_TO_MONITOR)
    tweets.reverse()

    newest_processed_id = last_seen_tweet_id # ID самого нового твита из *обработанного* пакета

    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        log.error("Целевой канал Discord с ID %d не найден! Проверьте TARGET_DISCORD_CHANNEL_ID.", TARGET_CHANNEL_ID)
        return

    # ИЗМЕНЕНИЕ 4: Проверка прав перед циклом отправки
    guild = channel.guild
    if not guild:
         log.warning("Не удалось определить сервер для канала %d. Пропуск отправки.", TARGET_CHANNEL_ID)
         return # Не можем проверить права без сервера

    me = guild.me
    permissions = channel.permissions_for(me)

    if not permissions.send_messages:
        log.error("Нет прав на отправку сообщений в канал #%s (%d) на сервере %s. Проверьте роли бота.", channel.name, channel.id, guild.name)
        # Можно добавить флаг, чтобы не логировать это каждые 15 минут
        return # Выходим, если нет прав

    if not permissions.embed_links:
         log.warning("Нет прав на встраивание ссылок в канале #%s (%d). Ссылки на твиты могут не отображаться корректно.", channel.name, channel.id)
         # Не выходим, но предупреждаем

    sent_count = 0
    for tweet in tweets:
        current_tweet_id = tweet.id # Сохраняем ID текущего твита

        tweet_text_lower = tweet.text.lower()
        if not KEYWORDS or any(keyword in tweet_text_lower for keyword in KEYWORDS):
            log.info("Релевантный твит (ID: %s): %s", tweet.id, tweet.text[:50] + "...")
            tweet_url = f"https://twitter.com/{TWITTER_USER_TO_MONITOR}/status/{tweet.id}"
            message = f"🚀 Новый твит от @{TWITTER_USER_TO_MONITOR}:\n{tweet.text}\n\n🔗 {tweet_url}"
            try:
                await channel.send(message)
                log.info("Твит (ID: %s) отправлен в канал %d", tweet.id, channel.id)
                sent_count += 1
                # Обновляем ID самого нового успешно обработанного твита
                newest_processed_id = current_tweet_id

            except discord.errors.Forbidden:
                # Эта ошибка теперь менее вероятна из-за проверки прав выше,
                # но может возникнуть из-за других ограничений (например, channel slowmode для бота)
                log.error("Forbidden: Не удалось отправить сообщение в канал %d (%s), возможно, из-за ограничений канала.", channel.id, channel.name)
                break # Прерываем отправку для этого цикла
            except Exception as e:
                log.exception("Не удалось отправить сообщение с твитом ID %s в канал %d.", tweet.id, channel.id)
        else:
            log.debug("Твит (ID: %s) пропущен (не содержит ключевых слов)", tweet.id)
            # Важно обновить ID, даже если твит пропущен, чтобы не проверять его снова
            newest_processed_id = current_tweet_id


    # ИЗМЕНЕНИЕ 2: Обновляем и сохраняем ID только если он изменился
    if newest_processed_id != last_seen_tweet_id:
        log.info("Обновление last_seen_tweet_id с %s на %s", last_seen_tweet_id, newest_processed_id)
        last_seen_tweet_id = newest_processed_id
        save_last_tweet_id() # Сохраняем в файл

# ИЗМЕНЕНИЕ 6: Обработчик ошибок для фоновой задачи
@check_twitter.error
async def on_check_twitter_error(error):
    log.exception("Необработанная ошибка в фоновой задаче check_twitter: %s", error)
    # Можно добавить сюда логику уведомления администратора или попытки перезапуска
    # traceback.print_exc() # Можно раскомментировать для вывода в консоль помимо лога

@check_twitter.before_loop
async def before_check_twitter():
    log.info("Ожидание готовности бота перед запуском цикла проверки Twitter...")
    await bot.wait_until_ready()
    log.info("Бот готов.")

    # ИЗМЕНЕНИЕ 2: Загрузка ID перенесена на старт скрипта
    # Здесь теперь только получаем ID пользователя, если он еще не получен

    if not target_user_id and twitter_client: # Проверяем, что клиент Twitter жив
        log.info("Получение ID пользователя Twitter для мониторинга...")
        global target_user_id
        target_user_id = await get_user_id_v2(TWITTER_USER_TO_MONITOR)
        if target_user_id:
            log.info("ID для @%s: %s. Мониторинг начнется.", TWITTER_USER_TO_MONITOR, target_user_id)
        else:
            log.error("Не удалось получить ID для @%s при запуске. Проверка Twitter будет пропускаться до успеха.", TWITTER_USER_TO_MONITOR)
    elif target_user_id:
         log.info("ID пользователя @%s (%s) уже известен.", TWITTER_USER_TO_MONITOR, target_user_id)

    if not twitter_client:
        log.warning("Клиент Twitter не инициализирован, мониторинг не начнется.")


@bot.event
async def on_ready():
    log.info("Бот %s (ID: %s) подключен и готов!", bot.user.name, bot.user.id)
    if twitter_client:
        log.info("Запуск фоновой задачи проверки Twitter...")
        check_twitter.start()
    else:
        log.warning("Фоновая задача проверки Twitter НЕ запущена (ошибка инициализации Twitter API).")


# --- DISCORD КОМАНДЫ ---
@bot.command(name="twitter", help="Показывает последние твиты пользователя. Использование: !twitter <username> [количество]")
async def twitter_command(ctx, username: str, count: int = 5):
    if not twitter_client:
        await ctx.send("❌ Ошибка: Модуль Twitter в данный момент неактивен.")
        return

    count = max(1, min(25, count))
    await ctx.send(f"🔍 Ищу последние {count} твитов от @{username}...")

    user_id = await get_user_id_v2(username)
    if not user_id:
        await ctx.send(f"❌ Не удалось найти пользователя Twitter @{username}.")
        return

    tweets = await get_tweets_v2(user_id, count=count)

    if tweets:
        # ИЗМЕНЕНИЕ 5: Не требуется, код уже использует Embeds.
        # УЛУЧШЕНИЕ: Используем display_avatar для большей надежности
        await ctx.send(f"📝 **Последние {len(tweets)} твитов от @{username}:**")
        for tweet in tweets:
            tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
            embed = discord.Embed(description=tweet.text, color=discord.Color.blue())
            embed.set_author(name=f"@{username}", url=tweet_url,
                             icon_url=ctx.author.display_avatar.url) # Используем display_avatar
            embed.add_field(name="Ссылка", value=f"[Перейти к твиту]({tweet_url})", inline=False)
            if tweet.created_at:
                embed.timestamp = tweet.created_at
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Не найдено твитов для @{username} или произошла ошибка API.")


@bot.command(name="helpme", help="Показывает это сообщение помощи.")
async def helpme_command(ctx):
    embed = discord.Embed(title="🤖 Помощь по командам бота", color=discord.Color.green())
    embed.add_field(name="`!twitter <имя_пользователя> [количество]`", value="Показывает последние твиты указанного пользователя (по умолчанию 5, макс. 25).", inline=False)
    embed.add_field(name="`!helpme`", value="Показывает это сообщение помощи.", inline=False)
    footer_text = f"Бот запущен"
    if ctx.guild:
        footer_text += f" на сервере {ctx.guild.name}"
    # УЛУЧШЕНИЕ: Добавим ID бота в футер для идентификации
    footer_text += f" | Bot ID: {bot.user.id}"
    embed.set_footer(text=footer_text)
    await ctx.send(embed=embed)


# --- ЗАПУСК БОТА ---
if __name__ == "__main__":
    log.info("Попытка запуска бота...")

    # ИЗМЕНЕНИЕ 1: Проверка флага ошибки инициализации Twitter
    if twitter_init_failed:
        log.critical("Запуск бота отменен из-за критической ошибки инициализации Twitter API.")
        sys.exit("Критическая ошибка: Не удалось инициализировать Twitter API. Проверьте токен и логи.")

    if not TOKEN:
        log.critical("Запуск бота отменен: DISCORD_BOT_TOKEN отсутствует!")
        sys.exit("Критическая ошибка: Отсутствует DISCORD_BOT_TOKEN.")

    # Запуск бота, если все основные компоненты готовы
    try:
        log.info("Запуск бота Discord...")
        bot.run(TOKEN, log_handler=None) # Передаем None, т.к. настроили свой logging
    except discord.errors.LoginFailure:
        log.critical("Ошибка входа в Discord: Неверный токен?")
        sys.exit("Критическая ошибка: Неверный токен Discord.")
    except Exception as e:
        log.critical("Непредвиденная ошибка при запуске бота: %s", e)
        traceback.print_exc() # Выводим трассировку для неизвестных ошибок
        sys.exit(f"Критическая ошибка при запуске: {e}")