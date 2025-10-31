# 🚀 CryptoCRM - Crypto Asset Management CRM System

## 📖 Übersicht

**CryptoCRM** ist ein umfassendes Customer Relationship Management (CRM) System, das speziell für Crypto Asset Manager entwickelt wurde. Das System bietet Funktionen zur Verwaltung von Kunden, Transaktionen, P&L-Berichten, Aufgaben und automatisierten Workflows.

### 🎯 Hauptfunktionen

- **👥 Kundenverwaltung** - Vollständige Verwaltung von Kundenprofilen mit Status-Tracking
- **💰 Transaktionsverfolgung** - Detaillierte Aufzeichnung aller Krypto-Transaktionen
- **📊 P&L-Berichte** - Automatische Berechnung von Profit & Loss
- **📈 Pipeline-Management** - Sales-Pipeline mit anpassbaren Stufen
- **✅ Aufgabenverwaltung** - Integriertes Task-Management-System
- **🔐 Sichere Authentifizierung** - JWT-basierte Auth mit optionaler 2FA
- **🔌 Exchange-Integration** - Binance und weitere Exchanges per API
- **📧 E-Mail-Benachrichtigungen** - Automatische Benachrichtigungen
- **🎨 Moderne UI** - React-basiertes responsive Dashboard

---

## 🛠️ Technologie-Stack

### Backend
- **FastAPI** - Modernes Python-Webframework
- **SQLAlchemy 2.0** - ORM mit async Support
- **PostgreSQL** - Hauptdatenbank
- **Redis** - Caching und Celery-Broker
- **Celery** - Asynchrone Aufgabenverarbeitung
- **Alembic** - Datenbank-Migration

### Frontend
- **React 18** - UI-Framework
- **React Router v6** - Navigation
- **Axios** - HTTP-Client
- **Modern CSS** - Responsive Design

### Sicherheit
- **JWT** - Token-basierte Authentifizierung
- **bcrypt** - Passwort-Hashing
- **CORS** - Cross-Origin-Sicherheit
- **2FA** - Zwei-Faktor-Authentifizierung (optional)

---

## 📋 Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass folgende Software installiert ist:

