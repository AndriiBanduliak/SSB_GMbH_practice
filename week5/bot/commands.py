import discord
from discord.ext import commands
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .tasks import TasksCog # Импортируем ког задач

log = logging.getLogger('discord_twitter_bot.commands_test')

class TestCommandsCog(commands.Cog, name="Тестовые команды"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        log.info("Ког тестовых команд инициализирован.")

    @commands.command(name="testtask")
    @commands.is_owner() # Только владелец бота может запустить
    async def test_task_command(self, ctx: commands.Context):
        """Запускает один цикл задачи check_hashtags немедленно."""
        tasks_cog: Optional['TasksCog'] = self.bot.get_cog("Hashtag Monitor")
        if tasks_cog and tasks_cog.check_hashtags.is_running():
             # Если задача уже запущена циклом, вызовем ее логику напрямую
             # Не используем tasks_cog.check_hashtags() напрямую, т.к. он ждет loop
             # Лучше вызвать внутренний метод, если бы он был,
             # но для простоты пока просто сообщим.
             # В качестве альтернативы - перезапустим задачу.
             await ctx.send("Задача уже запущена. Перезапускаю для теста...")
             tasks_cog.check_hashtags.restart()
        elif tasks_cog:
            await ctx.send("Запускаю цикл задачи `check_hashtags` для теста...")
            try:
                # Запускаем основной метод цикла один раз
                # Это не стандартный способ, лучше бы иметь отдельную корутину
                # await tasks_cog.check_hashtags() # Не сработает так как это decorated method
                # Безопаснее всего просто перезапустить loop
                tasks_cog.check_hashtags.restart()
                await ctx.send("Задача перезапущена.")
            except Exception as e:
                await ctx.send(f"Ошибка при ручном запуске задачи: {e}")
                log.exception("Ошибка ручного запуска check_hashtags")
        else:
            await ctx.send("Не удалось найти ког 'Hashtag Monitor'.")

async def setup(bot: commands.Bot):
    await bot.add_cog(TestCommandsCog(bot))
    log.info("Ког TestCommandsCog успешно загружен.")