
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*
ENV PYTHONPATH=/app
COPY backend/req.txt .
RUN pip install --upgrade pip && pip install -r req.txt
COPY backend /app/backend
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

