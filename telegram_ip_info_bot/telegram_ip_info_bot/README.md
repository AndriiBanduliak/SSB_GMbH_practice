# Telegram IP Lookup Bot

**A simple Telegram bot that provides detailed information about an IP address or hostname.**

## Overview

This project creates a Telegram bot that allows users to send an IP address or hostname and receive back comprehensive information about it, including country, city, region, ISP, coordinates, and more.  The bot leverages the `ipify.org` API for real-time IP lookup.

## Prerequisites

*   **Python 3.7+:** Ensure you have Python 3.7 or higher installed on your system.
*   **Telegram Bot Token:** You'll need a Telegram bot token to create and run this bot.  You can obtain one from the [BotFather](https://t.me/BotFather).
*   **`.env` File:** A `.env` file is used to store sensitive information like your bot token.

## Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/[Your GitHub Username]/telegram-ip-lookup-bot.git
    cd telegram-ip-lookup-bot
    ```

2.  **Create a Virtual Environment (Recommended):** This isolates project dependencies and prevents conflicts.
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows (Command Prompt)
    venv\Scripts\Activate.ps1 # Windows (PowerShell)
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the `.env` File:** Create a file named `.env` in the project directory and add your Telegram bot token:
    ```
    BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
    ```
    Replace `YOUR_TELEGRAM_BOT_TOKEN` with the actual token you obtained from BotFather.

5.  **Run the Bot:**
    ```bash
    python bot.py
    ```

## Usage

1.  **Start the Bot:** Run the `bot.py` script as described above. The bot will start listening for commands in your Telegram chat.

2.  **Send a Command:** In your Telegram chat, send the following command:
    `/ip [IP Address or Hostname]`
    For example: `/ip 8.8.8.8` or `/ip google.com`

3.  **Receive Information:** The bot will respond with detailed information about the specified IP address or hostname.

## API Usage

This project uses the `ipify.org` API for IP lookup. You can find more details about their API at: [https://www.ipify.org/](https://www.ipify.org/)

## Contributing

We welcome contributions to this project!  Please follow these guidelines:

1.  **Fork the Repository:** Create a fork of this repository on GitHub.
2.  **Create a Branch:** Create a new branch for your feature or bug fix.
3.  **Make Changes:** Implement your changes and write clear, concise code.
4.  **Commit Your Changes:** Commit your changes with descriptive messages.
5.  **Submit a Pull Request:** Submit a pull request to the main repository.

## License

This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.

