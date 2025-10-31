# 🚀 Развертывание на Heroku (Простой способ)

## 📋 Подготовка

### 1. Установка Heroku CLI
```bash
# Windows (через Chocolatey)
choco install heroku-cli

# Windows (через Scoop)
scoop install heroku

# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Вход в Heroku
```bash
heroku login
```

## 🔧 Настройка проекта

### 1. Создание файлов для Heroku

#### Procfile
```bash
echo "worker: python main.py" > Procfile
```

#### requirements.txt
```bash
pip freeze > requirements.txt
```

#### runtime.txt
```bash
echo "python-3.11.0" > runtime.txt
```

### 2. Создание приложения Heroku
```bash
heroku create your-bot-name
```

### 3. Настройка переменных окружения
```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token_here
heroku config:set OPENAI_API_KEY=your_openai_api_key_here
heroku config:set OPENAI_MODEL=gpt-4o-mini
heroku config:set DB_NAME=multilang_bot.db
heroku config:set LOG_LEVEL=INFO
```

### 4. Развертывание
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 5. Запуск воркера
```bash
heroku ps:scale worker=1
```

## 📊 Мониторинг

### Просмотр логов
```bash
heroku logs --tail
```

### Проверка статуса
```bash
heroku ps
```

### Перезапуск
```bash
heroku restart
```

## ⚠️ Ограничения Heroku

- **Бесплатный план**: Приложение "засыпает" через 30 мин неактивности
- **Платный план**: $7/месяц за постоянную работу
- **База данных**: Файловая БД сбрасывается при перезапуске

## 🔄 Альтернативы Heroku

### Railway (Рекомендуется)
```bash
# Установка Railway CLI
npm install -g @railway/cli

# Вход в Railway
railway login

# Развертывание
railway init
railway up
```

### Render
1. Подключите GitHub репозиторий
2. Выберите "Web Service"
3. Настройте переменные окружения
4. Разверните

---

## 💰 Сравнение цен:

| Провайдер | Бесплатно | Платно | Особенности |
|-----------|-----------|--------|-------------|
| **Heroku** | Да (с ограничениями) | $7/мес | Простое развертывание |
| **Railway** | Да (с ограничениями) | $5/мес | Современный интерфейс |
| **Render** | Да (с ограничениями) | $7/мес | Хорошая производительность |
| **VPS** | Нет | $3-10/мес | Полный контроль |
