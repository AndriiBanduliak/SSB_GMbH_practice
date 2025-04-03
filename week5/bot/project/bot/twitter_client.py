import tweepy
import logging
import time # <-- Добавлен импорт
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
            # *** ИЗМЕНЕНИЕ: Отключаем автоматическое ожидание ***
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                wait_on_rate_limit=False # <-- Установлено в False
            )
            log.info("Клиент Tweepy успешно инициализирован (wait_on_rate_limit=False).")
        except tweepy.errors.TweepyException as e:
            log.exception("Ошибка инициализации клиента Tweepy: %s", e)
            self.init_failed = True
        except Exception as e:
            log.exception("Неожиданная ошибка при инициализации клиента Tweepy: %s", e)
            self.init_failed = True

    async def search_recent_tweets(self, query: str, max_results: int = 100) -> Optional[Dict[str, Any]]:
        """
        Ищет недавние твиты по запросу, запрашивая ID автора и его public_metrics.
        Возвращает полный объект ответа API v2 Search или словарь с информацией об ожидании/ошибке.
        """
        if self.init_failed or not self.client:
            log.warning("Попытка поиска твитов, но клиент Twitter не инициализирован.")
            return {"errors": [{"title": "ClientInitError", "detail": "Twitter client not initialized"}]}
        try:
            log.debug("Запрос поиска твитов: query='%s', max_results=%d", query, max_results)
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max(10, min(100, max_results)),
                expansions=['author_id'],
                user_fields=['public_metrics']
            )

            if response:
                 log.debug("Получен ответ от API поиска: %s твитов, %s пользователей в includes.",
                          len(response.data) if response.data else 0,
                          len(response.includes.get('users', [])) if response.includes else 0)
            else:
                 log.warning("API поиска Twitter вернуло None.")

            response_dict = {
                "data": response.data if response else None,
                "includes": response.includes if response else {},
                "meta": response.meta if response else {},
                "errors": getattr(response, "errors", []) if response else []
            }
            return response_dict

        except tweepy.errors.TooManyRequests as e: # *** Явно ловим 429 ошибку ***
            log.warning("Rate limit exceeded (429). Twitter API response: %s", e.response.text if e.response else "N/A")
            reset_time_str = e.response.headers.get("x-rate-limit-reset") if e.response else None
            sleep_duration = 15 * 60 # По умолчанию ждем 15 минут
            if reset_time_str:
                try:
                    reset_timestamp = int(reset_time_str)
                    now_timestamp = int(time.time())
                    # Добавляем небольшой буфер (5 сек), чтобы точно успеть
                    sleep_duration = max(5, (reset_timestamp - now_timestamp) + 5)
                    log.info(f"Rate limit reset time: {reset_timestamp}. Need to sleep for {sleep_duration} seconds.")
                except (ValueError, TypeError):
                    log.warning(f"Could not parse x-rate-limit-reset header: {reset_time_str}. Using default sleep time.")

            # *** Возвращаем специальный словарь для ожидания ***
            return {"rate_limit_sleep": sleep_duration}

        except tweepy.errors.TweepyException as e:
            log.error("Ошибка API Twitter при поиске твитов (query='%s'): %s", query, e)
            return {"errors": [{"title": "TweepyException", "detail": str(e)}]}
        except Exception as e:
            log.exception("Неожиданная ошибка при поиске твитов (query='%s'): %s", query, e)
            return {"errors": [{"title": "UnexpectedException", "detail": str(e)}]}

    # --- Старые методы можно удалить, если команда !twitter не нужна ---
    # async def get_user_id_v2(...)
    # async def get_tweets_v2(...)