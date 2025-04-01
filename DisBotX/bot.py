import discord
from discord.ext import commands, tasks
import tweepy  # Используем tweepy для API v2
import os
import logging
from datetime import datetime
from dotenv import load_dotenv  # Для загрузки .env файла
import sys  # Для выхода при ошибке конфигурации

# --- ЗАГРУЗКА .ENV ---
load_dotenv()
print("Переменные окружения загружены.")  # Debug print

# --- LOGGING EINSTELLEN ---
LOG_FILE = "bot.log"
# (Код логирования остается без изменений, он хороший)
if os.path.exists(LOG_FILE):
    # Проверяем права на запись перед переименованием
    if os.access(LOG_FILE, os.W_OK) and os.access(".", os.W_OK):
        try:
            os.rename(LOG_FILE, LOG_FILE + ".old." +
                      datetime.now().strftime("%Y%m%d%H%M%S"))
            # Debug print
            print(f"Старый лог файл переименован в {LOG_FILE}.old...")
        except OSError as e:
            # Debug print
            print(f"Не удалось переименовать лог файл {LOG_FILE}: {e}")
            logging.warning(
                "Не удалось переименовать старый лог файл %s: %s", LOG_FILE, e)
    else:
        # Debug print
        print(
            f"Нет прав на переименование {LOG_FILE} или запись в текущую директорию.")
        logging.warning(
            "Недостаточно прав для переименования старого лог файла %s.", LOG_FILE)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logging.info("Логирование настроено.")

# --- КОНФИГУРАЦИЯ ИЗ .ENV ---
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
TARGET_CHANNEL_ID_STR = os.environ.get("TARGET_DISCORD_CHANNEL_ID")
TWITTER_USER_TO_MONITOR = os.environ.get("TWITTER_USER_TO_MONITOR")
# По умолчанию пустая строка
KEYWORDS_STR = os.environ.get("KEYWORDS_TO_MONITOR", "")

# Проверка обязательных переменных
errors = []
if not TOKEN:
    errors.append("DISCORD_BOT_TOKEN")
if not TWITTER_BEARER_TOKEN:
    errors.append("TWITTER_BEARER_TOKEN")
if not TARGET_CHANNEL_ID_STR:
    errors.append("TARGET_DISCORD_CHANNEL_ID")
if not TWITTER_USER_TO_MONITOR:
    errors.append("TWITTER_USER_TO_MONITOR")

if errors:
    logging.error(
        "Критические переменные окружения не установлены: %s", ", ".join(errors))
    sys.exit(
        f"Ошибка: Не установлены переменные окружения: {', '.join(errors)}. Проверьте ваш .env файл.")

# Преобразование типов и обработка опциональных
try:
    TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID_STR)
except ValueError:
    logging.error(
        "TARGET_DISCORD_CHANNEL_ID должен быть числом: %s", TARGET_CHANNEL_ID_STR)
    sys.exit(
        f"Ошибка: TARGET_DISCORD_CHANNEL_ID ({TARGET_CHANNEL_ID_STR}) не является допустимым числовым ID.")

KEYWORDS = [k.strip().lower() for k in KEYWORDS_STR.split(',') if k.strip()]
logging.info("Конфигурация загружена. Канал: %d, Пользователь: %s, Ключевые слова: %s",
             TARGET_CHANNEL_ID, TWITTER_USER_TO_MONITOR, KEYWORDS)

# --- DISCORD BOT EINSTELLUNGEN ---
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True  # Оставляем на всякий случай
intents.message_content = True  # <-- ВАЖНО для чтения команд
bot = commands.Bot(command_prefix="!", intents=intents)
logging.info("Discord Intents настроены.")

# --- TWITTER (X) API V2 CLIENT ---
try:
    # Используем API v2 Client с Bearer Token (достаточно для чтения публичных твитов)
    twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    logging.info("Клиент Twitter API v2 успешно инициализирован.")
    # Проверка аутентификации (опционально, но полезно)
    me_user = twitter_client.get_me()
    if me_user.data:
        logging.info(
            "Аутентификация Twitter Bearer Token прошла успешно (ID приложения: %s)", me_user.data.id)
    else:
        logging.warning(
            "Не удалось проверить аутентификацию Twitter Bearer Token (get_me вернул пустые данные), но клиент создан.")
