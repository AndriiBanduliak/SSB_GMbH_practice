# 🚀 Инструкция по развертыванию Telegram бота на VPS

## 📋 Подготовка

### 1. Создание VPS
- Выберите провайдера (DigitalOcean, Vultr, Linode)
- Создайте сервер с Ubuntu 20.04/22.04
- Минимальные требования: 1GB RAM, 1 CPU, 25GB SSD

### 2. Подключение к серверу
```bash
ssh root@YOUR_SERVER_IP
```

## 🔧 Установка зависимостей

### 1. Обновление системы
```bash
apt update && apt upgrade -y
```

### 2. Установка Python и pip
```bash
apt install python3 python3-pip python3-venv -y
```

### 3. Установка дополнительных пакетов
```bash
apt install git nginx supervisor -y
```

## 📁 Развертывание бота

### 1. Создание пользователя для бота
```bash
adduser telegrambot
usermod -aG sudo telegrambot
su - telegrambot
```

### 2. Клонирование проекта
```bash
git clone YOUR_REPOSITORY_URL
cd "Legal consultant tg bot/updated_0.2"
```

### 3. Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Установка зависимостей
```bash
pip install python-telegram-bot openai python-dotenv python-docx PyPDF2 num2words
```

### 5. Создание файла .env
```bash
nano .env
```

Содержимое .env:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
DB_NAME=multilang_bot.db
LOG_LEVEL=INFO
```

## 🔄 Настройка автозапуска

### 1. Создание systemd сервиса
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram Legal Consultant Bot
After=network.target

[Service]
Type=simple
User=telegrambot
WorkingDirectory=/home/telegrambot/"Legal consultant tg bot/updated_0.2"
Environment=PATH=/home/telegrambot/"Legal consultant tg bot/updated_0.2"/venv/bin
ExecStart=/home/telegrambot/"Legal consultant tg bot/updated_0.2"/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Активация сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### 3. Проверка статуса
```bash
sudo systemctl status telegram-bot
```

## 📊 Мониторинг и логи

### 1. Просмотр логов
```bash
sudo journalctl -u telegram-bot -f
```

### 2. Перезапуск бота
```bash
sudo systemctl restart telegram-bot
```

### 3. Остановка бота
```bash
sudo systemctl stop telegram-bot
```

## 🔒 Безопасность

### 1. Настройка файрвола
```bash
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable
```

### 2. Настройка SSH ключей
```bash
# На локальной машине
ssh-keygen -t rsa -b 4096
ssh-copy-id telegrambot@YOUR_SERVER_IP
```

## 📈 Масштабирование

### 1. Настройка Nginx (опционально)
```bash
sudo nano /etc/nginx/sites-available/telegram-bot
```

### 2. Мониторинг ресурсов
```bash
htop
df -h
free -h
```

## 🚨 Резервное копирование

### 1. Автоматический бэкап базы данных
```bash
crontab -e
# Добавить строку:
0 2 * * * cp /home/telegrambot/"Legal consultant tg bot/updated_0.2"/multilang_bot.db /home/telegrambot/backup/multilang_bot_$(date +\%Y\%m\%d).db
```

## 🔧 Обновление бота

### 1. Обновление кода
```bash
cd "Legal consultant tg bot/updated_0.2"
git pull origin main
sudo systemctl restart telegram-bot
```

## 📞 Поддержка

### Полезные команды:
```bash
# Проверка статуса
sudo systemctl status telegram-bot

# Просмотр логов
sudo journalctl -u telegram-bot -f

# Перезапуск
sudo systemctl restart telegram-bot

# Проверка места на диске
df -h

# Проверка использования памяти
free -h

# Проверка процессов
ps aux | grep python
```

---

## 💰 Примерные расходы:

- **VPS**: $3-10/месяц
- **Домен** (опционально): $10-15/год
- **SSL сертификат**: Бесплатно (Let's Encrypt)

**Итого**: ~$3-10/месяц за постоянную работу бота 24/7
