# bot.py
# Main script for the Telegram IP lookup bot

import os
import logging
import sys
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file at the beginning
# This makes variables like BOT_TOKEN available via os.getenv()
load_dotenv()

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Import the IP lookup function from the ip_lookup module
from ip_lookup import get_ip_info_from_api


# Configure logging for the bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Optional: Enable logging for python-telegram-bot itself (useful for debugging connection issues)
# logging.getLogger("httpx").setLevel(logging.WARNING) # Suppress noisy http messages


# Handler for the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hello, {user.mention_html()}! Send me an IP address or hostname like `/ip 8.8.8.8` to get information about it.",
    )

# Handler for the /ip command
async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /ip command and performs the IP lookup."""
    args = context.args # Get arguments after the command

    if not args:
        await update.message.reply_text(
            "Please provide an IP address or hostname after the /ip command. "
            "Example: `/ip 8.8.8.8`"
        )
        return

    target_ip = args[0] # Take the first argument as the target IP

    # Basic validation for common IP formats (optional but good practice)
    # This is a very simple check, not full IP validation
    # You could add more robust validation here if needed
    # Example:
    # import re
    # ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    # if not ip_pattern.match(target_ip):
    #    await update.message.reply_text("Invalid IP format. Please provide a valid IP address.")
    #    return


    await update.message.reply_text(f"Looking up information for: {target_ip}...")

    # Call the IP lookup function
    # Note: The get_ip_info_from_api function makes a synchronous HTTP request.
    # For very high traffic bots, you might need to run this in a thread pool
    # or use an asynchronous HTTP client (like httpx) within the lookup function
    # to avoid blocking the event loop. For a simple bot, this is usually fine.
    try:
        # The API call should ideally not block the bot's event loop.
        # Since requests is synchronous, in a real production bot handling
        # many users, you'd run this in a thread pool:
        # loop = asyncio.get_event_loop()
        # result = await loop.run_in_executor(None, get_ip_info_from_api, target_ip)
        # For simplicity here, we call it directly, acknowledging it's blocking.
        result = get_ip_info_from_api(target_ip)

    except Exception as e:
         # Catch any unexpected errors during the call itself before result processing
         logging.error(f"Error calling get_ip_info_from_api for {target_ip}: {e}")
         await update.message.reply_text("An internal error occurred during the lookup.")
         return


    # Process the result
    if result['status'] == 'success':
        ip_data = result['data']
        # Format the success message
        # Use get() with default 'N/A' to handle potentially missing keys gracefully
        message = (
            f"--- IP Information for {ip_data.get('query', target_ip)} ---\n"
            f"🌍 Country: {ip_data.get('country', 'N/A')}\n"
            f"🏙️ City: {ip_data.get('city', 'N/A')}\n"
            f"🗺️ Region: {ip_data.get('regionName', 'N/A')}\n"
            f"📦 ZIP Code: {ip_data.get('zip', 'N/A')}\n"
            f"⌚ Timezone: {ip_data.get('timezone', 'N/A')}\n"
            f"📡 ISP: {ip_data.get('isp', 'N/A')}\n"
            f"🏢 Organization: {ip_data.get('org', 'N/A')}\n"
            f"🧭 Coordinates: Lat {ip_data.get('lat', 'N/A')}, Lon {ip_data.get('lon', 'N/A')}\n"
            "----------------------------------------------------------"
        )
        await update.message.reply_text(message)
    else:
        # Format the error message
        error_message = result.get('message', 'An unknown error occurred.')
        await update.message.reply_text(f"❌ Error looking up IP: {error_message}")
        # Add a note about rate limits if applicable
        if 'limit' in error_message.lower():
             await update.message.reply_text("You might have hit the API rate limit (45 requests/minute on the free tier). Try again in a minute.")


def main() -> None:
    """Starts the bot."""
    # Get the bot token from environment variables.
    # load_dotenv() has already loaded variables from .env into os.environ
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logging.error(".env file not loaded or BOT_TOKEN not set.")
        # Use print here as logging might not be fully set up if dotenv failed early
        print("\nFATAL ERROR: BOT_TOKEN not found.")
        print(f"Please make sure you have a .env file in the project directory ('{os.getcwd()}')")
        print("with the line:")
        print("BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN")
        print("Replace YOUR_TELEGRAM_BOT_TOKEN with your actual token.")
        sys.exit(1)

    # Create the Application and pass it your bot's token.
    # We enable 'concurrent_updates' with a worker limit if we were using
    # synchronous blocking calls in handlers in a production setting.
    # With just one blocking call in ip_command, default is okay for simple bots.
    application = Application.builder().token(bot_token).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ip", ip_command))

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    logging.info("Bot started. Listening for messages...")
    # Use run_polling for local development.
    # stop_signals=None makes it easier to stop with Ctrl+C across platforms.
    application.run_polling(poll_interval=3.0, stop_signals=None)
    logging.info("Bot stopped.")


if __name__ == "__main__":
    main()
