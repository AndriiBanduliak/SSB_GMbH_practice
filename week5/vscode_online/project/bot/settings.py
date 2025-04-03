import json
import os
import logging
from .config import CONFIG, SERVER_SETTINGS_FILE  # Импортируем дефолтный язык и имя файла

log = logging.getLogger('discord_twitter_bot.settings')

class SettingsManager:
    """Класс для управления настройками серверов (язык и т.д.)."""
    def __init__(self, file_path=SERVER_SETTINGS_FILE, default_lang=CONFIG['DEFAULT_LANGUAGE']):
        self.file_path = file_path
        self.default_lang = default_lang
        self.server_settings = self._load_settings()

    def _load_settings(self):
        """Загружает настройки из JSON файла."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                log.info("Настройки серверов загружены из %s", self.file_path)
                return settings
            except json.JSONDecodeError:
                log.error("Ошибка декодирования JSON из %s. Файл может быть поврежден. Используются настройки по умолчанию.", self.file_path)
            except Exception:
                log.exception("Не удалось загрузить настройки серверов из %s. Используются настройки по умолчанию.", self.file_path)
        else:
            log.info("Файл настроек %s не найден, используются настройки по умолчанию.", self.file_path)
        return {} # Возвращаем пустой словарь в случае ошибки или отсутствия файла

    def _save_settings(self):
        """Сохраняет текущие настройки в JSON файл."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.server_settings, f, indent=4)
            log.debug("Настройки серверов сохранены в %s", self.file_path)
        except Exception:
            log.exception("Не удалось сохранить настройки серверов в %s.", self.file_path)

    def get_server_language(self, guild_id):
        """Получает язык для сервера или язык по умолчанию."""
        if guild_id:
            return self.server_settings.get(str(guild_id), {}).get("language", self.default_lang)
        return self.default_lang # Для DM или если guild_id не предоставлен

    def set_server_language(self, guild_id, lang_code):
        """Устанавливает язык для сервера и сохраняет настройки."""
        # Валидацию языка лучше проводить перед вызовом этого метода,
        # но можно добавить и сюда, если нужно.
        # from .translations import get_available_languages # Импорт внутри для избежания цикла
        # if lang_code not in get_available_languages():
        #    return False

        guild_id_str = str(guild_id)
        if guild_id_str not in self.server_settings:
            self.server_settings[guild_id_str] = {}
        self.server_settings[guild_id_str]["language"] = lang_code
        self._save_settings()
        log.info("Язык для сервера %s изменен на '%s'", guild_id_str, lang_code)
        return True

# Пример создания экземпляра менеджера настроек (обычно делается в main.py)
# settings_manager = SettingsManager()
