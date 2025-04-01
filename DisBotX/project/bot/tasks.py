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
