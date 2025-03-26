FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей, если они нужны (например, для mysqlclient)
# RUN apt-get update && apt-get install -y --no-install-recommends default-libmysqlclient-dev build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# CMD ["flask", "run"] # Для разработки
# Используйте Gunicorn для более продакшен-готового варианта
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
