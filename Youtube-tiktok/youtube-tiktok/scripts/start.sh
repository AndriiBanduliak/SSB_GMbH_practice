#!/usr/bin/env bash
set -e

# Фиксированное имя проекта
PROJECT_DIR="youtube-tiktok"

# Создание структуры директорий
mkdir -p "$PROJECT_DIR"/{src,scripts,tests}

# Файлы в корне проекта
cat > "$PROJECT_DIR"/README.md <<EOL
# $PROJECT_DIR

Автоматизация конвертации YouTube Shorts в TikTok.
EOL

touch "$PROJECT_DIR"/requirements.txt
cat > "$PROJECT_DIR"/.gitignore <<EOL
venv/
__pycache__/
*.pyc
EOL

# Заготовки файлов в src
for file in __init__.py fetch_shorts.py metadata.py download.py process.py generate_text.py publish.py scheduler.py analytics.py config.py; do
  touch "$PROJECT_DIR"/src/$file
done

# Копирование этого скрипта в scripts
cp "$0" "$PROJECT_DIR"/scripts/

# Переход в директорию проекта
cd "$PROJECT_DIR"

# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения (Git Bash / WSL)
if [ -f "venv/Scripts/activate" ]; then
  source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
else
  echo "Файл активации venv не найден. Убедитесь, что venv создан корректно."
  exit 1
fi

echo "Виртуальное окружение активировано."

echo "Структура проекта '$PROJECT_DIR' создана и venv активирован."