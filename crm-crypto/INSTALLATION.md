# 🚀 CryptoCRM - Schnellinstallation

## ⚡ Sofort-Start (Empfohlen)

### Schritt 1: Voraussetzungen installieren

Installieren Sie folgende Software:

1. **Python 3.10+** → https://www.python.org/downloads/
2. **Node.js 16+** → https://nodejs.org/
3. **PostgreSQL 14+** → https://www.postgresql.org/download/
4. **Git** → https://git-scm.com/

### Schritt 2: PostgreSQL vorbereiten

Öffnen Sie **pgAdmin** oder **psql** und erstellen Sie die Datenbank:

```sql
CREATE DATABASE cryptocrm;
CREATE USER cryptocrm WITH PASSWORD 'cryptocrm123';
GRANT ALL PRIVILEGES ON DATABASE cryptocrm TO cryptocrm;
```

### Schritt 3: Projekt einrichten

```powershell
# Repository klonen (oder Dateien entpacken)
cd "D:\Ihr\Projekt\Pfad"

# Backend vorbereiten
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# .env Datei erstellen
copy ENV_TEMPLATE.txt .env

# Datenbank initialisieren
python init_db.py

# Zurück zum Hauptverzeichnis
cd ..
```

### Schritt 4: Frontend vorbereiten

```powershell
cd frontend
npm install
cd ..
```

### Schritt 5: Alles starten!

```powershell
.\start_demo.ps1
```

Das war's! Die Anwendung startet automatisch.

---

## 🌐 Zugriff

Nach dem Start:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Dokumentation:** http://localhost:8000/api/v1/docs

### Standard-Anmeldedaten:

```
E-Mail:   admin@cryptocrm.com
Passwort: admin123
```

---

## 🛠️ Manueller Start (Falls Automatik nicht funktioniert)

### Backend starten:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend starten (Neues PowerShell-Fenster):

```powershell
cd frontend
npm start
```

### Celery starten (Optional, Neues PowerShell-Fenster):

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m celery -A app.worker.celery_app worker --loglevel=info --pool=solo
```

---

## ⚠️ Häufige Probleme

### Problem: "PostgreSQL läuft nicht"

**Lösung:**
1. Drücken Sie `Win + R`
2. Tippen Sie `services.msc`
3. Suchen Sie "PostgreSQL"
4. Rechtsklick → "Starten"

### Problem: "Port 8000 ist bereits belegt"

**Lösung:**
```powershell
# Alle Python-Prozesse beenden
Get-Process python | Stop-Process -Force
```

### Problem: "Modul 'fastapi' nicht gefunden"

**Lösung:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problem: "npm Fehler"

**Lösung:**
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

### Problem: "Login funktioniert nicht"

**Lösung:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python create_admin_user.py
```

---

## 📞 Support

Bei weiteren Fragen:

1. Lesen Sie die vollständige Dokumentation: `README.md`
2. Prüfen Sie die API-Docs: http://localhost:8000/api/v1/docs
3. Kontaktieren Sie den Support

---

## ✅ Checkliste

- [ ] Python 3.10+ installiert
- [ ] Node.js 16+ installiert
- [ ] PostgreSQL 14+ installiert
- [ ] Datenbank `cryptocrm` erstellt
- [ ] Backend venv erstellt
- [ ] Backend dependencies installiert
- [ ] .env Datei erstellt
- [ ] Datenbank initialisiert
- [ ] Frontend dependencies installiert
- [ ] `start_demo.ps1` ausgeführt
- [ ] Browser öffnet sich automatisch
- [ ] Login funktioniert

---

**Viel Erfolg! 🚀**

