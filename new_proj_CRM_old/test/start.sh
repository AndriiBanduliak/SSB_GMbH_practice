#!/bin/bash
set -e

# Создаём папку проекта и переходим в неё
PROJECT_DIR="crm-futures-project"
mkdir -p "$PROJECT_DIR"

# Переходим в папку проекта, создаём виртуальное окружение и активируем его
cd "$PROJECT_DIR"
python -m venv venv
source venv/Scripts/activate
cd ..


# Создаём базовую структуру директорий
mkdir -p "$PROJECT_DIR/backend/app/routes" "$PROJECT_DIR/backend/app/static" "$PROJECT_DIR/backend/app/templates" "$PROJECT_DIR/backend/migrations"
mkdir -p "$PROJECT_DIR/frontend/public" "$PROJECT_DIR/frontend/src/components" "$PROJECT_DIR/frontend/src/contexts" "$PROJECT_DIR/frontend/src/locales" "$PROJECT_DIR/frontend/src/services" "$PROJECT_DIR/frontend/src/styles"
mkdir -p "$PROJECT_DIR/db_init"

##############################
# Файл: .env
##############################
cat << 'EOF' > "$PROJECT_DIR/.env"
# Backend Configuration
SECRET_KEY='your_very_secret_complex_key_here' # Замените на надежный ключ!
FLASK_APP=run.py
FLASK_RUN_HOST=0.0.0.0
FLASK_DEBUG=1 # Установите 0 для продакшена

# Database Configuration
MYSQL_DATABASE=crm_db
MYSQL_USER=crm_user
MYSQL_PASSWORD=secret_password # Используйте надежный пароль
MYSQL_ROOT_PASSWORD=root_secret_password # Используйте надежный пароль
DATABASE_URL=mysql+mysqlconnector://crm_user:secret_password@db:3306/crm_db
EOF

