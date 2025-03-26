#!/bin/bash
set -e

PROJECT_DIR="futures_crm_fastapi"
if [ -d "$PROJECT_DIR" ]; then
  echo "Directory '$PROJECT_DIR' already exists. Remove it or choose another name."
  exit 1
fi

echo "Создаём структуру проекта FastAPI..."
mkdir -p "$PROJECT_DIR/app/templates/partials"
mkdir -p "$PROJECT_DIR/app/templates/registration"
mkdir -p "$PROJECT_DIR/app/static/css"
mkdir -p "$PROJECT_DIR/app/static/js"

# Создаем __init__.py
touch "$PROJECT_DIR/app/__init__.py"

echo "Создаём файлы проекта..."

# app/main.py
cat > "$PROJECT_DIR/app/main.py" <<'EOF'
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine, Base
from app import models, auth, routes

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(routes.router, prefix="", tags=["dashboard"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
EOF

# app/database.py
cat > "$PROJECT_DIR/app/database.py" <<'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./db.sqlite3"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# app/models.py
cat > "$PROJECT_DIR/app/models.py" <<'EOF'
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base
from datetime import datetime

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    symbol = Column(String, index=True)
    type = Column(String, index=True)  # LONG/SHORT
    entry_price = Column(Numeric(15, 2))
    current_price = Column(Numeric(15, 2), nullable=True)
    quantity = Column(Numeric(20, 8))
    leverage = Column(Integer, default=1)
    pnl = Column(Numeric(15, 2), default=0)
    pnl_percentage = Column(Numeric(5, 2), default=0)
    status = Column(String, default="OPEN")  # OPEN/CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Trade {self.symbol} {self.type}>"
EOF

# app/auth.py
cat > "$PROJECT_DIR/app/auth.py" <<'EOF'
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime

router = APIRouter()
fake_users_db = {}

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return request.app.state.templates.get_template("registration/login.html").render({"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    user = fake_users_db.get(username)
    if user and user["password"] == password:
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie("user", username)
        return response
    return request.app.state.templates.get_template("registration/login.html").render({"request": request, "error": "Неверный логин или пароль"})

@router.get("/signup", response_class=HTMLResponse)
async def signup_get(request: Request):
    return request.app.state.templates.get_template("registration/signup.html").render({"request": request})

@router.post("/signup", response_class=HTMLResponse)
async def signup_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in fake_users_db:
        return request.app.state.templates.get_template("registration/signup.html").render({"request": request, "error": "Пользователь уже существует"})
    fake_users_db[username] = {"username": username, "password": password, "created": datetime.utcnow()}
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie("user", username)
    return response
EOF

# app/routes.py
cat > "$PROJECT_DIR/app/routes.py" <<'EOF'
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import json

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
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
    trades = db.query(models.Trade).limit(5).all()
    return request.app.state.templates.get_template("dashboard.html").render({
        "request": request,
        "pnl_json": json.dumps(pnl_data),
        "trades": trades
    })
EOF

# app/templates/base.html
cat > "$PROJECT_DIR/app/templates/base.html" <<'EOF'
{% raw %}{% load static %}{% endraw %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FuturesTradeMate</title>
  <link href="/static/css/output.css" rel="stylesheet">
</head>
<body class="bg-background text-foreground">
  {% include 'partials/navbar.html' %}
  <main class="pt-16">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
EOF

# app/templates/partials/navbar.html
cat > "$PROJECT_DIR/app/templates/partials/navbar.html" <<'EOF'
<div class="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
  <div class="container mx-auto px-4 h-16 flex items-center justify-between">
    <a href="/" class="text-lg font-semibold">FuturesTradeMate</a>
    <nav class="hidden md:flex space-x-8">
      <a href="/" class="text-sm font-medium hover:text-foreground">Dashboard</a>
      <a href="/trades/" class="text-sm font-medium hover:text-foreground">Trades</a>
    </nav>
    <div class="flex items-center space-x-4">
      <a href="/auth/login" class="text-sm font-medium hover:text-foreground">Login</a>
      <a href="/auth/signup" class="text-sm font-medium hover:text-foreground">Signup</a>
    </div>
  </div>
</div>
EOF

# app/templates/dashboard.html
cat > "$PROJECT_DIR/app/templates/dashboard.html" <<'EOF'
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
            callback: function(value) { return '$' + value; }
          }
        }
      }
    }
  });
</script>
{% endblock %}
EOF

# app/static/css/variables.css
cat > "$PROJECT_DIR/app/static/css/variables.css" <<'EOF'
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

# app/static/css/tailwind.css
cat > "$PROJECT_DIR/app/static/css/tailwind.css" <<'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@import "variables.css";
EOF

# requirements.txt
cat > "$PROJECT_DIR/requirements.txt" <<'EOF'
fastapi==0.95.1
uvicorn==0.22.0
sqlalchemy==2.0.19
jinja2==3.1.2
python-multipart==0.0.5
aiofiles==23.1.0
ccxt>=2.0.0
gunicorn==20.1.0
EOF

# .dockerignore
cat > "$PROJECT_DIR/.dockerignore" <<'EOF'
venv
EOF

# Dockerfile
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
CMD ["./venv/bin/python", "-m", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
EOF

# docker-compose.yml
cat > "$PROJECT_DIR/docker-compose.yml" <<'EOF'
version: '3.8'
services:
  web:
    build: .
    command: ./venv/bin/python -m gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - venv_data:/app/venv
    ports:
      - "8000:8000"
    depends_on:
      - redis
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
volumes:
  venv_data:
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

echo "Инициализируем npm (для Tailwind) и устанавливаем tailwindcss, postcss и autoprefixer..."
npm install -D tailwindcss postcss autoprefixer

cat > postcss.config.js <<'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

cat > tailwind.config.js <<'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/templates/**/*.html',
    './app/static/css/**/*.css'
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

cat > package.json <<'EOF'
{
  "name": "futures_crm",
  "version": "1.0.0",
  "scripts": {
    "build-css": "npx tailwindcss -i ./app/static/css/tailwind.css -o ./app/static/css/output.css",
    "dev-css": "npx tailwindcss -i ./app/static/css/tailwind.css -o ./app/static/css/output.css --watch"
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
echo "1) Для локального запуска (FastAPI) выполните:"
echo "   source venv/Scripts/activate (Windows) или source venv/bin/activate (Unix)"
echo "   uvicorn app.main:app --reload"
echo
echo "2) Для сборки Tailwind выполните (из каталога проекта):"
echo "   npm run build-css"
echo "   (или npm run dev-css для режима watch)"
echo
echo "3) Для запуска через Docker-compose выполните:"
echo "   docker-compose up --build"
echo "--------------------------------------------"
