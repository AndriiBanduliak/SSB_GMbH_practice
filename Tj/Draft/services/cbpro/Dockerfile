FROM python:3.9-slim
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn cbpro==1.1.4 requests==2.13.0 python-dotenv cbpro
COPY app.py .
EXPOSE 8003
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
