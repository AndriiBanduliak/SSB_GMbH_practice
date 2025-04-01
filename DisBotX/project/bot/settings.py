import os
import json
import logging

log = logging.getLogger('settings')
SETTINGS_FILE = "server_settings.json"
server_settings = {}

def load_settings():
    global server_settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                server_settings = json.load(f)
        except Exception as e:
            log.exception("Ошибка загрузки настроек")
            server_settings = {}
    else:
        server_settings = {}

def save_settings():
    global server_settings
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(server_settings, f, indent=4)
    except Exception as e:
        log.exception("Ошибка сохранения настроек")

def get_server_language(guild_id, default_language):
    return server_settings.get(str(guild_id), {}).get("language", default_language)

def set_server_language(guild_id, lang_code):
    guild_id_str = str(guild_id)
    if guild_id_str not in server_settings:
        server_settings[guild_id_str] = {}
    server_settings[guild_id_str]["language"] = lang_code
    save_settings()
    return True
