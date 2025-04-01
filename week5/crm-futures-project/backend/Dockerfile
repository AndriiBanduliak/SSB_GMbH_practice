FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей, если они понадобятся
# Например, для mysqlclient (но мы используем mysql-connector-python):
# RUN apt-get update && apt-get install -y --no-install-recommends default-libmysqlclient-dev build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
# Убедимся, что pip обновлен
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
# Используем .dockerignore, чтобы исключить ненужное (venv, __pycache__, etc.)
COPY . .

EXPOSE 5000

# Используем Gunicorn для запуска (более продакшен-готовый вариант)
# Флаг --preload может помочь с производительностью, но иногда мешает при отладке
# Флаг --workers можно настроить (например, 2 * кол-во_ядер + 1)
# Флаг --log-level=debug для более подробных логов
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--log-level=info", "run:app"]