##############################
# Файл: docker-compose.yml
##############################
cat << 'EOF' > "$PROJECT_DIR/docker-compose.yml"
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5001:5000" # Хост:Контейнер
    volumes:
      - ./backend:/app # Для разработки, чтобы изменения кода подхватывались
    env_file:
      - .env
    environment:
      - FLASK_APP=\${FLASK_APP}
      - FLASK_RUN_HOST=\${FLASK_RUN_HOST}
      - FLASK_DEBUG=\${FLASK_DEBUG}
      - DATABASE_URL=\${DATABASE_URL}
      - SECRET_KEY=\${SECRET_KEY}
    depends_on:
      - db
    networks:
      - crm_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "8080:80" # Хост:Контейнер (Nginx)
    depends_on:
      - backend
    networks:
      - crm_network

  db:
    image: mysql:8.0
    command: --default-authentication-plugin=mysql_native_password # Для совместимости со старыми драйверами
    environment:
      MYSQL_ROOT_PASSWORD: \${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: \${MYSQL_DATABASE}
      MYSQL_USER: \${MYSQL_USER}
      MYSQL_PASSWORD: \${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./db_init:/docker-entrypoint-initdb.d # Запуск init.sql при первом старте
    ports:
      - "3307:3306" # Опционально: для прямого доступа к БД с хоста
    networks:
      - crm_network

volumes:
  mysql_data:

networks:
  crm_network:
    driver: bridge
EOF

##############################
# Файл: db_init/init.sql
##############################
cat << 'EOF' > "$PROJECT_DIR/db_init/init.sql"
-- Создаем базу данных, если она не существует
CREATE DATABASE IF NOT EXISTS crm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Используем созданную базу данных
USE crm_db;

-- Создаем таблицу пользователей
-- В реальном проекте пароль должен храниться в виде хеша!
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL, -- Здесь будет храниться хеш пароля
    language VARCHAR(5) DEFAULT 'en',    -- 'en', 'de', 'ru'
    theme VARCHAR(10) DEFAULT 'light',   -- 'light', 'dark'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Можно добавить тестового пользователя (пароль 'password', нужно хешировать при регистрации)
-- INSERT INTO users (username, email, password_hash, language, theme) VALUES
-- ('testuser', 'test@example.com', 'hashed_password_here', 'en', 'light');

-- Добавьте другие таблицы по мере необходимости (clients, trades, etc.)
-- CREATE TABLE IF NOT EXISTS clients (...);
-- CREATE TABLE IF NOT EXISTS trades (...);
EOF

##############################
# Backend: Dockerfile
##############################
cat << 'EOF' > "$PROJECT_DIR/backend/Dockerfile"
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
EOF

##############################
# Backend: requirements.txt
##############################
cat << 'EOF' > "$PROJECT_DIR/backend/requirements.txt"
Flask>=2.0
Flask-SQLAlchemy>=2.5
Flask-Migrate>=3.0
Flask-Cors>=3.0 # Для разрешения запросов с фронтенда
python-dotenv>=0.19
mysql-connector-python>=8.0 # Драйвер MySQL
gunicorn>=20.1 # WSGI сервер
Werkzeug>=2.0 # Для хеширования паролей
EOF

##############################
# Backend: run.py
##############################
cat << 'EOF' > "$PROJECT_DIR/backend/run.py"
import os
from app import create_app, db
# from app.models import User # Раскомментируйте, если нужно работать с моделями здесь

# Загрузка переменных окружения из .env файла (Flask делает это автоматически, но для Gunicorn может быть полезно)
# from dotenv import load_dotenv
# load_dotenv()

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Создание контекста приложения для работы с БД вне запросов (например, для миграций)
# app_context = app.app_context()
# app_context.push()

# Команды для CLI (можно добавить `flask db init/migrate/upgrade`)
@app.shell_context_processor
def make_shell_context():
    return dict(db=db) # Добавьте User=User и т.д.

if __name__ == '__main__':
    # Не используйте app.run() в продакшене с Gunicorn
    # app.run(host='0.0.0.0', debug=app.config['DEBUG'])
    pass # Gunicorn запустит приложение через run:app
EOF

##############################
# Backend -> app: __init__.py
##############################
cat << 'EOF' > "$PROJECT_DIR/backend/app/__init__.py"
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import config # Импортируем словарь конфигураций

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    """Фабрика приложений."""
    app = Flask(__name__)
    app.config.from_object(config[config_name]) # Загружаем конфиг из config.py
    config[config_name].init_app(app) # Инициализация специфичная для конфига (если есть)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # Разрешаем CORS для /api

    # Регистрация Blueprints (маршрутов)
    from .routes.settings import settings_bp
    # from .routes.auth import auth_bp # Раскомментируйте, когда добавите аутентификацию

    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/health')
    def health_check():
        return "Backend OK", 200

    return app
EOF

##############################
# Backend -> app: config.py
##############################
cat << 'EOF' > "$PROJECT_DIR/backend/app/config.py"
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла, если он есть
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '..', '..', '.env') # Путь к .env в корне проекта
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Можно добавить другие общие настройки

    @staticmethod
    def init_app(app):
        pass # Пока ничего специфичного

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite') # Фоллбэк на SQLite для простоты

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # Добавьте здесь настройки для продакшена (логирование, и т.д.)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
EOF

##############################
# Backend -> app: models.py
##############################
cat << 'EOF' > "$PROJECT_DIR/backend/app/models.py"
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users' # Явно указываем имя таблицы
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    language = db.Column(db.String(5), default='en')
    theme = db.Column(db.String(10), default='light')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        # Возвращает словарь с данными пользователя (без пароля)
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'language': self.language,
            'theme': self.theme,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z'
        }

    def __repr__(self):
        return f'<User {self.username}>'

# Добавьте другие модели: Client, Trade, Account и т.д.
# class Client(db.Model): ...
EOF

##############################
# Backend -> app/routes: __init__.py
##############################
touch "$PROJECT_DIR/backend/app/routes/__init__.py"

##############################
# Backend -> app/routes: settings.py
##############################
cat << 'EOF' > "$PROJECT_DIR/backend/app/routes/settings.py"
from flask import Blueprint, request, jsonify
from .. import db
from ..models import User
# Добавьте импорт для аутентификации, когда она будет готова
# from flask_jwt_extended import jwt_required, get_jwt_identity

settings_bp = Blueprint('settings', __name__)

# Временный хардкод ID пользователя для примера
# В реальном приложении нужно получать ID из токена аутентификации
TEMP_USER_ID = 1

@settings_bp.route('/', methods=['GET'])
# @jwt_required() # Раскомментируйте после настройки JWT
def get_settings():
    # user_id = get_jwt_identity() # Получение ID из токена
    user_id = TEMP_USER_ID # Временный хардкод
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "language": user.language,
        "theme": user.theme
    }), 200

