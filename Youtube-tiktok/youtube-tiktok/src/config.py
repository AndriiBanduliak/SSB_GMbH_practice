# src/config.py
# Файл для хранения настроек, ключей API и путей.
# ВНИМАНИЕ: Чувствительные данные (ключи API) лучше хранить вне репозитория,
# например, в переменных окружения или .env файле, который добавлен в .gitignore.

import os

# --- YouTube API ---
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY") # Замените или используйте .env

# --- TikTok API/Selenium Settings ---
TIKTOK_USERNAME = os.environ.get("TIKTOK_USERNAME", "YOUR_TIKTOK_USERNAME")
TIKTOK_PASSWORD = os.environ.get("TIKTOK_PASSWORD", "YOUR_TIKTOK_PASSWORD") # Замените или используйте .env
# Или другие настройки для Selenium (путь к драйверу и т.д.)
# TIKTOK_SELENIUM_DRIVER_PATH = "/path/to/chromedriver"

# --- Пути к файлам/директориям ---
DOWNLOAD_DIR = "downloads"
PROCESSED_DIR = "processed"
ANALYTICS_DIR = "analytics"

# Создание директорий, если они не существуют
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(ANALYTICS_DIR, exist_ok=True)

# --- Настройки обработки видео ---
# Пример: Максимальная длительность Shorts (для TikTok)
MAX_SHORT_DURATION_SEC = 60

# --- Другие настройки ---
# Количество Shorts для поиска за один раз
FETCH_LIMIT = 10
# Интервал между публикациями (в часах)
PUBLISH_INTERVAL_HOURS = 4