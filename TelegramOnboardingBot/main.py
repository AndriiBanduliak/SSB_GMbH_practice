import logging
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, ChatJoinRequest as ChatJoinRequestFilter
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hlink # Для безопасного форматирования ссылок, хотя в HTML это тоже работает

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
# CHANNEL_ID should be an integer or string representation of integer
CHANNEL_ID_STR = os.getenv("CHANNEL_ID")
ADMIN_ID_STR = os.getenv("ADMIN_ID") # Add your Telegram User ID here

# Validate configuration
if not API_TOKEN:
    logging.error("API_TOKEN environment variable not set!")
    exit(1)
if not CHANNEL_ID_STR:
    logging.error("CHANNEL_ID environment variable not set!")
    exit(1)
try:
    CHANNEL_ID = int(CHANNEL_ID_STR)
except ValueError:
    logging.error("CHANNEL_ID must be an integer.")
    exit(1)
if not ADMIN_ID_STR:
     logging.warning("ADMIN_ID environment variable not set. Configuration commands will be disabled.")
     ADMIN_ID = None
else:
    try:
        ADMIN_ID = int(ADMIN_ID_STR)
    except ValueError:
        logging.error("ADMIN_ID must be an integer.")
        exit(1)


# --- Constants and Initial State ---
DEFAULT_WELCOME_MESSAGE = "Hello, {username}! Your request to join the channel has been received! ⏳ Please wait for approval."
# Using a dictionary to store configuration allows easy passing via dp.data
INITIAL_STATE = {
    'welcome_message': DEFAULT_WELCOME_MESSAGE,
    'buttons': [] # List of tuples (text, url)
}

# --- Helper Functions ---

def get_welcome_message_text(message_template: str, username: str) -> str:
    """Formats the welcome message template with the username."""
    return message_template.replace("{username}", username)

def create_inline_keyboard(buttons_data: list[tuple[str, str]]) -> InlineKeyboardMarkup | None:
    """Creates an inline keyboard from a list of (text, url) tuples."""
    if not buttons_data:
        return None

    keyboard = []
    row = []
    for i, (text, url) in enumerate(buttons_data):
        row.append(InlineKeyboardButton(text=text, url=url))
        # Add buttons to a row, max 2 buttons per row for cleaner look
        if len(row) == 2 or i == len(buttons_data) - 1:
            keyboard.append(row)
            row = []

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- Middlewares/Filters (Optional but good for complex logic) ---
# For a simple admin check, a filter lambda or function is sufficient

def is_admin(user_id: int) -> bool:
    """Checks if the given user ID is the configured admin."""
    return ADMIN_ID is not None and user_id == ADMIN_ID

# --- Handlers ---

@dp.chat_join_request(ChatJoinRequestFilter(chat_id=CHANNEL_ID))
async def handle_join_request(event: ChatJoinRequest, bot: Bot):
    """Handles chat join requests for the specified channel."""
    user_id = event.from_user.id
    username = event.from_user.first_name or f"user_{user_id}" # Use first name or a generic name

    # Get state from dispatcher data
    state = dp.data # Access data directly
    welcome_message_template = state.get('welcome_message', DEFAULT_WELCOME_MESSAGE)
    buttons_data = state.get('buttons', [])

    welcome_message = get_welcome_message_text(welcome_message_template, username)
    reply_keyboard = create_inline_keyboard(buttons_data)

    try:
        # Send a message to the user with buttons
        await bot.send_message(
            user_id,
            welcome_message,
            parse_mode=ParseMode.HTML, # Allow HTML in the welcome message
            reply_markup=reply_keyboard
        )
        logging.info(f"Sent welcome message to user {username} ({user_id}) for channel {event.chat.id}")

    except Exception as e:
        logging.warning(f"Error sending welcome message to user {user_id}: {e}")
        # Optionally inform admin about the failure

# --- Admin Commands ---

@dp.message(Command("edit"), lambda message: is_admin(message.from_user.id))
async def edit_welcome_message(message: types.Message):
    """Admin command to edit the welcome message template."""
    args = message.get_args()

    if not args:
        await message.reply(
            "Usage: /edit <new welcome message>\n"
            "Use {username} as a placeholder for the user's first name.\n"
            "HTML markup is supported (e.g., <a href='https://example.com'>Link text</a>)."
        )
        return

    # Update state
    dp.data['welcome_message'] = args
    await message.reply("Welcome message template updated!")
    logging.info(f"Welcome message updated by admin {message.from_user.id}")


@dp.message(Command("addbutton"), lambda message: is_admin(message.from_user.id))
async def add_button(message: types.Message):
    """Admin command to add a button to the welcome message."""
    args = message.get_args()

    if not args:
        await message.reply(
            "Usage: /addbutton <Button text> | <URL>\n"
            "Example: /addbutton Our channel | https://t.me/channel"
        )
        return

    try:
        button_text, button_url = args.split("|", 1) # Split only once
        button_text = button_text.strip()
        button_url = button_url.strip()

        if not button_text or not button_url:
             await message.reply("Invalid format. Both text and URL are required.")
             return

        # Add button to state
        dp.data['buttons'].append((button_text, button_url))
        await message.reply(f"Button '{button_text}' added!")
        logging.info(f"Button added by admin {message.from_user.id}: {button_text} -> {button_url}")

    except ValueError:
        await message.reply("Invalid format. Usage: /addbutton <Button text> | <URL>")


@dp.message(Command("clearbuttons"), lambda message: is_admin(message.from_user.id))
async def clear_buttons(message: types.Message):
    """Admin command to remove all buttons from the welcome message."""
    # Clear buttons in state
    dp.data['buttons'] = []
    await message.reply("All buttons have been removed!")
    logging.info(f"All buttons cleared by admin {message.from_user.id}")


@dp.message(Command("showbuttons"), lambda message: is_admin(message.from_user.id))
async def show_buttons(message: types.Message):
    """Admin command to show the current list of buttons."""
    buttons_data = dp.data.get('buttons', [])

    if not buttons_data:
        await message.reply("Button list is empty!")
        return

    buttons_list_text = "\n".join([f"📌 {text} -> {url}" for text, url in buttons_data])
    await message.reply(f"Current buttons:\n{buttons_list_text}")


# --- Main Execution ---

async def main():
    """Starts the bot and polling."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    logging.info("Starting bot...")

    # Initialize bot and dispatcher
    bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML) # Set default parse mode
    dp = Dispatcher()

    # Initialize state in dispatcher data
    dp.data.update(INITIAL_STATE)

    # Register handlers - they are already registered via decorators,
    # but you can also register them here if needed.

    # Set bot commands (optional but good UX)
    if ADMIN_ID is not None:
        admin_commands = [
            types.BotCommand(command="edit", description="Edit welcome message template"),
            types.BotCommand(command="addbutton", description="Add button (text | url)"),
            types.BotCommand(command="clearbuttons", description="Clear all buttons"),
            types.BotCommand(command="showbuttons", description="Show current buttons")
        ]
        try:
             await bot.set_my_commands(admin_commands, scope=types.BotCommandScopeChat(chat_id=ADMIN_ID))
             logging.info(f"Admin commands set for chat ID {ADMIN_ID}")
        except Exception as e:
             logging.warning(f"Could not set admin commands for chat ID {ADMIN_ID}: {e}")

    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logging.info("Bot stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot execution interrupted.")