# services/kucoin/Dockerfile
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn requests python-dotenv python-kucoin
COPY app.py .
EXPOSE 8006
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8006"]
