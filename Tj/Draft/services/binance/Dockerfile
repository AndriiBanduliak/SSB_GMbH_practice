FROM python:3.9-slim
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn python-binance==1.0.15 requests==2.31.0 python-dotenv
COPY app.py .
EXPOSE 8001
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