except tweepy.errors.TweepyException as e:
    logging.error("Ошибка инициализации клиента Twitter API v2: %s", e)
    # Устанавливаем в None, чтобы бот мог запуститься, но функции Twitter не работали
    twitter_client = None
except Exception as e:
    logging.error(
        "Неожиданная ошибка при инициализации клиента Twitter: %s", e)
    twitter_client = None


# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ДЛЯ ОТСЛЕЖИВАНИЯ ---
# ID пользователя Twitter для мониторинга (получим в before_loop)
target_user_id = None
# ID последнего твита, отправленного в Discord (для предотвращения дублей)
# Для надежности лучше хранить в файле или БД, но для примера используем переменную
last_seen_tweet_id = None
logging.info("Глобальные переменные для отслеживания инициализированы.")


# --- ФУНКЦИИ TWITTER API V2 ---
async def get_user_id_v2(username):
    """Получает ID пользователя Twitter по его имени (API v2)."""
    if not twitter_client:
        logging.warning(
            "Попытка получить ID пользователя, но Twitter клиент не инициализирован.")
        return None
    try:
        response = twitter_client.get_user(username=username)
        if response.data:
            logging.debug("Найден ID (%s) для пользователя %s",
                          response.data.id, username)
            return response.data.id
        else:
            logging.warning("Пользователь Twitter @%s не найден.", username)
            return None
    except tweepy.errors.TweepyException as e:
        logging.error(
            "Ошибка Twitter API при получении ID пользователя @%s: %s", username, e)
        return None
    except Exception as e:
        logging.error(
            "Неожиданная ошибка при получении ID пользователя @%s: %s", username, e)
        return None


async def get_tweets_v2(user_id, count=5, since_id=None):
    """Получает последние твиты пользователя по ID (API v2)."""
    if not twitter_client:
        logging.warning(
            "Попытка получить твиты, но Twitter клиент не инициализирован.")
        return []
    if not user_id:
        logging.warning("Попытка получить твиты, но не указан user_id.")
        return []

    tweets_data = []
    try:
        logging.debug(
            "Запрос твитов для user_id=%s, count=%d, since_id=%s", user_id, count, since_id)
        response = twitter_client.get_users_tweets(
            id=user_id,
            # API v2 требует минимум 5, максимум 100
            max_results=max(5, min(100, count)),
            since_id=since_id,
            # Запросим доп. поля, если нужны
            tweet_fields=["created_at", "public_metrics"]
        )
        if response.data:
            logging.debug("Получено %d твитов", len(response.data))
            # response.data содержит объекты Tweet, берем текст
            tweets_data = response.data
        else:
            logging.debug("Новых твитов не найдено (since_id=%s)", since_id)
            # Если since_id был указан, это нормально. Если нет - значит, у пользователя нет твитов.

        # Логирование meta информации (полезно для отладки rate limits и since_id)
        if response.meta:
            logging.debug("Meta информация от Twitter API: %s", response.meta)
            # Если есть newest_id, можно использовать его для обновления last_seen_tweet_id
            # if 'newest_id' in response.meta:
            #    update_last_seen_id(response.meta['newest_id']) # Пример

        return tweets_data  # Возвращаем полные объекты Tweet

    except tweepy.errors.TweepyException as e:
        logging.error(
            "Ошибка Twitter API при получении твитов для user_id %s: %s", user_id, e)
        return []
    except Exception as e:
        logging.error(
            "Неожиданная ошибка при получении твитов для user_id %s: %s", user_id, e)
        return []


