#!/bin/bash
set -e

PROJECT_DIR="futures_crm"
if [ -d "$PROJECT_DIR" ]; then
  echo "Directory '$PROJECT_DIR' already exists. Remove or choose another name."
  exit 1
fi

echo "Создаём структуру проекта..."
mkdir -p "$PROJECT_DIR/futures_crm"
mkdir -p "$PROJECT_DIR/trading_app"
mkdir -p "$PROJECT_DIR/trading_app/templates/partials"
mkdir -p "$PROJECT_DIR/trading_app/templates/registration"
mkdir -p "$PROJECT_DIR/trading_app/static/css"
mkdir -p "$PROJECT_DIR/trading_app/static/js"

# Создаем __init__.py в нужных папках
touch "$PROJECT_DIR/futures_crm/__init__.py"
touch "$PROJECT_DIR/trading_app/__init__.py"

echo "Создаём файлы проекта..."

# Файл manage.py
cat > "$PROJECT_DIR/manage.py" <<'EOF'
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futures_crm.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)
EOF
chmod +x "$PROJECT_DIR/manage.py"

# futures_crm/settings.py
cat > "$PROJECT_DIR/futures_crm/settings.py" <<'EOF'
SECRET_KEY = 'changeme'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'trading_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'futures_crm.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['../trading_app/templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'futures_crm.wsgi.application'
ASGI_APPLICATION = 'futures_crm.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
EOF

# futures_crm/urls.py
cat > "$PROJECT_DIR/futures_crm/urls.py" <<'EOF'
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('trading_app.urls')),
]
EOF

# futures_crm/asgi.py
cat > "$PROJECT_DIR/futures_crm/asgi.py" <<'EOF'
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futures_crm.settings')
application = get_asgi_application()
EOF

# futures_crm/wsgi.py
cat > "$PROJECT_DIR/futures_crm/wsgi.py" <<'EOF'
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futures_crm.settings')
application = get_wsgi_application()
EOF

# futures_crm/routing.py
cat > "$PROJECT_DIR/futures_crm/routing.py" <<'EOF'
# Placeholder routing for Channels
from channels.routing import ProtocolTypeRouter
application = ProtocolTypeRouter({
    # "websocket": ...
})
EOF

# trading_app/models.py
cat > "$PROJECT_DIR/trading_app/models.py" <<'EOF'
from django.db import models
from django.contrib.auth.models import User

class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    symbol = models.CharField(max_length=50)
    type = models.CharField(max_length=5)  # LONG/SHORT
    entry_price = models.DecimalField(max_digits=15, decimal_places=2)
    current_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    leverage = models.PositiveIntegerField(default=1)
    pnl = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pnl_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=6, default='OPEN')  # OPEN/CLOSED
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} ({self.type})"
EOF

# trading_app/views.py
cat > "$PROJECT_DIR/trading_app/views.py" <<'EOF'
import json
from django.shortcuts import render
from .models import Trade

def dashboard(request):
    pnl_data = [
        {"date": "Jan", "value": 1000},
        {"date": "Feb", "value": 1200},
        {"date": "Mar", "value": 900},
        {"date": "Apr", "value": 1500},
        {"date": "May", "value": 2000},
        {"date": "Jun", "value": 1800},
        {"date": "Jul", "value": 2200},
        {"date": "Aug", "value": 2600},
        {"date": "Sep", "value": 2400},
        {"date": "Oct", "value": 2800},
        {"date": "Nov", "value": 3500},
        {"date": "Dec", "value": 3800},
    ]
    context = {
        "pnl_json": json.dumps(pnl_data),
        "trades": Trade.objects.all()[:5],
    }
    return render(request, "dashboard.html", context)
EOF

# trading_app/urls.py
cat > "$PROJECT_DIR/trading_app/urls.py" <<'EOF'
from django.urls import path
from .views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
]
EOF

# trading_app/consumers.py
cat > "$PROJECT_DIR/trading_app/consumers.py" <<'EOF'
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({'echo': data}))
EOF

# trading_app/templates/base.html (с {% load static %})
cat > "$PROJECT_DIR/trading_app/templates/base.html" <<'EOF'
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FuturesTradeMate</title>
  <link href="{% static 'css/output.css' %}" rel="stylesheet">
</head>
<body class="bg-background text-foreground">
  {% include 'partials/navbar.html' %}
  <main class="pt-16">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
EOF

# trading_app/templates/partials/navbar.html
cat > "$PROJECT_DIR/trading_app/templates/partials/navbar.html" <<'EOF'
<div class="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
  <div class="container mx-auto px-4 h-16 flex items-center justify-between">
    <a href="/" class="text-lg font-semibold">FuturesTradeMate</a>
    <nav class="hidden md:flex space-x-8">
      <a href="/" class="text-sm font-medium hover:text-foreground">Dashboard</a>
      <a href="/trades/" class="text-sm font-medium hover:text-foreground">Trades</a>
    </nav>
    <div class="flex items-center space-x-4">
      <a href="/accounts/login/" class="text-sm font-medium hover:text-foreground">Login</a>
      <a href="/accounts/signup/" class="text-sm font-medium hover:text-foreground">Signup</a>
    </div>
  </div>
</div>
EOF

