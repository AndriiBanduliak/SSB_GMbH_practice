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