# --- ФОНОВАЯ ЗАДАЧА: ПРОВЕРКА TWITTER ---
@tasks.loop(minutes=15)
async def check_twitter():
    global last_seen_tweet_id # Эта строка уже была для last_seen_tweet_id
    global target_user_id     # <--- ДОБАВЬ ЭТУ СТРОКУ ДЛЯ ЯВНОСТИ

    if not twitter_client:
        logging.warning("Пропуск проверки Twitter: клиент не инициализирован.")
        return

    # Теперь проверка 'if not target_user_id:' должна быть менее подозрительной для IDE
    if not target_user_id:
        logging.warning("Пропуск проверки Twitter: ID целевого пользователя %s неизвестен.", TWITTER_USER_TO_MONITOR)
        # Попробуем получить ID снова, если его не удалось получить в before_loop
        new_id = await get_user_id_v2(TWITTER_USER_TO_MONITOR)
        if new_id:
            # 'global target_user_id' здесь уже не нужен, так как он объявлен в начале функции
            target_user_id = new_id
            logging.info("ID целевого пользователя %s успешно получен: %s", TWITTER_USER_TO_MONITOR, target_user_id)
        else:
            return # Если снова не удалось, пропускаем цикл

    logging.info("Проверка новых твитов для @%s (ID: %s), ищем начиная с tweet_id: %s",
                 TWITTER_USER_TO_MONITOR, target_user_id, last_seen_tweet_id)

    # Получаем только НОВЫЕ твиты с момента последней проверки
    # count можно увеличить
    tweets = await get_tweets_v2(target_user_id, count=20, since_id=last_seen_tweet_id)

    if not tweets:
        logging.info("Новых твитов от @%s не найдено.",
                     TWITTER_USER_TO_MONITOR)
        return  # Нет новых твитов

    logging.info("Найдено %d новых твитов от @%s.",
                 len(tweets), TWITTER_USER_TO_MONITOR)

    # Твиты приходят от новых к старым, перевернем для обработки в хронологическом порядке
    tweets.reverse()

    # Запоминаем текущий ID на случай, если твиты не пройдут фильтр
    new_last_id = last_seen_tweet_id

    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        logging.error("Целевой канал Discord с ID %d не найден!",
                      TARGET_CHANNEL_ID)
        return

    sent_count = 0
    for tweet in tweets:
        # Обновляем ID последнего *обработанного* твита
        new_last_id = tweet.id

        tweet_text_lower = tweet.text.lower()
        # Проверяем ключевые слова (если они заданы)
        if not KEYWORDS or any(keyword in tweet_text_lower for keyword in KEYWORDS):
            logging.info("Найден релевантный твит (ID: %s): %s",
                         tweet.id, tweet.text[:50] + "...")
            # Формируем ссылку на твит
            tweet_url = f"https://twitter.com/{TWITTER_USER_TO_MONITOR}/status/{tweet.id}"
            message = f"🚀 Новый твит от @{TWITTER_USER_TO_MONITOR}:\n{tweet.text}\n\n🔗 {tweet_url}"
            try:
                await channel.send(message)
                logging.info("Твит (ID: %s) отправлен в канал %d",
                             tweet.id, channel.id)
                sent_count += 1
            except discord.errors.Forbidden:
                logging.error(
                    "Нет прав на отправку сообщения в канал %d (%s)", channel.id, channel.name)
                # Возможно, стоит остановить задачу или оповестить администратора
                break  # Прерываем отправку в этом цикле
            except Exception as e:
                logging.error(
                    "Не удалось отправить сообщение в канал %d: %s", channel.id, e)
        else:
            logging.debug(
                "Твит (ID: %s) пропущен (не содержит ключевых слов)", tweet.id)

    # Обновляем ID *только после* успешной обработки всех твитов в пакете
    if new_last_id != last_seen_tweet_id:
        logging.info("Обновление last_seen_tweet_id с %s на %s",
                     last_seen_tweet_id, new_last_id)
        last_seen_tweet_id = new_last_id
        # Здесь можно добавить сохранение last_seen_tweet_id в файл


@check_twitter.before_loop
async def before_check_twitter():
    """Выполняется перед первым запуском цикла check_twitter."""
    logging.info(
        "Ожидание готовности бота перед запуском цикла проверки Twitter...")
    await bot.wait_until_ready()
    logging.info(
        "Бот готов. Получение ID пользователя Twitter для мониторинга...")
    global target_user_id  # Указываем, что будем менять глобальную переменную
    target_user_id = await get_user_id_v2(TWITTER_USER_TO_MONITOR)
    if target_user_id:
        logging.info("ID для @%s: %s. Запуск цикла проверки Twitter.",
                     TWITTER_USER_TO_MONITOR, target_user_id)
        # Здесь можно загрузить last_seen_tweet_id из файла, если он есть
    else:
        logging.error(
            "Не удалось получить ID для @%s. Проверка Twitter будет пропускаться до успешного получения ID.", TWITTER_USER_TO_MONITOR)


