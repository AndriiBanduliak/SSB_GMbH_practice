#!/bin/bash

# --- Script for setting up a Telegram bot project for IP information lookup ---

echo "This script will help set up the project structure for your Telegram bot."
echo "It will create the necessary files (.env, requirements.txt, ip_lookup.py, bot.py) and the project folder."
echo ""

# Prompt user for the desired project folder name
read -p "Enter the desired project folder name (e.g., telegram_ip_bot): " project_dir

# Prompt user for the bot token
read -p "Enter your Telegram Bot Token (obtained from BotFather): " bot_token

echo ""

# Check if a folder with this name already exists
if [ -d "$project_dir" ]; then
    echo "Error: Folder '$project_dir' already exists."
    echo "Please choose a different name or delete the existing folder."
    exit 1
fi

# Create the project folder
mkdir "$project_dir"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create folder '$project_dir'."
    exit 1
fi
echo "Project folder created: $project_dir"

# Change into the created folder
cd "$project_dir"
if [ $? -ne 0 ]; then
    echo "Error: Failed to change into folder '$project_dir'. Aborting."
    exit 1
fi

# Create the .env file and write the token
echo "Creating .env file and writing token..."
cat << EOF > .env
# .env file for Telegram Bot Token
# IMPORTANT: Add this file to your .gitignore!
BOT_TOKEN=$bot_token
EOF
echo ".env successfully created."

# Create the requirements.txt file
echo "Creating requirements.txt file..."
cat << EOF > requirements.txt
requests
python-telegram-bot
python-dotenv
EOF
echo "requirements.txt successfully created."

# Create the .gitignore file (useful when using Git)
echo "Creating .gitignore file..."
cat << EOF > .gitignore
# Ignore virtual environment directory
venv/
.venv/

# Ignore environment variables file
.env

# Ignore Python bytecode files
*.pyc
__pycache__/
EOF
echo ".gitignore successfully created."


# Create the ip_lookup.py file with the function code (comments already in English)
echo "Creating ip_lookup.py file..."
# Using 'EOF' in single quotes prevents interpretation of variables or escape sequences inside the Python code
cat << 'EOF' > ip_lookup.py
# ip_lookup.py
# This module contains the function to query IP information from ip-api.com

import requests
import json
import logging
from typing import Optional, Dict, Any

# Configure logging - the bot's main logging configuration will be used
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_ip_info_from_api(ip_address: Optional[str] = None) -> Dict[str, Any]:
    """
    Queries the ip-api.com service for information about an IP address.

    Args:
        ip_address: The IP address to look up. If None, the API will return
                    information for the IP address of the calling machine (the bot server).

    Returns:
        A dictionary containing the API response data and status.
        Returns {'status': 'success', 'data': {...}} on success.
        Returns {'status': 'error', 'message': 'Error description'} on failure.
    """
    base_url = "http://ip-api.com/json/"
    url = f"{base_url}{ip_address}" if ip_address else base_url

    headers = {
        'User-Agent': 'TelegramIPLookupBot/1.0 (Python)' # Identify your bot script
    }

    logging.debug(f"Querying API: {url} for IP: {ip_address if ip_address else 'caller IP'}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Check the 'status' field within the API response itself
        if data.get('status') == 'success':
            return {'status': 'success', 'data': data}
        else:
            # API returned an error status
            message = data.get('message', 'Unknown error from API')
            logging.warning(f"API returned error status for {ip_address}: {message}")
            return {'status': 'error', 'message': f"API error: {message}"}

    except requests.exceptions.Timeout:
        logging.error(f"API request timed out for {ip_address}")
        return {'status': 'error', 'message': "API request timed out."}
    except requests.exceptions.RequestException as e:
        logging.error(f"Network or HTTP error during API call for {ip_address}: {e}")
        return {'status': 'error', 'message': f"Network or HTTP error: {e}"}
    except json.JSONDecodeError:
         logging.error(f"API response was not valid JSON for {ip_address}")
         return {'status': 'error', 'message': "Invalid response from API."}
    except Exception as e:
         logging.error(f"An unexpected error occurred during API call for {ip_address}: {e}")
         return {'status': 'error', 'message': f"An unexpected error occurred: {e}"}
EOF
echo "ip_lookup.py successfully created."

# Create the bot.py file (comments already in English)
echo "Creating bot.py file..."
cat << 'EOF' > bot.py
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
EOF
echo "bot.py successfully created."

echo ""
echo "----------------------------------------------------"
echo "Project setup completed in folder: ./"$project_dir
echo "----------------------------------------------------"
echo "Next steps:"
echo ""
echo "1. Change into the project folder:"
echo "   cd \"$project_dir\""
echo ""
echo "2. Create a Python virtual environment:"
echo "   python -m venv venv"
echo ""
echo "3. Activate the virtual environment:"
echo "   # On Linux/macOS (Bash/Zsh):"
echo "   source venv/bin/activate"
echo "   # On Windows (Command Prompt):"
echo "   venv\\Scripts\\activate"
echo "   # On Windows (PowerShell):"
echo "   venv\\Scripts\\Activate.ps1"
echo ""
echo "4. Install the required Python libraries:"
echo "   pip install -r requirements.txt"
echo ""
echo "5. Your bot token has been written to the .env file. If you need to change it, edit the .env file."
echo ""
echo "6. Run the bot script:"
echo "   python bot.py"
echo ""
echo "Press Ctrl+C in the terminal window to stop the bot."
echo "If you are using Git, make sure the .env file is added to your .gitignore to avoid publishing the token."
echo "----------------------------------------------------"