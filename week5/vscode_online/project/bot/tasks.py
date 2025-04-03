import discord
from discord.ext import commands, tasks
import logging
import os
from typing import Optional, TYPE_CHECKING, Dict, Any, List # Добавлены типы

# Используем TYPE_CHECKING для избежания цикличных импортов
if TYPE_CHECKING:
    from .twitter_client import TwitterService
    from .settings import SettingsManager
    # config и translator импортировать не нужно, они берутся из bot

# Импортируем имя файла для last_tweet_id
from .config import LAST_TWEET_ID_FILE

log = logging.getLogger('discord_twitter_bot.tasks')

class TasksCog(commands.Cog, name="Фоновые задачи"):
    """Ког, содержащий фоновые задачи, такие как проверка Twitter."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Получаем зависимости из атрибутов бота
        self.config: dict = getattr(bot, 'config', {})
        self.twitter_service: 'TwitterService' = getattr(bot, 'twitter_service', None)
        self.settings_manager: 'SettingsManager' = getattr(bot, 'settings_manager', None)
        self._ = getattr(bot, 'translator_func', lambda key, **kwargs: key) # Переводчик или заглушка

        # Проверка зависимостей
        if not self.config:
            log.error("TasksCog: Config не найден в атрибутах бота!")
        if not self.twitter_service:
            log.error("TasksCog: TwitterService не найден в атрибутах бота!")
        if not self.settings_manager:
            log.error("TasksCog: SettingsManager не найден в атрибутах бота!")

        # Переменные состояния задачи
        self.target_user_id: Optional[int] = None # Убрали инициализацию отсюда
        self.last_seen_tweet_id: Optional[int] = self._load_last_tweet_id()
        self.target_channel: Optional[discord.TextChannel] = None

        log.info("Ког задач инициализирован. Last seen tweet ID from file: %s", self.last_seen_tweet_id)
        # !!! Запуск задачи ПЕРЕМЕЩЕН в on_ready в main.py !!!
        # self.check_twitter.start()

    def cog_unload(self):
        """Вызывается при выгрузке кога."""
        self.check_twitter.cancel()
        log.info("Фоновая задача check_twitter остановлена.")

    # --- Управление файлом last_tweet.id ---
    # TODO: Эта логика устареет, когда last_seen_tweet_id будет храниться для каждого пользователя/сервера.
    # Пока оставляем для совместимости с текущим этапом.
    def _load_last_tweet_id(self) -> Optional[int]:
        """Загружает ID последнего виденного твита из файла."""
        try:
            if os.path.exists(LAST_TWEET_ID_FILE):
                with open(LAST_TWEET_ID_FILE, 'r') as f:
                    content = f.read().strip()
                    if content: return int(content)
                    else: log.warning(f"Файл {LAST_TWEET_ID_FILE} пуст."); return None
            else:
                log.info(f"Файл {LAST_TWEET_ID_FILE} не найден.")
                return None
        except ValueError:
            log.error(f"Некорректное значение в файле {LAST_TWEET_ID_FILE}. Ожидалось число.")
            return None
        except Exception:
            log.exception(f"Ошибка при загрузке ID последнего твита из {LAST_TWEET_ID_FILE}")
            return None

    def _save_last_tweet_id(self):
        """Сохраняет ID последнего обработанного твита в файл."""
        if self.last_seen_tweet_id is None: return
        try:
            with open(LAST_TWEET_ID_FILE, 'w') as f: f.write(str(self.last_seen_tweet_id))
            log.debug(f"ID последнего твита ({self.last_seen_tweet_id}) сохранен в {LAST_TWEET_ID_FILE}")
        except Exception:
            log.exception(f"Ошибка при сохранении ID последнего твита ({self.last_seen_tweet_id}) в {LAST_TWEET_ID_FILE}")

    # --- Основной цикл проверки Twitter ---
    @tasks.loop(minutes=15)
    async def check_twitter(self):
        """Периодически проверяет новые твиты целевого пользователя (из config)."""
        # Проверка инициализации зависимостей
        if not self.twitter_service or not self.settings_manager or not self.config:
             log.error("Пропуск цикла check_twitter: одна или несколько зависимостей не инициализированы.")
             return

        # Проверяем, инициализирован ли Twitter клиент и получен ли ID пользователя
        if self.twitter_service.init_failed or not self.target_user_id:
            log.warning("Пропуск цикла check_twitter: Twitter клиент не инициализирован или ID целевого пользователя не получен.")
            # Попытка получить ID снова (на случай если он не был получен в before_loop)
            if not self.twitter_service.init_failed and not self.target_user_id and self.config.get('TWITTER_USER_TO_MONITOR'):
                 log.info("Попытка получить ID пользователя в цикле...")
                 await self._ensure_target_user_id() # Вызываем внутренний метод
                 if not self.target_user_id:
                     log.error("Не удалось получить ID пользователя в цикле. Пропуск.")
                     return # Все еще не можем получить ID
            else:
                return # Выходим, если Twitter не работает или нет имени пользователя

        # Проверяем и кэшируем целевой канал
        if not self.target_channel:
             await self._ensure_target_channel() # Вызываем внутренний метод
             if not self.target_channel:
                 log.error("Целевой канал не найден или недоступен. Пропуск цикла.")
                 return # Не можем найти канал

        # Используем язык по умолчанию для логов задачи
        log_lang_guild_id = None

        log.info(self._("TASK_CHECKING_TWEETS", log_lang_guild_id,
                      username=self.config['TWITTER_USER_TO_MONITOR'],
                      user_id=self.target_user_id,
                      since_id=self.last_seen_tweet_id))

        tweets: Optional[List[Dict[str, Any]]] = await self.twitter_service.get_tweets_v2(
            self.target_user_id,
            count=20, # Запрашиваем больше, чтобы не пропустить, если было много твитов
            since_id=self.last_seen_tweet_id
        )

        if tweets is None:
            log.error("Ошибка API Twitter при получении твитов в фоновой задаче.")
            return
        if not tweets:
            log.info("Новых твитов не найдено.")
            return

        log.info(self._("TASK_FOUND_TWEETS", log_lang_guild_id, count=len(tweets), username=self.config['TWITTER_USER_TO_MONITOR']))

        tweets.reverse() # Обрабатываем от старых к новым

        newest_processed_id = self.last_seen_tweet_id
        guild = self.target_channel.guild
        current_guild_id = guild.id # Получаем ID сервера для переводов сообщений в канал

        # Проверка прав (можно вынести в _ensure_target_channel, но оставим здесь для ясности)
        me = guild.me
        permissions = self.target_channel.permissions_for(me)
        can_send = permissions.send_messages
        can_embed = permissions.embed_links

        if not can_send:
            err_msg = self._("ERROR_FORBIDDEN_SEND", current_guild_id, channel_name=self.target_channel.name, channel_id=self.target_channel.id, server_name=guild.name)
            log.error(err_msg + " Остановка проверки до следующего цикла.")
            return

        if not can_embed:
             log.warning(self._("WARN_NO_EMBED", current_guild_id, channel_name=self.target_channel.name, channel_id=self.target_channel.id))

        # Обработка твитов
        for tweet in tweets:
            current_tweet_id = tweet['id']
            # Пропускаем твиты старше или равные уже виденному (на случай если since_id не сработал идеально)
            if self.last_seen_tweet_id is not None and current_tweet_id <= self.last_seen_tweet_id:
                log.debug(f"Пропуск твита {current_tweet_id}, так как он не новее {self.last_seen_tweet_id}")
                continue

            tweet_text_lower = tweet['text'].lower()
            keywords = self.config.get('KEYWORDS', []) # Получаем ключевые слова из конфига

            if not keywords or any(keyword in tweet_text_lower for keyword in keywords):
                tweet_url = f"https://twitter.com/{self.config['TWITTER_USER_TO_MONITOR']}/status/{tweet['id']}"
                message = self._("NEW_TWEET_ALERT", current_guild_id, username=self.config['TWITTER_USER_TO_MONITOR'], text=tweet['text'], url=tweet_url)
                try:
                    await self.target_channel.send(message, suppress_embeds=not can_embed)
                    log.info(self._("TASK_SENDING_TWEET", log_lang_guild_id, tweet_id=tweet['id'], channel_id=self.target_channel.id))
                    newest_processed_id = current_tweet_id

                except discord.errors.Forbidden:
                    err_msg = self._("ERROR_FORBIDDEN_SEND", current_guild_id, channel_name=self.target_channel.name, channel_id=self.target_channel.id, server_name=guild.name)
                    log.error(self._("TASK_FORBIDDEN_SEND_LOOP", log_lang_guild_id, error_message=err_msg))
                    break # Прерываем обработку этого набора твитов
                except Exception:
                    log.exception(self._("TASK_ERROR_SENDING_TWEET", log_lang_guild_id, tweet_id=tweet['id'], channel_id=self.target_channel.id))
                    # Не обновляем ID, попробуем снова в след. раз, но прерываем текущий набор
                    break
            else:
                log.debug(self._("TASK_SKIPPING_TWEET_KEYWORDS", log_lang_guild_id, tweet_id=tweet['id']))
                newest_processed_id = current_tweet_id # Обновляем ID, т.к. твит обработан (пропущен)

        # Сохраняем ID последнего успешно обработанного/пропущенного твита
        if newest_processed_id != self.last_seen_tweet_id and newest_processed_id is not None:
             log.info(self._("TASK_UPDATING_LAST_ID", log_lang_guild_id, old_id=self.last_seen_tweet_id, new_id=newest_processed_id))
             self.last_seen_tweet_id = newest_processed_id
             self._save_last_tweet_id() # TODO: Изменить при переходе на хранение по пользователям

    # --- Методы выполняемые перед запуском цикла ---
    async def _ensure_target_user_id(self):
        """Пытается получить ID целевого пользователя из конфига."""
        if self.target_user_id: return True # Уже есть
        if not self.twitter_service or self.twitter_service.init_failed: return False # Twitter недоступен

        target_username = self.config.get('TWITTER_USER_TO_MONITOR')
        if not target_username:
            log.warning("Имя пользователя Twitter для мониторинга не указано в конфигурации.")
            return False

        log.info(self._("TASK_GETTING_USER_ID", None, username=target_username))
        user_id = await self.twitter_service.get_user_id_v2(target_username)
        if user_id:
            self.target_user_id = user_id
            log.info(self._("TASK_USER_ID_SUCCESS", None, user_id=user_id, username=target_username))
            return True
        else:
            log.error(self._("TASK_USER_ID_FAIL", None, username=target_username))
            return False

    async def _ensure_target_channel(self):
        """Пытается получить и проверить целевой канал Discord."""
        if self.target_channel and isinstance(self.target_channel, discord.TextChannel):
            # Проверить, существует ли канал еще (на случай удаления)
            try:
                 await self.bot.fetch_channel(self.target_channel.id)
                 return True # Канал существует и кэширован
            except (discord.NotFound, discord.Forbidden):
                 log.warning(f"Кэшированный целевой канал {self.target_channel.id} больше не доступен.")
                 self.target_channel = None # Сбрасываем кэш

        target_channel_id = self.config.get('TARGET_CHANNEL_ID')
        if not target_channel_id:
            log.error("ID целевого канала не указан в конфигурации.")
            return False

        try:
            channel = await self.bot.fetch_channel(target_channel_id)
            if isinstance(channel, discord.TextChannel):
                self.target_channel = channel
                log.info(f"Целевой канал для отправки твитов: #{channel.name} ({channel.id})")
                # Проверим права сразу
                if channel.guild:
                     me = channel.guild.me
                     permissions = channel.permissions_for(me)
                     if not permissions.send_messages:
                          log.error(f"Нет прав на отправку сообщений в целевой канал {channel.id}.")
                          self.target_channel = None # Считаем канал недоступным
                          return False
                     if not permissions.embed_links:
                           log.warning(f"Нет прав на встраивание ссылок в целевом канале {channel.id}.")
                return True
            else:
                log.error(f"Канал с ID {target_channel_id} не является текстовым каналом!")
                return False
        except discord.NotFound:
            log.error(self._("ERROR_TARGET_CHANNEL_NOT_FOUND", None, channel_id=target_channel_id))
            return False
        except discord.Forbidden:
            log.error(f"Нет доступа к каналу с ID {target_channel_id}.")
            return False
        except Exception:
            log.exception(f"Неожиданная ошибка при получении канала {target_channel_id}.")
            return False


    @check_twitter.before_loop
    async def before_check_twitter(self):
        """Выполняется один раз перед первым запуском цикла."""
        log.info(self._("TASK_WAITING_BOT", None))
        await self.bot.wait_until_ready() # Ждем полной готовности бота
        log.info(self._("TASK_BOT_READY", None))

        # Проверка инициализации Twitter и получение ID пользователя
        if not await self._ensure_target_user_id():
             log.error("Не удалось получить ID пользователя Twitter перед запуском цикла. Задача не будет выполняться.")
             self.check_twitter.stop()
             return

        # Проверка и кэширование целевого канала
        if not await self._ensure_target_channel():
             log.error("Не удалось получить доступ к целевому каналу Discord перед запуском цикла. Задача не будет выполняться.")
             self.check_twitter.stop()
             return

        log.info("Предварительные проверки для check_twitter пройдены.")


    @check_twitter.error
    async def on_check_twitter_error(self, error):
        """Обработчик необработанных ошибок в цикле задачи."""
        log.exception(self._("TASK_UNHANDLED_ERROR", None, error=error))


# Функция setup для загрузки кога ботом
async def setup(bot: commands.Bot):
    # Теперь зависимости передаются через bot в __init__
    await bot.add_cog(TasksCog(bot))
    log.info("Ког TasksCog успешно загружен.")