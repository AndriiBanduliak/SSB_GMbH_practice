# Scripts для CryptoCRM

Эта папка содержит скрипты для работы с CryptoCRM.

---

## 🪟 Windows Scripts

### start_all.ps1 (в корне проекта)
Автоматически запускает все компоненты CryptoCRM:
- Backend API
- Celery Worker
- Celery Beat
- Frontend

**Использование:**
```powershell
cd "D:\coursera\CBS\играюсь\срм система"
.\start_all.ps1
```

---

## 🐧 Linux/Mac Scripts

### startup.sh
Запуск с использованием Docker Compose

**Использование:**
```bash
./scripts/startup.sh
```

### backup.sh
Создание резервной копии базы данных

**Использование:**
```bash
./scripts/backup.sh
```

### restore.sh
Восстановление базы данных из резервной копии

**Использование:**
```bash
./scripts/restore.sh backup_file.sql
```

---

## 📝 Примечания

- Скрипты для Linux требуют Docker и Docker Compose
- Скрипт для Windows работает без Docker
- Перед использованием скриптов убедитесь, что они исполняемые:
  - Linux/Mac: `chmod +x scripts/*.sh`
  - Windows: права выполнения PowerShell скриптов могут потребовать настройки

---

## 🔧 Создание собственных скриптов

### Для Windows (PowerShell):
Создайте файл `.ps1` с необходимыми командами.

Пример:
```powershell
Write-Host "Starting service..." -ForegroundColor Green
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### Для Linux (Bash):
Создайте файл `.sh` с необходимыми командами.

Пример:
```bash
#!/bin/bash
echo "Starting service..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

---

Для получения дополнительной информации см. основную документацию:
- [Windows без Docker](../WINDOWS_README.md)
- [Docker setup](../README.md)