# trading_app/templates/dashboard.html
cat > "$PROJECT_DIR/trading_app/templates/dashboard.html" <<'EOF'
{% extends 'base.html' %}
{% block content %}
<div class="container mx-auto px-4 py-8 space-y-6">
  <h2 class="text-2xl font-bold tracking-tight">Dashboard</h2>
  <div>
    <canvas id="pnlChart" class="h-64 w-full"></canvas>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  const pnlData = JSON.parse('{{ pnl_json|escapejs }}');
  const ctx = document.getElementById('pnlChart').getContext('2d');
  const labels = pnlData.map(item => item.date);
  const dataValues = pnlData.map(item => item.value);
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'PnL',
        data: dataValues,
        borderColor: 'hsl(var(--primary))',
        backgroundColor: 'rgba(59,130,246,0.2)',
        fill: true
      }]
    },
    options: {
      scales: {
        y: {
          ticks: {
            callback: function(value) {
              return '$' + value;
            }
          }
        }
      }
    }
  });
</script>
{% endblock %}
EOF

# trading_app/static/css/variables.css
cat > "$PROJECT_DIR/trading_app/static/css/variables.css" <<'EOF'
:root {
  --background: 210, 20%, 98%;
  --foreground: 210, 20%, 10%;
  --border: 210, 10%, 85%;
  --primary: 226, 70%, 55%;
  --card: 210, 20%, 95%;
  --card-foreground: 210, 20%, 10%;
}

.dark {
  --background: 210, 20%, 10%;
  --foreground: 210, 20%, 96%;
  --border: 210, 5%, 30%;
  --card: 210, 15%, 15%;
  --card-foreground: 210, 20%, 96%;
  --primary: 226, 70%, 55%;
}
EOF

# trading_app/static/css/tailwind.css
cat > "$PROJECT_DIR/trading_app/static/css/tailwind.css" <<'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@import "variables.css";
EOF

# requirements.txt
cat > "$PROJECT_DIR/requirements.txt" <<'EOF'
Django==4.2
channels==4.0
redis==4.5.0
ccxt>=2.0.0
django-tailwind==2.2.0
django-allauth==0.51.0
gunicorn==20.1.0
EOF

# .dockerignore чтобы не монтировать локальный venv
cat > "$PROJECT_DIR/.dockerignore" <<'EOF'
venv
EOF

# Dockerfile (Linux)
cat > "$PROJECT_DIR/Dockerfile" <<'EOF'
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
CMD ["./venv/bin/gunicorn", "futures_crm.wsgi:application", "--bind", "0.0.0.0:8000"]

EOF

# docker-compose.yml
cat > "$PROJECT_DIR/docker-compose.yml" <<'EOF'
version: '3.8'
services:
  web:
    build: .
    command: venv/bin/gunicorn futures_crm.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
EOF

echo "Переходим в каталог проекта: $PROJECT_DIR"
cd "$PROJECT_DIR"
echo "Содержимое текущей директории:"
ls -la

echo "Создаем виртуальное окружение и устанавливаем Python-зависимости..."
python -m venv venv

if [ -f "venv/Scripts/activate" ]; then
    echo "Используем Windows-путь для активации виртуального окружения."
    source venv/Scripts/activate
    PYTHON_BIN="venv/Scripts/python.exe"
else
    echo "Используем Unix-путь для активации виртуального окружения."
    source venv/bin/activate
    PYTHON_BIN="venv/bin/python"
fi

$PYTHON_BIN -m pip install --upgrade pip
$PYTHON_BIN -m pip install -r requirements.txt

echo "Выполняем миграции Django..."
python manage.py migrate

echo "Инициализируем npm (для Tailwind) и устанавливаем tailwindcss, postcss и autoprefixer..."
npm install -D tailwindcss postcss autoprefixer

# Создаем postcss.config.js
cat > postcss.config.js <<'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# Создаем tailwind.config.js
cat > tailwind.config.js <<'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './trading_app/templates/**/*.html',
    './trading_app/static/css/**/*.css'
  ],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        border: 'hsl(var(--border))',
        card: 'hsl(var(--card))',
        'card-foreground': 'hsl(var(--card-foreground))',
        primary: 'hsl(var(--primary))'
      }
    }
  },
  plugins: [],
}
EOF

# Обновляем package.json со скриптами для Tailwind
cat > package.json <<'EOF'
{
  "name": "futures_crm",
  "version": "1.0.0",
  "scripts": {
    "build-css": "node_modules/.bin/tailwindcss -i ./trading_app/static/css/tailwind.css -o ./trading_app/static/css/output.css",
    "dev-css": "node_modules/.bin/tailwindcss -i ./trading_app/static/css/tailwind.css -o ./trading_app/static/css/output.css --watch"
  },
  "devDependencies": {
    "tailwindcss": "^4.0.15",
    "postcss": "^8.5.3",
    "autoprefixer": "^10.4.21"
  }
}
EOF

echo "Проект создан!"
echo "--------------------------------------------"
echo "1) Для локального запуска (Python) выполните:"
echo "   source venv/Scripts/activate (Windows) или source venv/bin/activate (Unix)"
echo "   python manage.py runserver"
echo
echo "2) Для сборки Tailwind выполните (из папки $PROJECT_DIR):"
echo "   npm run build-css"
echo "   (или npm run dev-css для режима watch)"
echo
echo "3) Для запуска через Docker-compose выполните:"
echo "   docker-compose up --build"
echo "--------------------------------------------"
