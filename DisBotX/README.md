## DisBotX — Discord Twitter Monitor Bot

DisBotX is a Discord bot that fetches and displays tweets from a specified Twitter/X account and offers basic multi-language support (German and English). It uses discord.py and Tweepy.

### Features
- Fetch recent tweets with `!twitter <username> [count]`
- Per-server language setting with `!setlang <de|en>`
- Simple help message with `!helpme`
- Periodic background task scaffold to track new tweets

### Requirements
- Python 3.12+
- Discord Bot Token
- Twitter/X API Bearer Token (v2)

### Setup
1) Clone the repository and create a virtual environment:
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

2) Install dependencies:
```bash
pip install -r requirements.txt
```

3) Configure environment variables:
```bash
cp .env.example .env    # or copy manually on Windows
# Fill in the values:
# DISCORD_BOT_TOKEN=...
# TWITTER_BEARER_TOKEN=...
# TARGET_DISCORD_CHANNEL_ID=...
# TWITTER_USER_TO_MONITOR=...
# KEYWORDS_TO_MONITOR=bitcoin, eth
# BOT_DEFAULT_LANGUAGE=en
```

4) Run the bot

Option A — from the `project` directory (recommended):
```bash
cd project
python -m bot.main
```

Option B — from repo root by adjusting PYTHONPATH for this run:
```bash
# Windows (PowerShell)
$env:PYTHONPATH = "project"; python -m bot.main

# Linux/macOS
PYTHONPATH=project python -m bot.main
```

### Commands
- `!twitter <username> [count]` — show recent tweets
- `!setlang <de|en>` — set server language (admin only)
- `!helpme` — show help

### Configuration Files
- `.env` — runtime secrets and IDs (not committed)
- `server_settings.json` — per-guild settings (auto-created)

### Development Notes
- Source package is at `project/bot`
- Logging writes to console; remove or change file handlers as needed
- Background task in `bot/tasks.py` is scaffolded for future implementation

### License
MIT

