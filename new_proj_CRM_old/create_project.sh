#!/bin/bash
set -e

# Корневая директория проекта
PROJECT_DIR="crm-futures-project"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# -------------------------
# Backend структура
# -------------------------
mkdir -p backend/app/routes
mkdir -p backend/app/static
mkdir -p backend/app/templates
mkdir -p backend/migrations

# Файлы для backend/app
touch backend/app/__init__.py      # Инициализация Flask приложения, расширений
touch backend/app/config.py        # Конфигурация
touch backend/app/models.py        # Модели SQLAlchemy (User)

# Файлы для маршрутов (Blueprints)
touch backend/app/routes/__init__.py
touch backend/app/routes/auth.py   # (Placeholder) Аутентификация
touch backend/app/routes/settings.py  # API для настроек пользователя

# Дополнительные файлы backend
touch backend/run.py              # Точка входа для запуска Flask
touch backend/requirements.txt    # Зависимости Python
touch backend/Dockerfile          # Dockerfile для бэкенда

# -------------------------
# Frontend структура
# -------------------------
mkdir -p frontend/public
mkdir -p frontend/src/components
mkdir -p frontend/src/contexts
mkdir -p frontend/src/locales
mkdir -p frontend/src/services
mkdir -p frontend/src/styles

# Файл для frontend/public
touch frontend/public/index.html  # Базовый HTML

# Файлы для frontend/src
touch frontend/src/App.js         # Корневой компонент React
touch frontend/src/index.js       # Точка входа React

# Файлы для компонентов
touch frontend/src/components/Dashboard.js
touch frontend/src/components/Settings.js

# Файлы для React Context
touch frontend/src/contexts/LanguageContext.js
touch frontend/src/contexts/ThemeContext.js

# Файлы локализации (i18n)
touch frontend/src/locales/en.json
touch frontend/src/locales/de.json
touch frontend/src/locales/ru.json

# Файл для API запросов
touch frontend/src/services/api.js

# Файл для стилей
touch frontend/src/styles/global.css

# Дополнительные файлы frontend
touch frontend/package.json        # Зависимости Node.js
touch frontend/Dockerfile          # Dockerfile для фронтенда (Nginx)
touch frontend/nginx.conf          # Конфигурация Nginx для Docker

# -------------------------
# DB и корневые файлы проекта
# -------------------------
mkdir -p db_init
touch db_init/init.sql             # SQL скрипт для инициализации БД

touch docker-compose.yml           # Файл Docker Compose
touch .env                         # Файл с переменными окружения (пример)

echo "Структура проекта успешно создана!"
