import discord
from discord.ext import commands
import logging
from typing import TYPE_CHECKING, Optional # Добавлено Optional

# Используем TYPE_CHECKING для избежания цикличных импортов при проверке типов
if TYPE_CHECKING:
    from .twitter_client import TwitterService
    from .settings import SettingsManager
    # Функция get_translator больше не нужна для импорта здесь

log = logging.getLogger('discord_twitter_bot.commands')

class CommandsCog(commands.Cog, name="Основные команды"):
    """Ког, содержащий основные команды бота."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Получаем зависимости из атрибутов бота
        # Добавляем аннотации типов для подсказок IDE
        self.twitter_service: 'TwitterService' = getattr(bot, 'twitter_service', None)
        self.settings_manager: 'SettingsManager' = getattr(bot, 'settings_manager', None)
        self._ = getattr(bot, 'translator_func', lambda key, **kwargs: key) # Функция перевода или заглушка
        from .translations import get_available_languages # Импортируем здесь
        self.available_langs = get_available_languages()

        # Проверка, что зависимости были переданы
        if not self.twitter_service:
            log.error("CommandsCog: TwitterService не найден в атрибутах бота!")
        if not self.settings_manager:
            log.error("CommandsCog: SettingsManager не найден в атрибутах бота!")

        log.info("Ког команд инициализирован.")

    # --- Команда !setlang ---
    @commands.command(name="setlang")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def setlang_command(self, ctx: commands.Context, lang_code: str):
        """Устанавливает язык бота для текущего сервера."""
        # Проверяем наличие settings_manager на всякий случай
        if not self.settings_manager:
            log.error("setlang_command: SettingsManager недоступен.")
            await ctx.send("Ошибка: Сервис настроек не инициализирован.")
            return

        guild_id = ctx.guild.id
        lang_code = lang_code.lower()
        available_langs_str = ", ".join(f"`{code}`" for code in self.available_langs)

        if lang_code not in self.available_langs:
            await ctx.send(self._("LANG_SET_FAIL_INVALID", guild_id, available_langs=available_langs_str))
            return

        if self.settings_manager.set_server_language(guild_id, lang_code):
            await ctx.send(self._("LANG_SET_SUCCESS", guild_id, lang=lang_code))
            log.info("Язык для сервера %d (%s) изменен на '%s' пользователем %s (%d)",
                     guild_id, ctx.guild.name, lang_code, ctx.author.name, ctx.author.id)
        else:
             await ctx.send(self._("ERROR_UNEXPECTED_COMMAND", guild_id)) # Общая ошибка сохранения

    @setlang_command.error
    async def setlang_command_error(self, ctx: commands.Context, error):
        """Обработчик ошибок для команды !setlang."""
        guild_id = ctx.guild.id if ctx.guild else None
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(self._("LANG_SET_FAIL_PERMISSIONS", guild_id))
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(self._("LANG_SET_FAIL_DM", None))
        elif isinstance(error, commands.MissingRequiredArgument):
             available_langs_str = ", ".join(f"`{code}`" for code in self.available_langs)
             await ctx.send(self._("LANG_SET_FAIL_INVALID", guild_id, available_langs=available_langs_str))
        else:
            # Логируем как ошибку CheckFailure, если она не была обработана в on_command_error
            if not isinstance(error, commands.CheckFailure):
                 log.error("Неожиданная ошибка в команде setlang для сервера %s: %s", guild_id, error, exc_info=error)
                 await ctx.send(self._("ERROR_UNEXPECTED_COMMAND", guild_id))
            # CheckFailure уже логируется и обрабатывается в on_command_error

    # --- Команда !twitter ---
    @commands.command(name="twitter")
    async def twitter_command(self, ctx: commands.Context, username: str, count: int = 5):
        """Показывает последние твиты указанного пользователя Twitter."""
        # Проверяем наличие twitter_service
        if not self.twitter_service:
            log.error("twitter_command: TwitterService недоступен.")
            await ctx.send("Ошибка: Сервис Twitter не инициализирован.")
            return

        guild_id = ctx.guild.id if ctx.guild else None

        if self.twitter_service.init_failed:
            await ctx.send(self._("TWITTER_INACTIVE", guild_id))
            return

        count = max(1, min(25, count))

        try:
            processing_msg = await ctx.send(self._("SEARCHING_TWEETS", guild_id, count=count, username=username))
        except discord.Forbidden:
             log.warning(f"Нет прав на отправку сообщения в канале {ctx.channel.id} ({ctx.channel.name}) сервера {ctx.guild.name if ctx.guild else 'DM'}")
             return
        except Exception as e:
            log.error(f"Ошибка отправки 'searching' сообщения: {e}")
            processing_msg = None

        # Используем await для асинхронных методов сервиса
        user_id = await self.twitter_service.get_user_id_v2(username)
        if not user_id:
            error_message = self._("USER_NOT_FOUND", guild_id, username=username)
            try:
                if processing_msg: await processing_msg.edit(content=error_message)
                else: await ctx.send(error_message)
            except (discord.NotFound, discord.Forbidden): pass # Игнорируем ошибки редактирования/отправки здесь
            return

        tweets = await self.twitter_service.get_tweets_v2(user_id, count=count)

        if tweets is None:
             error_message = self._("NO_TWEETS_FOUND", guild_id, username=username)
             try:
                 if processing_msg: await processing_msg.edit(content=error_message)
                 else: await ctx.send(error_message)
             except (discord.NotFound, discord.Forbidden): pass
             return

        if not tweets:
            message = self._("NO_TWEETS_FOUND", guild_id, username=username)
            try:
                if processing_msg: await processing_msg.edit(content=message)
                else: await ctx.send(message)
            except (discord.NotFound, discord.Forbidden): pass
            return

        if processing_msg:
            try:
                await processing_msg.delete()
            except (discord.NotFound, discord.Forbidden): pass

        await ctx.send(self._("LAST_TWEETS_HEADER", guild_id, num_tweets=len(tweets), username=username))

        for tweet in tweets:
            tweet_url = f"https://twitter.com/{username}/status/{tweet['id']}"
            embed = discord.Embed(description=tweet['text'], color=discord.Color.blue())
            icon_url = ctx.author.display_avatar.url if ctx.author.display_avatar else None
            embed.set_author(name=f"@{username}", url=tweet_url, icon_url=icon_url)
            embed.add_field(name=self._("TWEET_LINK_TEXT", guild_id), value=self._("TWEET_GOTO_LINK", guild_id, url=tweet_url), inline=False)
            if tweet.get('created_at'):
                embed.timestamp = tweet['created_at']

            try:
                await ctx.send(embed=embed)
            except discord.Forbidden:
                 err_msg = self._("ERROR_FORBIDDEN_SEND", guild_id, channel_name=ctx.channel.name, channel_id=ctx.channel.id, server_name=ctx.guild.name if ctx.guild else "DM")
                 log.error(f"Нет прав на отправку embed в канале {ctx.channel.id}. Отправка твитов прервана. {err_msg}")
                 try:
                     await ctx.send(err_msg) # Сообщаем пользователю
                 except discord.Forbidden: pass # Если даже это нельзя
                 break
            except Exception as e:
                 log.exception(f"Ошибка при отправке embed твита {tweet['id']}: {e}")

    # --- Команда !helpme ---
    @commands.command(name="helpme")
    async def helpme_command(self, ctx: commands.Context):
        """Показывает справочное сообщение со списком команд."""
        # Проверяем наличие settings_manager
        if not self.settings_manager:
            log.error("helpme_command: SettingsManager недоступен.")
            await ctx.send("Ошибка: Сервис настроек не инициализирован.")
            return

        guild_id = ctx.guild.id if ctx.guild else None
        # Используем self._ для доступа к переводчику
        current_lang = self.settings_manager.get_server_language(guild_id)

        embed = discord.Embed(title=self._("HELP_TITLE", guild_id), color=discord.Color.green())

        # Используем bot.get_command для проверки доступности команды
        if self.bot.get_command('twitter'):
             embed.add_field(name=self._("HELP_CMD_TWITTER_NAME", guild_id), value=self._("HELP_CMD_TWITTER_VALUE", guild_id), inline=False)
        if self.bot.get_command('setlang'):
             embed.add_field(name=self._("HELP_CMD_SETLANG_NAME", guild_id), value=self._("HELP_CMD_SETLANG_VALUE", guild_id), inline=False)
        if self.bot.get_command('helpme'):
            embed.add_field(name=self._("HELP_CMD_HELPME_NAME", guild_id), value=self._("HELP_CMD_HELPME_VALUE", guild_id), inline=False)

        embed.add_field(name="---", value=self._("LANG_INFO", guild_id, lang=current_lang), inline=False)

        footer_text = ""
        if ctx.guild:
            footer_text = self._("HELP_FOOTER_SERVER", guild_id, server_name=ctx.guild.name)
        else:
            footer_text = self._("HELP_FOOTER_DM", guild_id)
        if self.bot.user:
             footer_text += f" | Bot ID: {self.bot.user.id}"
        embed.set_footer(text=footer_text)

        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            log.error(f"Нет прав на отправку embed в канале {ctx.channel.id} для команды help.")
            try:
                 await ctx.send(f"Cannot send help embed (missing permissions). Current language: {current_lang}")
            except discord.Forbidden: pass

# Функция setup для загрузки кога ботом
async def setup(bot: commands.Bot):
    # Теперь зависимости передаются через bot в __init__
    await bot.add_cog(CommandsCog(bot))
    log.info("Ког CommandsCog успешно загружен.")