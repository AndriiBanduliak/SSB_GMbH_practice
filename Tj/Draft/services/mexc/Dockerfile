FROM python:3.9-slim

# Задаем переменную окружения TZ
ENV TZ=UTC

# Обновляем пакеты, устанавливаем build-essential и tzdata, настраиваем часовую зону, очищаем кеш apt
RUN apt-get update && \
    apt-get install -y build-essential tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install fastapi uvicorn requests python-dotenv

COPY app.py .

EXPOSE 8005

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8005"]
