#!/usr/bin/env python
import psutil
import logging
import json
from pathlib import Path
import sys

# —————————————————————————————————————————————————————————
# Пути
base_dir = Path(__file__).parent
cfg_path = base_dir / 'config.json'
log_file = base_dir / 'antivirus.log'

# —————————————————————————————————————————————————————————
# Настройка логирования: вывод в консоль + файл
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)

# —————————————————————————————————————————————————————————
# Загрузка конфигурации
if not cfg_path.exists():
    logging.error(f'Не найден файл конфигурации: {cfg_path}')
    sys.exit(1)

try:
    cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
except json.JSONDecodeError as e:
    logging.error(f'Ошибка чтения конфигурации: {e}')
    sys.exit(1)

# Проверка наличия ключей
if 'keywords' not in cfg or 'whitelist' not in cfg:
    logging.warning("В конфигурации отсутствуют ключи 'keywords' или 'whitelist'. Используются пустые списки.")

suspicious = set(cfg.get('keywords', []))
whitelist = set(cfg.get('whitelist', []))

# —————————————————————————————————————————————————————————
def scan_processes():
    alerts = []
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'create_time']):
        try:
            name = (proc.info['name'] or '').lower()
            if any(kw in name for kw in suspicious) and name not in whitelist:
                alerts.append(proc.info)
        except psutil.NoSuchProcess:
            logging.debug(f'Процесс не существует: PID={proc.pid}')
        except psutil.AccessDenied:
            logging.debug(f'Доступ запрещен к процессу: PID={proc.pid}')
    return alerts

# —————————————————————————————————————————————————————————
if __name__ == '__main__':
    logging.info('Запуск сканера процессов')
    findings = scan_processes()

    if findings:
        logging.warning('Найдены подозрительные процессы:')
        for p in findings:
            logging.warning(f"PID={p['pid']} Name={p['name']} Path={p['exe']}")
        sys.exit(1)
    else:
        logging.info('Все процессы в порядке.')
        sys.exit(0)