@bot.event
async def on_ready():
    """Выполняется, когда бот успешно подключился к Discord."""
    logging.info("Бот %s (ID: %s) подключен и готов!",
                 bot.user.name, bot.user.id)
    if twitter_client:
        check_twitter.start()  # Запускаем фоновую задачу проверки Twitter
        logging.info("Фоновая задача проверки Twitter запущена.")
    else:
        logging.warning(
            "Фоновая задача проверки Twitter НЕ запущена, т.к. клиент Twitter не инициализирован.")


# --- DISCORD КОМАНДЫ ---
@bot.command(name="twitter", help="Показывает последние твиты пользователя. Использование: !twitter <username> [количество]")
async def twitter_command(ctx, username: str, count: int = 5):
    """Команда !twitter <Benutzername> [Anzahl] - Показывает последние твиты пользователя."""
    if not twitter_client:
        await ctx.send("❌ Ошибка: Модуль Twitter в данный момент неактивен.")
        return

    # Ограничим count разумным значением
    # API v2 позволяет до 100, но для команды хватит и 25
    count = max(1, min(25, count))

    await ctx.send(f"🔍 Ищу последние {count} твитов от @{username}...")

    user_id = await get_user_id_v2(username)
    if not user_id:
        await ctx.send(f"❌ Не удалось найти пользователя Twitter @{username}.")
        return

    tweets = await get_tweets_v2(user_id, count=count)

    if tweets:
        await ctx.send(f"📝 **Последние {len(tweets)} твитов от @{username}:**")
        for tweet in tweets:
            tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
            # Используем discord.Embed для лучшего форматирования
            embed = discord.Embed(description=tweet.text,
                                  color=discord.Color.blue())
            # Попробуем взять аватар автора команды
            embed.set_author(name=f"@{username}", url=tweet_url,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            embed.add_field(
                name="Ссылка", value=f"[Перейти к твиту]({tweet_url})", inline=False)
            if tweet.created_at:
                embed.timestamp = tweet.created_at
            await ctx.send(embed=embed)
            # Обычный текстовый вариант:
            # await ctx.send(f"[{tweet.created_at.strftime('%Y-%m-%d %H:%M') if tweet.created_at else 'Время ?'}] {tweet.text}\n🔗 {tweet_url}\n---")
    else:
        await ctx.send(f"❌ Не найдено твитов для @{username} или произошла ошибка API.")


@bot.command(name="helpme", help="Показывает это сообщение помощи.")
async def helpme_command(ctx):
    """Команда !helpme - Показывает список доступных команд."""
    # Используем встроенную систему помощи discord.py для большей гибкости в будущем,
    # но пока оставим простой вариант.
    embed = discord.Embed(title="🤖 Помощь по командам бота",
                          color=discord.Color.green())
    embed.add_field(name="`!twitter <имя_пользователя> [количество]`",
                    value="Показывает последние твиты указанного пользователя (по умолчанию 5, макс. 25).", inline=False)
    embed.add_field(name="`!helpme`",
                    value="Показывает это сообщение помощи.", inline=False)
    embed.set_footer(
        text=f"Бот запущен на сервере {ctx.guild.name}" if ctx.guild else "Бот запущен в ЛС")
    await ctx.send(embed=embed)


# --- ЗАПУСК БОТА ---
if __name__ == "__main__":
    logging.info("Попытка запуска бота...")
    if not TOKEN:
        # Эта проверка уже была выше, но на всякий случай
        logging.critical(
            "Невозможно запустить бота: DISCORD_BOT_TOKEN отсутствует!")
    elif not twitter_client and TARGET_CHANNEL_ID:  # Если Twitter нужен для основной функции
        logging.warning(
            "Бот запускается, НО КЛИЕНТ TWITTER НЕ ИНИЦИАЛИЗИРОВАН. Функции Twitter работать не будут.")
        # Реши, должен ли бот вообще запускаться в этом случае. Может быть, лучше sys.exit()?
        # Например:
        # logging.critical("Невозможно запустить бота: Ошибка инициализации Twitter API!")
        # sys.exit("Критическая ошибка: Не удалось инициализировать Twitter API.")
        try:
            logging.info("Запуск бота Discord...")
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            logging.critical("Ошибка входа в Discord: Неверный токен?")
        except Exception as e:
            logging.critical("Непредвиденная ошибка при запуске бота: %s", e)

    else:
        try:
            logging.info("Запуск бота Discord...")
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            logging.critical("Ошибка входа в Discord: Неверный токен?")
        except Exception as e:
            logging.critical("Непредвиденная ошибка при запуске бота: %s", e)
