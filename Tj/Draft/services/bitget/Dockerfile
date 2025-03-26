FROM python:3.9-slim
WORKDIR /app

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn requests python-dotenv loguru

# Копируем локальную библиотеку (папку python_bitget) в контейнер
COPY python_bitget /app/python_bitget

# Добавляем /app/python_bitget в PYTHONPATH, чтобы пакет pybitget стал топ-уровневым
ENV PYTHONPATH="/app/python_bitget:${PYTHONPATH}"

# Копируем файл приложения
COPY app.py .

EXPOSE 8004
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]