@settings_bp.route('/', methods=['PUT'])
# @jwt_required()
def update_settings():
    # user_id = get_jwt_identity()
    user_id = TEMP_USER_ID # Временный хардкод
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    updated = False
    if 'language' in data and data['language'] in ['en', 'de', 'ru']:
        user.language = data['language']
        updated = True
    if 'theme' in data and data['theme'] in ['light', 'dark']:
        user.theme = data['theme']
        updated = True

    if updated:
        try:
            db.session.commit()
            return jsonify({
                "message": "Settings updated successfully",
                "language": user.language,
                "theme": user.theme
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Failed to update settings", "error": str(e)}), 500
    else:
        return jsonify({"message": "No valid settings provided to update"}), 400

# Добавьте здесь эндпоинты для других настроек (профиль, уведомления и т.д.)
EOF

##############################
# Frontend: Dockerfile
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/Dockerfile"
# --- Stage 1: Build React App ---
FROM node:18-alpine as builder

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код приложения
COPY . .

# Собираем продакшен-билд
RUN npm run build

# --- Stage 2: Serve with Nginx ---
FROM nginx:1.21-alpine

# Копируем кастомную конфигурацию Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранные статические файлы из стадии builder
COPY --from=builder /app/build /usr/share/nginx/html

# Открываем порт 80
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
EOF

##############################
# Frontend: nginx.conf
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/nginx.conf"
server {
    listen 80;
    server_name localhost; # Или ваш домен

    root /usr/share/nginx/html;
    index index.html index.htm;

    # Обработка статических файлов React
    location / {
        try_files \$uri /index.html;
    }

    # Проксирование API запросов на бэкенд
    location /api {
        # Важно: 'backend' - это имя сервиса в docker-compose.yml
        proxy_pass http://backend:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Опционально: обработка ошибок
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

##############################
# Frontend: package.json
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/package.json"
{
  "name": "crm-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "axios": "^1.0.0",
    "i18next": "^22.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-i18next": "^12.0.0",
    "react-router-dom": "^6.4.0",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "overrides": {
    "nth-check": "^2.0.1",
    "postcss": "^8.4.31"
  },
  "proxy": "http://localhost:5001"
}
EOF

##############################
# Frontend: public/index.html (пустой базовый HTML)
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/public/index.html"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CRM Futures Project</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
EOF

##############################
# Frontend: src/index.js
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/index.js"
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { ThemeProvider } from './contexts/ThemeContext';
import { LanguageProvider } from './contexts/LanguageContext';
import './i18n'; // Инициализация i18next
import './styles/global.css'; // Глобальные стили

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <LanguageProvider>
          <App />
        </LanguageProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);
EOF

##############################
# Frontend: src/App.js
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/App.js"
import React, { useContext } from 'react';
import { Routes, Route, Link, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ThemeContext } from './contexts/ThemeContext';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
// import LoginPage from './pages/LoginPage'; // Импортируйте страницы, когда они будут

function App() {
  const { theme } = useContext(ThemeContext);
  const { t } = useTranslation();

  // Простая проверка аутентификации (замените на реальную логику)
  const isAuthenticated = true; // Placeholder

  // Применяем класс темы к body
  React.useEffect(() => {
    document.body.className = theme; // 'light' или 'dark'
  }, [theme]);

  return (
    <div className={\`app-container \${theme}\`}>
      {/* Простая навигация для примера */}
      {isAuthenticated && (
        <nav>
          <ul>
            <li><Link to="/dashboard">{t('navigation.dashboard')}</Link></li>
            <li><Link to="/settings">{t('navigation.settings')}</Link></li>
          </ul>
          {/* Кнопка смены темы для демонстрации */}
          {/* <button onClick={toggleTheme}>Toggle Theme</button> */}
        </nav>
      )}

      <main>
        <Routes>
          {/* <Route path="/login" element={<LoginPage />} /> */}
          <Route
            path="/dashboard"
            element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/settings"
            element={isAuthenticated ? <Settings /> : <Navigate to="/login" replace />}
          />
          {/* Главная страница или редирект */}
          <Route
            path="/"
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />}
          />
          {/* Добавьте страницу входа /login */}
          <Route path="/login" element={<div>Login Page Placeholder</div>} />
          {/* Заглушка для 404 */}
          <Route path="*" element={<div>404 Not Found</div>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
EOF

##############################
# Frontend: src/contexts/ThemeContext.js
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/contexts/ThemeContext.js"
import React, { createContext, useState, useEffect } from 'react';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  // Получаем тему из localStorage или используем 'light' по умолчанию
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  // Сохраняем тему в localStorage при изменении
  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.body.className = theme; // Обновляем класс на body
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  const changeTheme = (newTheme) => {
    if (newTheme === 'light' || newTheme === 'dark') {
      setTheme(newTheme);
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, changeTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
EOF

##############################
# Frontend: src/contexts/LanguageContext.js
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/contexts/LanguageContext.js"
import React, { createContext, useState, useEffect } from 'react';
import i18n from '../i18n'; // Импортируем инстанс i18next

export const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  // Получаем язык из localStorage или используем 'en' по умолчанию
  const [language, setLanguage] = useState(() => localStorage.getItem('language') || 'en');

  // Меняем язык в i18next и сохраняем в localStorage
  useEffect(() => {
    i18n.changeLanguage(language);
    localStorage.setItem('language', language);
  }, [language]);

  const changeLanguage = (newLang) => {
    if (['en', 'de', 'ru'].includes(newLang)) {
      setLanguage(newLang);
    }
  };

  return (
    <LanguageContext.Provider value={{ language, changeLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};
EOF

##############################
# Frontend: src/i18n.js
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/i18n.js"
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import enTranslation from './locales/en.json';
import deTranslation from './locales/de.json';
import ruTranslation from './locales/ru.json';

const resources = {
  en: { translation: enTranslation },
  de: { translation: deTranslation },
  ru: { translation: ruTranslation },
};

i18n
  .use(initReactI18next) // передаем инстанс i18n в react-i18next
  .init({
    resources,
    lng: localStorage.getItem('language') || 'en', // язык по умолчанию
    fallbackLng: 'en', // язык, если текущий недоступен

    interpolation: {
      escapeValue: false, // не нужно для React, т.к. он сам защищает от XSS
    },
  });

export default i18n;
EOF

##############################
# Frontend: src/locales/en.json
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/locales/en.json"
{
  "navigation": {
    "dashboard": "Dashboard",
    "settings": "Settings"
  },
  "dashboard": {
    "title": "Dashboard Overview"
  },
  "settings": {
    "title": "User Settings",
    "language": "Language",
    "theme": "Theme",
    "light": "Light",
    "dark": "Dark",
    "save": "Save Settings",
    "success": "Settings saved successfully!",
    "error": "Failed to save settings."
  }
}
EOF

##############################
# Frontend: src/locales/de.json
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/locales/de.json"
{
  "navigation": {
    "dashboard": "Dashboard",
    "settings": "Einstellungen"
  },
  "dashboard": {
    "title": "Dashboard-Übersicht"
  },
  "settings": {
    "title": "Benutzereinstellungen",
    "language": "Sprache",
    "theme": "Thema",
    "light": "Hell",
    "dark": "Dunkel",
    "save": "Einstellungen speichern",
    "success": "Einstellungen erfolgreich gespeichert!",
    "error": "Einstellungen konnten nicht gespeichert werden."
  }
}
EOF

##############################
# Frontend: src/locales/ru.json
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/locales/ru.json"
{
  "navigation": {
    "dashboard": "Дашборд",
    "settings": "Настройки"
  },
  "dashboard": {
    "title": "Обзор Дашборда"
  },
  "settings": {
    "title": "Настройки пользователя",
    "language": "Язык",
    "theme": "Тема",
    "light": "Светлая",
    "dark": "Темная",
    "save": "Сохранить настройки",
    "success": "Настройки успешно сохранены!",
    "error": "Не удалось сохранить настройки."
  }
}
EOF

##############################
# Frontend: src/services/api.js
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/services/api.js"
import axios from 'axios';

// Создаем инстанс axios
// baseURL будет автоматически подставляться перед /api/...
// В Docker окружении Nginx перенаправит /api на бэкенд
const apiClient = axios.create({
  baseURL: '/api', // Используем относительный путь для Nginx proxy
  headers: {
    'Content-Type': 'application/json'
  },
});

// Перехватчик для добавления токена (пример)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken'); // Получаем токен
  if (token) {
    config.headers.Authorization = "Bearer " + token;`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Функции для работы с API
export const getSettings = () => {
  return apiClient.get('/settings/'); // Запрос на GET /api/settings/
};

export const updateSettings = (settingsData) => {
  // settingsData = { language: 'en', theme: 'dark' }
  return apiClient.put('/settings/', settingsData); // Запрос на PUT /api/settings/
};

export default apiClient;
EOF

##############################
# Frontend: src/components/Dashboard.js
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/components/Dashboard.js"
import React from 'react';
import { useTranslation } from 'react-i18next';

function Dashboard() {
  const { t } = useTranslation();

  return (
    <div>
      <h2>{t('dashboard.title')}</h2>
      <p>Welcome to your dashboard. Futures trading data will appear here.</p>
      {/* Здесь будут виджеты, графики и т.д. */}
    </div>
  );
}

export default Dashboard;
EOF

##############################
# Frontend: src/components/Settings.js
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/components/Settings.js"
import React, { useState, useEffect, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { ThemeContext } from '../contexts/ThemeContext';
import { LanguageContext } from '../contexts/LanguageContext';
import { getSettings, updateSettings } from '../services/api';

function Settings() {
  const { t } = useTranslation();
  const { theme, changeTheme } = useContext(ThemeContext);
  const { language, changeLanguage: changeAppLanguage } = useContext(LanguageContext);

  const [selectedLanguage, setSelectedLanguage] = useState(language);
  const [selectedTheme, setSelectedTheme] = useState(theme);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setSelectedLanguage(language);
  }, [language]);

  useEffect(() => {
    setSelectedTheme(theme);
  }, [theme]);

  const handleSave = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setMessage('');
    try {
      const response = await updateSettings({
        language: selectedLanguage,
        theme: selectedTheme,
      });
      changeAppLanguage(response.data.language);
      changeTheme(response.data.theme);
      setMessage(t('settings.success'));
    } catch (error) {
      console.error("Error saving settings:", error);
      setMessage(t('settings.error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>{t('settings.title')}</h2>
      {message && <p>{message}</p>}
      <form onSubmit={handleSave}>
        <div>
          <label htmlFor="languageSelect">{t('settings.language')}: </label>
          <select
            id="languageSelect"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            disabled={isLoading}
          >
            <option value="en">English</option>
            <option value="de">Deutsch</option>
            <option value="ru">Русский</option>
          </select>
        </div>
        <br />
        <div>
          <label>{t('settings.theme')}: </label>
          <label>
            <input
              type="radio"
              name="theme"
              value="light"
              checked={selectedTheme === 'light'}
              onChange={(e) => setSelectedTheme(e.target.value)}
              disabled={isLoading}
            /> {t('settings.light')}
          </label>
          <label>
            <input
              type="radio"
              name="theme"
              value="dark"
              checked={selectedTheme === 'dark'}
              onChange={(e) => setSelectedTheme(e.target.value)}
              disabled={isLoading}
            /> {t('settings.dark')}
          </label>
        </div>
        <br />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : t('settings.save')}
        </button>
      </form>
    </div>
  );
}

export default Settings;
EOF

##############################
# Frontend: src/styles/global.css
##############################
cat << 'EOF' > "$PROJECT_DIR/frontend/src/styles/global.css"
body {
  margin: 0;
  font-family: sans-serif;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Светлая тема */
body.light {
  background-color: #ffffff;
  color: #333333;
}

body.light nav {
  background-color: #f0f0f0;
  padding: 10px;
  border-bottom: 1px solid #ccc;
}
body.light nav a {
  color: #007bff;
  text-decoration: none;
  margin-right: 15px;
}
body.light nav a:hover {
  text-decoration: underline;
}
body.light button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 15px;
  cursor: pointer;
  border-radius: 4px;
}
body.light button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
body.light input, body.light select {
  padding: 5px;
  margin-left: 5px;
}

/* Темная тема */
body.dark {
  background-color: #22272e;
  color: #c9d1d9;
}

body.dark nav {
  background-color: #1c2128;
  padding: 10px;
  border-bottom: 1px solid #444c56;
}
body.dark nav a {
  color: #58a6ff;
  text-decoration: none;
  margin-right: 15px;
}
body.dark nav a:hover {
  text-decoration: underline;
}
body.dark button {
  background-color: #377ef0;
  color: white;
  border: none;
  padding: 8px 15px;
  cursor: pointer;
  border-radius: 4px;
}
body.dark button:disabled {
  background-color: #555;
  color: #aaa;
  cursor: not-allowed;
}
body.dark input, body.dark select {
  background-color: #1c2128;
  color: #c9d1d9;
  border: 1px solid #444c56;
  padding: 5px;
  margin-left: 5px;
}
body.dark label {
  margin-right: 10px;
}

/* Общий контейнер */
.app-container {
  min-height: 100vh;
}

main {
  padding: 20px;
}

nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

nav li {
  display: inline-block;
}
EOF

echo "Структура проекта crm-futures-project успешно создана!"

echo ""
echo "Далее выполните следующие шаги для запуска проекта:"
echo "1. Перейдите в папку frontend и установите зависимости:"
echo "   cd crm-futures-project/frontend && npm install"
echo "2. Вернитесь в корень проекта и выполните:"
echo "   docker-compose up --build"