### Erforderlich:
1. **Python 3.10+** - [Download](https://www.python.org/downloads/)
2. **Node.js 16+** - [Download](https://nodejs.org/)
3. **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
4. **Git** - [Download](https://git-scm.com/)

### Optional:
5. **Redis** oder **Memurai** (für Windows) - Für Celery-Tasks

---

## ⚡ Schnellstart (Eine Kommando!)

### Automatischer Start mit PowerShell:

```powershell
.\start_demo.ps1
```

Dieses Skript wird automatisch:
- ✅ Alle Abhängigkeiten prüfen
- ✅ Python-Pakete installieren (falls nötig)
- ✅ Datenbank initialisieren
- ✅ Backend API starten (Port 8000)
- ✅ Frontend starten (Port 3000)
- ✅ Celery Worker starten (falls Redis läuft)
- ✅ Browser mit Anmeldeseite öffnen

**Standard-Anmeldedaten:**
```
E-Mail:   admin@cryptocrm.com
Passwort: admin123
```

---

## 📦 Manuelle Installation

Falls Sie die Schritte manuell durchführen möchten:

### 1. Repository klonen

```powershell
git clone https://github.com/AndriiBanduliak/SSB_GMbH_practice/tree/main/crm-crypto
cd crm-crypto
```

### 2. PostgreSQL-Datenbank erstellen

```sql
CREATE DATABASE cryptocrm;
CREATE USER cryptocrm WITH PASSWORD 'cryptocrm_password';
GRANT ALL PRIVILEGES ON DATABASE cryptocrm TO cryptocrm;
```

### 3. Backend einrichten

```powershell
cd backend

# Virtuelle Umgebung erstellen
python -m venv venv

# Virtuelle Umgebung aktivieren
.\venv\Scripts\Activate.ps1

# Abhängigkeiten installieren
pip install --upgrade pip
pip install -r requirements.txt

# .env Datei erstellen
copy ENV_TEMPLATE.txt .env

# .env mit Ihren Einstellungen anpassen
# DATABASE_URL, SECRET_KEY, etc.

# Datenbank initialisieren
python init_db.py

# Admin-Benutzer erstellen (falls nötig)
python create_admin_user.py
```

### 4. Backend starten

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend läuft auf:** http://localhost:8000
**API Dokumentation:** http://localhost:8000/api/v1/docs

### 5. Frontend einrichten und starten

```powershell
cd frontend

# Abhängigkeiten installieren
npm install

# Entwicklungsserver starten
npm start
```

**Frontend läuft auf:** http://localhost:3000

### 6. Celery Worker starten (Optional)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m celery -A app.worker.celery_app worker --loglevel=info --pool=solo
```

---

## 🔧 Konfiguration

### Umgebungsvariablen (.env)

Wichtige Einstellungen in der `.env` Datei:

```env
# Datenbank
DATABASE_URL=postgresql+asyncpg://cryptocrm:cryptocrm_password@localhost/cryptocrm

# Sicherheit
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin-Benutzer
FIRST_SUPERUSER_EMAIL=admin@cryptocrm.com
FIRST_SUPERUSER_PASSWORD=admin123

# CORS (für Frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Redis
REDIS_URL=redis://localhost:6379/0

# E-Mail (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 📚 API-Dokumentation

Nach dem Start des Backends ist die interaktive API-Dokumentation verfügbar:

- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

### Hauptendpunkte:

#### Authentifizierung
- `POST /api/v1/auth/login` - Benutzer-Anmeldung
- `POST /api/v1/auth/register` - Neue Benutzer registrieren
- `GET /api/v1/auth/me` - Aktuellen Benutzer abrufen

#### Kunden
- `GET /api/v1/clients/` - Alle Kunden auflisten
- `POST /api/v1/clients/` - Neuen Kunden erstellen
- `GET /api/v1/clients/{id}` - Kunden-Details
- `PUT /api/v1/clients/{id}` - Kunden aktualisieren
- `DELETE /api/v1/clients/{id}` - Kunden löschen

#### Transaktionen
- `GET /api/v1/transactions/` - Transaktionen auflisten
- `POST /api/v1/transactions/` - Transaktion erstellen
- `GET /api/v1/transactions/{id}` - Transaktions-Details

#### P&L-Berichte
- `GET /api/v1/pnl/summary` - P&L-Zusammenfassung
- `GET /api/v1/pnl/by-client` - P&L nach Kunde

#### Aufgaben
- `GET /api/v1/tasks/` - Aufgaben auflisten
- `POST /api/v1/tasks/` - Neue Aufgabe erstellen
- `PUT /api/v1/tasks/{id}` - Aufgabe aktualisieren

---

## 🎨 Frontend-Funktionen

### Dashboard
- Übersicht über KPIs
- Neueste Transaktionen
- Anstehende Aufgaben
- P&L-Diagramme

### Kundenverwaltung
- Kundenliste mit Filter
- Detaillierte Kundenprofile
- Status-Tracking (Lead, Prospect, Active, Inactive)
- Kontakthistorie

### Transaktionen
- Transaktionsliste
- Filter nach Datum, Typ, Status
- Transaktionsdetails
- Export-Funktionen

### Aufgaben
- Aufgabenliste mit Prioritäten
- Zuweisung zu Benutzern
- Deadline-Tracking
- Status-Updates

---

## 🔐 Sicherheit

### Authentifizierung
- JWT-Tokens mit konfigurierbarer Ablaufzeit
- Passwort-Hashing mit bcrypt
- Optionale 2FA mit TOTP

### Autorisierung
- Rollenbasierte Zugriffskontrolle (RBAC)
- Rollen: ADMIN, MANAGER, TRADER, VIEWER
- Endpunkt-basierte Berechtigungen

### Datenbank
- Parametrisierte Queries (SQL-Injection-Schutz)
- Verschlüsselte Passwörter
- API-Schlüssel-Verschlüsselung

---

## 🧪 Tests

### Backend-Tests ausführen

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest
```

### Frontend-Tests ausführen

```powershell
cd frontend
npm test
```

---

## 📊 Datenbankschema

### Haupttabellen:

- **users** - Benutzerkonten
- **clients** - Kundenprofile
- **transactions** - Krypto-Transaktionen
- **pnl_records** - Profit & Loss Berichte
- **pipelines** - Sales-Pipelines
- **pipeline_stages** - Pipeline-Stufen
- **tasks** - Aufgaben
- **audit_logs** - Audit-Trail

---

## 🐛 Fehlerbehebung

### Backend startet nicht

1. **PostgreSQL prüfen:**
   ```powershell
   # Öffnen Sie services.msc
   # Starten Sie den PostgreSQL-Dienst
   ```

2. **Virtuelle Umgebung prüfen:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   ```

3. **Abhängigkeiten neu installieren:**
   ```powershell
   pip install -r requirements.txt
   ```

### Frontend startet nicht

1. **node_modules löschen und neu installieren:**
   ```powershell
   cd frontend
   Remove-Item -Recurse -Force node_modules
   npm install
   ```

2. **Port 3000 ist belegt:**
   ```powershell
   # Frontend auf anderem Port starten
   $env:PORT=3001
   npm start
   ```

### Celery funktioniert nicht

1. **Redis prüfen:**
   ```powershell
   # Testen Sie Redis-Verbindung
   redis-cli ping
   # Sollte "PONG" zurückgeben
   ```

2. **Memurai (Windows Redis Alternative):**
   - Download: https://www.memurai.com/

### Login funktioniert nicht

1. **Admin-Benutzer neu erstellen:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python create_admin_user.py
   ```

2. **CORS-Einstellungen prüfen:**
   - Überprüfen Sie `CORS_ORIGINS` in `.env`
   - Sollte enthalten: `http://localhost:3000`

---

## 📝 Entwicklung

### Code-Struktur

```
cryptocrm/
├── backend/
│   ├── app/
│   │   ├── api/          # API-Endpunkte
│   │   ├── core/         # Konfiguration, Sicherheit
│   │   ├── models/       # SQLAlchemy-Modelle
│   │   ├── schemas/      # Pydantic-Schemas
│   │   ├── services/     # Business-Logik
│   │   └── worker/       # Celery-Tasks
│   ├── alembic/          # Datenbank-Migrationen
│   └── tests/            # Backend-Tests
│
├── frontend/
│   ├── public/           # Statische Dateien
│   └── src/
│       ├── components/   # React-Komponenten
│       ├── contexts/     # React-Contexts
│       ├── pages/        # Seiten-Komponenten
│       └── services/     # API-Services
│
└── тупуш/               # Deployment-Skripte
    ├── start_demo.ps1    # Auto-Start-Skript
    └── create_admin_user.py  # Admin-Erstellung
```

### Neue Funktion hinzufügen

1. **Backend-Modell erstellen** (`app/models/`)
2. **Pydantic-Schema erstellen** (`app/schemas/`)
3. **API-Endpunkt erstellen** (`app/api/v1/endpoints/`)
4. **Service-Logik implementieren** (`app/services/`)
5. **Migration erstellen:**
   ```powershell
   alembic revision --autogenerate -m "Add new feature"
   alembic upgrade head
   ```

6. **Frontend-Komponente erstellen** (`frontend/src/components/`)
7. **API-Service hinzufügen** (`frontend/src/services/`)

---

## 🚀 Deployment

### Produktions-Deployment

#### 1. Backend (FastAPI)

```powershell
# Gunicorn mit Uvicorn Worker
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 2. Frontend (React)

```powershell
cd frontend
npm run build
# Serve build/ mit Nginx oder Apache
```

#### 3. Datenbank

- Verwenden Sie verwaltete PostgreSQL (z.B. AWS RDS)
- Backup-Strategie implementieren
- SSL-Verbindungen aktivieren

#### 4. Redis/Celery

- Verwenden Sie verwalteten Redis (z.B. AWS ElastiCache)
- Skalieren Sie Celery-Worker horizontal

---

## 📄 Lizenz

Dieses Projekt ist proprietär und vertraulich.

---

## 👥 Support

Bei Fragen oder Problemen:

1. Prüfen Sie die **Fehlerbehebungs-Sektion**
2. Konsultieren Sie die **API-Dokumentation**
3. Kontaktieren Sie den Entwickler

---

## 🎯 Roadmap

### Geplante Funktionen:

- [ ] WebSocket für Echtzeit-Updates
- [ ] Erweiterte Reporting-Dashboard
- [ ] Mobile App (React Native)
- [ ] Weitere Exchange-Integrationen
- [ ] KI-basierte Kundenempfehlungen
- [ ] Automatisierte Compliance-Berichte
- [ ] Multi-Tenancy-Support

---

## ⚙️ Systemanforderungen

### Mindestanforderungen:
- **CPU:** 2 Kerne
- **RAM:** 4 GB
- **Festplatte:** 10 GB freier Speicher
- **OS:** Windows 10/11, Linux, macOS

### Empfohlen:
- **CPU:** 4+ Kerne
- **RAM:** 8+ GB
- **Festplatte:** 20+ GB SSD
- **OS:** Windows 11, Ubuntu 22.04 LTS

---

## 🌟 Erste Schritte

Nach der Installation:

1. **Starten Sie die Anwendung:**
   ```powershell
   .\start_demo.ps1
   ```

2. **Öffnen Sie im Browser:**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/api/v1/docs

3. **Melden Sie sich an:**
   - E-Mail: `admin@cryptocrm.com`
   - Passwort: `admin123`

4. **Erkunden Sie das Dashboard** und die Funktionen!

---

## 📞 Kontakt

**Entwickelt für:** Deutscher Kunde
**Version:** 1.0.0
**Letztes Update:** Oktober 2025

---

**Viel Erfolg mit CryptoCRM! 🚀**

