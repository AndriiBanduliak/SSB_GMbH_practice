import discord
from discord.ext import commands, tasks
import logging
import asyncio # <-- Добавлен импорт
from typing import Optional, TYPE_CHECKING, Dict, Any, List

# Используем TYPE_CHECKING
if TYPE_CHECKING:
    from .twitter_client import TwitterService

log = logging.getLogger('discord_twitter_bot.tasks')

class TasksCog(commands.Cog, name="Hashtag Monitor"):
    """Ког для фоновой задачи мониторинга хештегов Twitter."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config: dict = getattr(bot, 'config', {})
        self.twitter_service: 'TwitterService' = getattr(bot, 'twitter_service', None)
        self._ = getattr(bot, 'translator_func', lambda key, **kwargs: key)

        if not self.config: log.error("TasksCog: Config не найден!")
        if not self.twitter_service: log.error("TasksCog: TwitterService не найден!")

        self.target_channel: Optional[discord.TextChannel] = None
        self.target_hashtags: List[str] = self.config.get('TARGET_HASHTAGS', [])
        self.target_hashtags = [tag.lower().lstrip('#') for tag in self.target_hashtags]

        log.info("Ког задач (Hashtag Monitor) инициализирован.")

    def cog_unload(self):
        self.check_hashtags.cancel()
        log.info("Фоновая задача check_hashtags остановлена.")

    @tasks.loop(hours=2)
    async def check_hashtags(self):
        """Периодически ищет твиты по хештегам и постит самый популярный."""
        if not self.twitter_service or self.twitter_service.init_failed:
            log.warning("Пропуск цикла check_hashtags: TwitterService недоступен.")
            return
        if not self.target_hashtags:
            log.warning("Пропуск цикла check_hashtags: Список целевых хештегов пуст.")
            return

        if not self.target_channel:
             await self._ensure_target_channel()
             if not self.target_channel:
                 log.error("Целевой канал не найден/недоступен. Пропуск цикла.")
                 return

        log.info(self._("TASK_STARTING_SEARCH", hashtags=', '.join(f'#{tag}' for tag in self.target_hashtags)))

        query = f"({' OR '.join(f'#{tag}' for tag in self.target_hashtags)}) -is:retweet lang:en"
        log.info(self._("TASK_SEARCH_QUERY", query=query))

        response = await self.twitter_service.search_recent_tweets(query=query, max_results=10)

        # *** ОБРАБОТКА RATE LIMIT ***
        if response and "rate_limit_sleep" in response:
            sleep_seconds = response["rate_limit_sleep"]
            log.warning(f"Получен сигнал о Rate Limit от Twitter API. Задача будет спать {sleep_seconds} секунд.")
            await asyncio.sleep(sleep_seconds) # <-- АСИНХРОННЫЙ sleep
            log.info("Задача проснулась после ожидания Rate Limit. Пропускаем текущий цикл.")
            return # Выходим из этого цикла, ждем следующей итерации по расписанию

        # Обработка других ошибок API
        if response is None or response.get("errors"):
            error_detail = "Response is None"
            if response and response.get("errors"):
                # Формируем более понятное сообщение об ошибке
                err = response["errors"][0]
                error_detail = f"{err.get('title', 'Unknown Error')}: {err.get('detail', 'No details')}"
                if 'parameter' in err: error_detail += f" (Parameter: {err['parameter']})"
                if 'value' in err: error_detail += f" (Value: {err['value']})"
            log.error(self._("TASK_SEARCH_API_ERROR", error=error_detail))
            return

        tweets = response.get("data")
        includes = response.get("includes")
        users = includes.get("users") if includes else None

        if not tweets or not users:
            log.info(self._("TASK_NO_TWEETS_FOUND"))
            return

        log.info(self._("TASK_PROCESSING_TWEETS", tweet_count=len(tweets)))

        users_data: Dict[str, Dict[str, Any]] = {user.id: user.data for user in users}

        max_followers = -1
        best_hashtag_found = None
        best_tweet_author_info = None

        for tweet in tweets:
            author_id = tweet.author_id
            # ID пользователя теперь строка в ответе API v2 через Tweepy v4
            author_data = users_data.get(str(author_id))

            if not author_data:
                log.warning(f"Не найдены данные для автора {author_id} твита {tweet.id}")
                continue

            public_metrics = author_data.get("public_metrics")
            if not public_metrics:
                 log.debug(f"Отсутствуют public_metrics для автора @{author_data.get('username', author_id)}")
                 continue

            followers_count = public_metrics.get("followers_count", 0)

            if followers_count > max_followers:
                tweet_text_lower = tweet.text.lower()
                found_target_hashtag = None
                for target_tag in self.target_hashtags:
                    if f"#{target_tag}" in tweet_text_lower:
                         found_target_hashtag = f"#{target_tag}"
                         break

                if found_target_hashtag:
                    max_followers = followers_count
                    best_hashtag_found = found_target_hashtag
                    best_tweet_author_info = author_data.get("username", f"ID:{author_id}")
                    log.debug(f"Новый кандидат: {best_hashtag_found} от @{best_tweet_author_info} ({max_followers} followers)")

        if best_hashtag_found:
            log.info(self._("TASK_FOUND_BEST_HASHTAG",
                          hashtag=best_hashtag_found,
                          username=best_tweet_author_info,
                          followers=max_followers))
            try:
                log.info(self._("TASK_SENDING_HASHTAG", hashtag=best_hashtag_found, channel_id=self.target_channel.id))
                await self.target_channel.send(best_hashtag_found)
                log.info(self._("TASK_SEND_SUCCESS", hashtag=best_hashtag_found))
            except discord.Forbidden:
                log.error(self._("TASK_SEND_FORBIDDEN", channel_id=self.target_channel.id))
                self.target_channel = None
            except Exception as e:
                log.exception(self._("TASK_SEND_ERROR", channel_id=self.target_channel.id, error=e))
        else:
            log.info(self._("TASK_NO_SUITABLE_TWEET"))

    async def _ensure_target_channel(self):
        """Пытается получить и проверить целевой канал Discord."""
        if self.target_channel and isinstance(self.target_channel, discord.TextChannel):
            if self.bot.get_channel(self.target_channel.id): return True
            else: log.warning(f"Кэшированный целевой канал {self.target_channel.id} больше не доступен."); self.target_channel = None

        target_channel_id = self.config.get('TARGET_CHANNEL_ID')
        if not target_channel_id: log.error("ID целевого канала не указан в конфигурации."); return False

        try:
            channel = self.bot.get_channel(target_channel_id)
            if not channel: channel = await self.bot.fetch_channel(target_channel_id)

            if isinstance(channel, discord.TextChannel):
                 if channel.guild:
                     me = channel.guild.me
                     if not channel.permissions_for(me).send_messages:
                          log.error(f"Нет прав на отправку сообщений в целевой канал {channel.id} ({channel.name})."); return False
                 self.target_channel = channel
                 log.info(f"Целевой канал для отправки хештегов: #{channel.name} ({channel.id})")
                 return True
            else: log.error(f"Канал с ID {target_channel_id} не является текстовым каналом!"); return False
        except (discord.NotFound, discord.Forbidden): log.error(self._("TASK_TARGET_CHANNEL_ERROR", channel_id=target_channel_id)); return False
        except Exception: log.exception(f"Неожиданная ошибка при получении канала {target_channel_id}."); return False

    @check_hashtags.before_loop
    async def before_check_hashtags(self):
        """Выполняется один раз перед первым запуском цикла."""
        log.info(self._("TASK_WAITING_BOT"))
        await self.bot.wait_until_ready()
        log.info(self._("TASK_BOT_READY"))

        if not self.twitter_service or self.twitter_service.init_failed:
             log.error(self._("TASK_TWITTER_INIT_FAILED"))
             self.check_hashtags.stop(); return

        if not await self._ensure_target_channel():
             log.error("Остановка задачи из-за проблем с целевым каналом.")
             self.check_hashtags.stop(); return

        log.info("Предварительные проверки для check_hashtags пройдены.")

    @check_hashtags.error
    async def on_check_hashtags_error(self, error):
        """Обработчик необработанных ошибок в цикле задачи."""
        log.exception(self._("TASK_UNHANDLED_ERROR", error=error))

# Функция setup для загрузки кога ботом
async def setup(bot: commands.Bot):
    await bot.add_cog(TasksCog(bot))
    log.info("Ког TasksCog (Hashtag Monitor) успешно загружен.")