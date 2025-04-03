import discord
from discord.ext import commands
import asyncio
import logging
import sys
import traceback
from typing import Optional # Добавлено для TYPE_CHECKING

# --- Импорты из нашего пакета ---
# Порядок важен: сначала config и logger
from .config import CONFIG, log # check_env_vars вызывается при импорте config
# Затем остальные компоненты
from .settings import SettingsManager
from .twitter_client import TwitterService
from .translations import get_translator, get_available_languages # Функции, не сам словарь

# Для TYPE_CHECKING, чтобы избежать реальных цикличных импортов
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .tasks import TasksCog # Импортируем тип кога для аннотации в on_ready

# --- Основная асинхронная функция ---
async def main():
    """Основная функция для инициализации и запуска бота."""

    # 1. Проверка переменных окружения (уже выполняется при импорте config)
    # check_env_vars()

    # 2. Инициализация менеджера настроек
    settings_manager = SettingsManager()

    # 3. Инициализация сервиса Twitter
    twitter_service = TwitterService(CONFIG['TWITTER_BEARER_TOKEN'])
    _ = get_translator(settings_manager) # Получаем переводчик до возможного выхода

    if twitter_service.init_failed:
         log.critical(_("CRITICAL_TWITTER_INIT_FAIL", None))
         # sys.exit("Критическая ошибка: Не удалось инициализировать Twitter клиент.") # Раскомментировать для выхода

    # 4. Получение функции-переводчика (уже сделано выше)

    # 5. Настройка намерений (Intents) Discord
    intents = discord.Intents.default()
    intents.guilds = True
    intents.messages = True
    intents.message_content = True

    # 6. Создание экземпляра бота
    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
        help_command=None
    )

    # !!! ДОБАВЬТЕ ЭТИ СТРОКИ: Сохраняем зависимости в боте !!!
    bot.settings_manager = settings_manager
    bot.twitter_service = twitter_service
    bot.translator_func = _
    bot.config = CONFIG # Добавим и конфиг, если нужен в когах напрямую

    # --- Обработчики событий бота ---
    @bot.event
    async def on_ready():
        """Вызывается, когда бот успешно подключился и готов к работе."""
        log.info(_("BOT_READY", None, bot_name=bot.user.name, bot_id=bot.user.id))
        log.info(_("BOT_AVAILABLE_LANGS", None, langs=", ".join(get_available_languages())))

        # !!! ЗАПУСК ЗАДАЧИ ИЗ КОГА !!!
        # Получаем ког по имени, указанному в классе TasksCog
        # Используем аннотацию типа для подсказок IDE
        tasks_cog: Optional['TasksCog'] = bot.get_cog("Фоновые задачи")

        if tasks_cog:
             # Проверяем инициализацию Twitter сервиса перед запуском
            if not tasks_cog.twitter_service.init_failed:
                # Убедимся, что задача не запущена дважды, если бот переподключался
                if not tasks_cog.check_twitter.is_running():
                    log.info(_("BOT_START_TWITTER_TASK", None))
                    tasks_cog.check_twitter.start()
                else:
                    log.info("Фоновая задача Twitter уже запущена.")
            else:
                 log.warning("Ког задач загружен, но Twitter сервис не инициализирован. Задача не будет запущена.")
        else:
            log.error("Не удалось найти ког 'Фоновые задачи' для запуска цикла.")

    @bot.event
    async def on_command_error(ctx: commands.Context, error):
        """Глобальный обработчик ошибок команд (если не обработаны в коге)."""
        guild_id = ctx.guild.id if ctx.guild else None
        # Получаем функцию перевода из бота
        translator = bot.translator_func

        if isinstance(error, commands.CommandNotFound):
            log.debug(f"Неизвестная команда: {ctx.message.content}")
            return
        elif isinstance(error, commands.CommandInvokeError):
            original_error = error.original
            log.exception(f"Ошибка при выполнении команды '{ctx.command.qualified_name}': {original_error}", exc_info=original_error)
            await ctx.send(translator("ERROR_UNEXPECTED_COMMAND", guild_id))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Не хватает аргумента: `{error.param.name}`. Используйте `{bot.command_prefix}helpme` для справки.")
        elif isinstance(error, commands.CheckFailure):
            # Обрабатываем здесь общие ошибки прав, если они не перехвачены в коге
            if isinstance(error, commands.MissingPermissions):
                 perms = ", ".join(error.missing_permissions)
                 await ctx.send(f"У вас нет необходимых прав для этой команды: `{perms}`")
                 log.warning(f"Пользователь {ctx.author} ({ctx.author.id}) попытался использовать команду '{ctx.command.qualified_name}', не имея прав: {perms}")
            elif isinstance(error, commands.NoPrivateMessage):
                 await ctx.send(translator("LANG_SET_FAIL_DM", None)) # Используем существующий перевод
                 log.warning(f"Пользователь {ctx.author} ({ctx.author.id}) попытался использовать команду '{ctx.command.qualified_name}' в ЛС.")
            else:
                 log.warning(f"Ошибка проверки для команды '{ctx.command.qualified_name}' пользователя {ctx.author}: {error}")
                 await ctx.send("Вы не можете использовать эту команду здесь или у вас недостаточно прав.")
        else:
            log.exception(f"Необработанная ошибка команды: {error}", exc_info=error)
            await ctx.send(translator("ERROR_UNEXPECTED_COMMAND", guild_id))


    # 7. Загрузка когов (модулей с командами и задачами)
    async with bot:
        try:
            log.info("Загрузка когов...")
            # Правильный способ загрузки когов (без доп. аргументов):
            await bot.load_extension('bot.commands') # Указываем путь к модулю
            await bot.load_extension('bot.tasks')    # Указываем путь к модулю
            log.info("Все коги успешно загружены.")
        except commands.ExtensionNotFound as e:
             log.exception(f"Ошибка: Ког не найден - {e}")
             await bot.close()
             return
        except commands.ExtensionAlreadyLoaded:
             log.warning("Попытка повторной загрузки кога.") # Может случиться при перезагрузке
        except commands.NoEntryPointError as e:
             log.exception(f"Ошибка: В коге отсутствует функция setup - {e}")
             await bot.close()
             return
        except commands.ExtensionFailed as e:
             # Ошибка внутри setup() или __init__() кога
             log.exception(f"Ошибка при инициализации кога '{e.name}': {e.original}")
             await bot.close()
             return
        except Exception as e:
             log.exception(f"Неожиданная ошибка при загрузке когов: {e}")
             await bot.close()
             return

        # 8. Запуск бота
        log.info(_("BOT_START_SUCCESS", None))
        try:
            await bot.start(CONFIG['TOKEN'])
        except discord.errors.LoginFailure:
            log.critical(_("CRITICAL_LOGIN_FAIL", None))
            sys.exit("Критическая ошибка: Неверный токен Discord.")
        except Exception as e:
            log.critical(_("CRITICAL_GENERIC_FAIL", None))
            log.exception(e)
            sys.exit(f"Критическая ошибка при запуске бота: {e}")


# --- Точка входа ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Бот остановлен вручную (KeyboardInterrupt).")
    except Exception as e:
        print(f"Фатальная ошибка вне цикла событий asyncio: {e}", file=sys.stderr)
        traceback.print_exc()