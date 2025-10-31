import logging
from bot.config import DISCORD_BOT_TOKEN
from bot.settings import load_settings
from bot.commands import bot
from bot.tasks import check_twitter

logging.basicConfig(level=logging.INFO)

def main():
    load_settings()
    
    @bot.event
    async def on_ready():
        logging.info("Бот %s (ID: %s) готов!", bot.user.name, bot.user.id)
        check_twitter.start()
    
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()
