#!/bin/bash

# 🚀 Скрипт автоматического развертывания Telegram бота на VPS
# Использование: ./deploy.sh

set -e

echo "🚀 Начинаем развертывание Telegram бота..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка, что скрипт запущен от root
if [ "$EUID" -ne 0 ]; then
    error "Пожалуйста, запустите скрипт от root: sudo ./deploy.sh"
    exit 1
fi

# Обновление системы
log "Обновляем систему..."
apt update && apt upgrade -y

# Установка необходимых пакетов
log "Устанавливаем зависимости..."
apt install -y python3 python3-pip python3-venv git nginx supervisor htop curl wget

# Создание пользователя для бота
log "Создаем пользователя telegrambot..."
if ! id "telegrambot" &>/dev/null; then
    adduser --disabled-password --gecos "" telegrambot
    usermod -aG sudo telegrambot
    log "Пользователь telegrambot создан"
else
    warn "Пользователь telegrambot уже существует"
fi

# Переход в домашнюю директорию пользователя
cd /home/telegrambot

# Клонирование репозитория (замените на ваш URL)
log "Клонируем репозиторий..."
if [ ! -d "legal-consultant-bot" ]; then
    sudo -u telegrambot git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git legal-consultant-bot
    log "Репозиторий склонирован"
else
    warn "Репозиторий уже существует"
fi

# Переход в директорию проекта
cd legal-consultant-bot/updated_0.2

# Создание виртуального окружения
log "Создаем виртуальное окружение..."
sudo -u telegrambot python3 -m venv venv

# Активация виртуального окружения и установка зависимостей
log "Устанавливаем Python зависимости..."
sudo -u telegrambot bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u telegrambot bash -c "source venv/bin/activate && pip install python-telegram-bot openai python-dotenv python-docx PyPDF2 num2words"

# Создание файла .env
log "Создаем файл .env..."
if [ ! -f ".env" ]; then
    sudo -u telegrambot cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
DB_NAME=multilang_bot.db
LOG_LEVEL=INFO
EOF
    warn "Не забудьте отредактировать файл .env с вашими токенами!"
else
    warn "Файл .env уже существует"
fi

# Создание systemd сервиса
log "Создаем systemd сервис..."
cat > /etc/systemd/system/telegram-bot.service << EOF
[Unit]
Description=Telegram Legal Consultant Bot
After=network.target

[Service]
Type=simple
User=telegrambot
WorkingDirectory=/home/telegrambot/legal-consultant-bot/updated_0.2
Environment=PATH=/home/telegrambot/legal-consultant-bot/updated_0.2/venv/bin
ExecStart=/home/telegrambot/legal-consultant-bot/updated_0.2/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd и активация сервиса
log "Активируем сервис..."
systemctl daemon-reload
systemctl enable telegram-bot

# Настройка файрвола
log "Настраиваем файрвол..."
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443

# Создание директории для бэкапов
log "Создаем директорию для бэкапов..."
sudo -u telegrambot mkdir -p /home/telegrambot/backup

# Настройка cron для бэкапов
log "Настраиваем автоматические бэкапы..."
sudo -u telegrambot crontab -l 2>/dev/null | { cat; echo "0 2 * * * cp /home/telegrambot/legal-consultant-bot/updated_0.2/multilang_bot.db /home/telegrambot/backup/multilang_bot_\$(date +\%Y\%m\%d).db"; } | sudo -u telegrambot crontab -

# Создание скрипта управления
log "Создаем скрипт управления..."
cat > /usr/local/bin/bot-manage << 'EOF'
#!/bin/bash

case "$1" in
    start)
        echo "Запускаем бота..."
        systemctl start telegram-bot
        ;;
    stop)
        echo "Останавливаем бота..."
        systemctl stop telegram-bot
        ;;
    restart)
        echo "Перезапускаем бота..."
        systemctl restart telegram-bot
        ;;
    status)
        systemctl status telegram-bot
        ;;
    logs)
        journalctl -u telegram-bot -f
        ;;
    update)
        echo "Обновляем бота..."
        cd /home/telegrambot/legal-consultant-bot
        sudo -u telegrambot git pull origin main
        systemctl restart telegram-bot
        echo "Бот обновлен и перезапущен"
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs|update}"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/bot-manage

# Финальные инструкции
log "Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл .env с вашими токенами:"
echo "   nano /home/telegrambot/legal-consultant-bot/updated_0.2/.env"
echo ""
echo "2. Запустите бота:"
echo "   bot-manage start"
echo ""
echo "3. Проверьте статус:"
echo "   bot-manage status"
echo ""
echo "4. Просмотрите логи:"
echo "   bot-manage logs"
echo ""
echo "🔧 Полезные команды:"
echo "   bot-manage start    - Запустить бота"
echo "   bot-manage stop     - Остановить бота"
echo "   bot-manage restart  - Перезапустить бота"
echo "   bot-manage status   - Проверить статус"
echo "   bot-manage logs     - Просмотреть логи"
echo "   bot-manage update   - Обновить бота"
echo ""
warn "Не забудьте настроить файл .env с вашими токенами перед запуском!"
