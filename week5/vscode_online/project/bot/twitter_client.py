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
