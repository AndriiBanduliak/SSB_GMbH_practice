FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

COPY . /app/

RUN python -m venv venv && \
    venv/bin/pip install --upgrade pip && \
    venv/bin/pip install -r requirements.txt

EXPOSE 8000
CMD ["venv/bin/python", "-m", "gunicorn", "futures_crm.wsgi:application", "--bind", "0.0.0.0:8000"]
