# 🚀 Быстрое развертывание Telegram бота

## 🎯 Выберите способ развертывания:

### 1. 🆓 **Heroku (Самый простой)**
```bash
# 1. Установите Heroku CLI
# 2. Войдите в аккаунт
heroku login

# 3. Создайте приложение
heroku create your-bot-name

# 4. Настройте переменные
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set OPENAI_API_KEY=your_key

# 5. Разверните
git add .
git commit -m "Deploy bot"
git push heroku main

# 6. Запустите воркер
heroku ps:scale worker=1
```

### 2. 💰 **VPS (Надежный)**
```bash
# 1. Создайте VPS (DigitalOcean, Vultr, Linode)
# 2. Подключитесь к серверу
ssh root@your-server-ip

# 3. Запустите скрипт развертывания
wget https://raw.githubusercontent.com/YOUR_REPO/deploy.sh
chmod +x deploy.sh
./deploy.sh

# 4. Настройте .env файл
nano /home/telegrambot/legal-consultant-bot/updated_0.2/.env

# 5. Запустите бота
bot-manage start
```

### 3. 🆕 **Railway (Современный)**
```bash
# 1. Установите Railway CLI
npm install -g @railway/cli

# 2. Войдите в аккаунт
railway login

# 3. Разверните
railway init
railway up
```

## 📊 Сравнение способов:

| Способ | Сложность | Цена | Надежность | Рекомендация |
|--------|-----------|------|------------|--------------|
| **Heroku** | ⭐ | $7/мес | ⭐⭐⭐ | Для начинающих |
| **VPS** | ⭐⭐⭐ | $3-10/мес | ⭐⭐⭐⭐⭐ | Для продвинутых |
| **Railway** | ⭐⭐ | $5/мес | ⭐⭐⭐⭐ | Для среднего уровня |

## 🔧 После развертывания:

### Проверка работы:
```bash
# Heroku
heroku logs --tail

# VPS
bot-manage status
bot-manage logs

# Railway
railway logs
```

### Управление ботом:
```bash
# Heroku
heroku restart
heroku ps:scale worker=0  # остановка
heroku ps:scale worker=1  # запуск

# VPS
bot-manage restart
bot-manage stop
bot-manage start

# Railway
railway restart
```

## ⚠️ Важные моменты:

1. **Не забудьте настроить .env файл** с вашими токенами
2. **Проверьте логи** после развертывания
3. **Настройте мониторинг** для отслеживания работы
4. **Сделайте бэкап** базы данных

## 🆘 Если что-то не работает:

1. Проверьте логи на ошибки
2. Убедитесь, что все переменные окружения настроены
3. Проверьте, что токены действительны
4. Убедитесь, что бот запущен и работает

---

**Удачного развертывания! 🎉**
