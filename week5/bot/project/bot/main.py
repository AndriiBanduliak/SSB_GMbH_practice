import discord
from discord.ext import commands
import asyncio
import logging
import sys
import traceback
from typing import Optional

# --- Импорты из нашего пакета ---
from .config import CONFIG, log
from .twitter_client import TwitterService
# Используем только get_translator, т.к. SettingsManager удален
from .translations import get_translator, get_available_languages

# Для TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .tasks import TasksCog

# --- Основная асинхронная функция ---


async def main():
    """Основная функция для инициализации и запуска бота."""

    # 1. Инициализация сервиса Twitter
    twitter_service = TwitterService(CONFIG['TWITTER_BEARER_TOKEN'])

    # 2. Получение функции-переводчика (использует язык по умолчанию)
    _ = get_translator()

    if twitter_service.init_failed:
        log.critical(_("CRITICAL_TWITTER_INIT_FAIL"))
        # sys.exit("Критическая ошибка: Не удалось инициализировать Twitter клиент.")

    # 3. Настройка намерений (Intents) Discord
    intents = discord.Intents.default()
    # Убираем ненужный интент
    # intents.message_content = True # <- Убрали
    intents.guilds = True       # Нужен для получения информации о канале

    # 4. Создание экземпляра бота
    bot = commands.Bot(
        command_prefix="!",  # Префикс не используется, но должен быть
        intents=intents,
        help_command=None
    )

    # !!! Сохраняем зависимости в боте !!!
    bot.twitter_service = twitter_service
    bot.translator_func = _
    bot.config = CONFIG

    # --- Обработчики событий бота ---
    @bot.event
    async def on_ready():
        """Вызывается, когда бот успешно подключился и готов к работе."""
        log.info(_("BOT_READY", bot_name=bot.user.name, bot_id=bot.user.id))

        tasks_cog: Optional['TasksCog'] = bot.get_cog("Hashtag Monitor")

        if tasks_cog:
            if not tasks_cog.twitter_service.init_failed:
                if not tasks_cog.check_hashtags.is_running():
                    log.info("Запуск фоновой задачи мониторинга хештегов...")
                    tasks_cog.check_hashtags.start()
                else:
                    log.info("Фоновая задача мониторинга хештегов уже запущена.")
            else:
                log.warning(
                    "Ког задач загружен, но Twitter сервис не инициализирован. Задача не будет запущена.")
        else:
            log.error("Не удалось найти ког 'Hashtag Monitor' для запуска цикла.")

    # 5. Загрузка когов (только TasksCog)
    async with bot:
        try:
            log.info("Загрузка кога задач...")
            await bot.load_extension('bot.tasks')  # Загружаем ТОЛЬКО ког задач
            # Убрали строку: await bot.load_extension('bot.commands')
            log.info("Ког задач успешно загружен.")
        # Обработчики ошибок загрузки когов
        except commands.ExtensionNotFound as e:
            log.exception(f"Ошибка: Ког не найден - {e}")
            await bot.close()
            return
        except commands.ExtensionAlreadyLoaded:
            log.warning("Попытка повторной загрузки кога.")
        except commands.NoEntryPointError as e:
            log.exception(f"Ошибка: В коге отсутствует функция setup - {e}")
            await bot.close()
            return
        except commands.ExtensionFailed as e:
            log.exception(
                f"Ошибка при инициализации кога '{e.name}': {e.original}")
            await bot.close()
            return
        except Exception as e:
            log.exception(f"Неожиданная ошибка при загрузке когов: {e}")
            await bot.close()
            return

        # 6. Запуск бота
        log.info(_("BOT_START_SUCCESS"))
        try:
            await bot.start(CONFIG['TOKEN'])
        except discord.errors.LoginFailure:
            log.critical(_("CRITICAL_LOGIN_FAIL"))
            sys.exit("Критическая ошибка: Неверный токен Discord.")
        except Exception as e:
            log.critical(_("CRITICAL_GENERIC_FAIL"))
            log.exception(e)
            sys.exit(f"Критическая ошибка при запуске бота: {e}")

# --- Точка входа ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Бот остановлен вручную (KeyboardInterrupt).")
    except Exception as e:
        print(
            f"Фатальная ошибка вне цикла событий asyncio: {e}", file=sys.stderr)
        traceback.print_exc()
