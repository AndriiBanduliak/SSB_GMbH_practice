#!/bin/bash

if ! command -v python3 &>/dev/null; then
    echo "Python3 не установлен. Установите Python3 и повторите попытку."
    exit 1
fi

python3 -m venv venv
source venv/Scripts/activate
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Файл requirements.txt не найден!"
    exit 1
fi

echo "Виртуальное окружение успешно настроено и зависимости установлены."
