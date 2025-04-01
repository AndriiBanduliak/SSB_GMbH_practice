import discord
from discord.ext import commands
from bot.translations import translate
from bot.settings import set_server_language, get_server_language
from bot.twitter_client import get_user_id, get_tweets

bot = commands.Bot(command_prefix="!")

@bot.command(name="setlang", help="Legt die Sprache des Bots für diesen Server fest.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def setlang_command(ctx, lang_code: str):
    lang_code = lang_code.lower()
    available_langs = ", ".join(["de", "en"])
    if set_server_language(ctx.guild.id, lang_code):
        await ctx.send(translate("LANG_SET_SUCCESS", ctx.guild.id, lang=lang_code))
    else:
        await ctx.send(translate("LANG_SET_FAIL_INVALID", ctx.guild.id, available_langs=available_langs))

@bot.command(name="twitter", help="Zeigt die letzten Tweets eines Benutzers an.")
async def twitter_command(ctx, username: str, count: int = 5):
    guild_id = ctx.guild.id if ctx.guild else None
    await ctx.send(translate("SEARCHING_TWEETS", guild_id, count=count, username=username))
    user_id = await get_user_id(username)
    if not user_id:
        await ctx.send(translate("USER_NOT_FOUND", guild_id, username=username))
        return
    tweets = await get_tweets(user_id, count=count)
    if tweets:
        await ctx.send(translate("LAST_TWEETS_HEADER", guild_id, num_tweets=len(tweets), username=username))
        for tweet in tweets:
            tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
            embed = discord.Embed(description=tweet.text, color=discord.Color.blue())
            embed.set_author(name=f"@{username}", url=tweet_url, icon_url=ctx.author.display_avatar.url)
            embed.add_field(name=translate("TWEET_LINK_TEXT", guild_id), value=translate("TWEET_GOTO_LINK", guild_id, url=tweet_url), inline=False)
            if tweet.created_at:
                embed.timestamp = tweet.created_at
            await ctx.send(embed=embed)
    else:
        await ctx.send(translate("NO_TWEETS_FOUND", guild_id, username=username))

@bot.command(name="helpme", help="Zeigt diese Hilfenachricht an.")
async def helpme_command(ctx):
    guild_id = ctx.guild.id if ctx.guild else None
    embed = discord.Embed(title=translate("HELP_TITLE", guild_id), color=discord.Color.green())
    embed.add_field(name=translate("HELP_CMD_TWITTER_NAME", guild_id), value=translate("HELP_CMD_TWITTER_VALUE", guild_id), inline=False)
    embed.add_field(name=translate("HELP_CMD_SETLANG_NAME", guild_id), value=translate("HELP_CMD_SETLANG_VALUE", guild_id), inline=False)
    embed.add_field(name=translate("HELP_CMD_HELPME_NAME", guild_id), value=translate("HELP_CMD_HELPME_VALUE", guild_id), inline=False)
    current_lang = get_server_language(guild_id, "de")
    embed.add_field(name="---", value=translate("LANG_INFO", guild_id, lang=current_lang), inline=False)
    footer_text = translate("HELP_FOOTER_SERVER", guild_id, server_name=ctx.guild.name) if ctx.guild else translate("HELP_FOOTER_DM", guild_id)
    footer_text += f" | Bot ID: {bot.user.id}"
    embed.set_footer(text=footer_text)
    await ctx.send(embed=embed)
