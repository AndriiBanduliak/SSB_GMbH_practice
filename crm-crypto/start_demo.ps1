# CryptoCRM - Vollautomatischer Start und Demo
# Autor: AI Assistant

param(
    [switch]$SkipBrowser = $false
)

$ErrorActionPreference = "Stop"

# Farben für Ausgabe
function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "[WARNUNG] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[FEHLER] $Message" -ForegroundColor Red }
function Write-Header { param($Message) Write-Host "`n=== $Message ===" -ForegroundColor Magenta }

# Skript-Verzeichnis ermitteln
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "backend"
$FrontendDir = Join-Path $ScriptDir "frontend"

Write-Header "CryptoCRM - Automatischer Start"
Write-Host ""

# Verzeichnisse prüfen
if (-not (Test-Path $BackendDir)) {
    Write-Error "Backend-Verzeichnis nicht gefunden!"
    exit 1
}

if (-not (Test-Path $FrontendDir)) {
    Write-Error "Frontend-Verzeichnis nicht gefunden!"
    exit 1
}

# Virtuelle Umgebung prüfen
$VenvPath = Join-Path $BackendDir "venv\Scripts\Activate.ps1"
if (-not (Test-Path $VenvPath)) {
    Write-Error "Virtuelle Umgebung nicht gefunden! Erstellen mit: python -m venv venv"
    exit 1
}

# .env Datei prüfen
$EnvFile = Join-Path $BackendDir ".env"
$EnvTemplate = Join-Path $BackendDir "ENV_TEMPLATE.txt"

if (-not (Test-Path $EnvFile)) {
    if (Test-Path $EnvTemplate) {
        Write-Info "Erstelle .env Datei aus Vorlage..."
        Copy-Item $EnvTemplate $EnvFile
        Write-Success ".env Datei erstellt"
    } else {
        Write-Error ".env Datei nicht gefunden! Bitte manuell erstellen."
        exit 1
    }
}

# Funktion zum Prüfen ob Port belegt ist
function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        return $connection.TcpTestSucceeded
    } catch {
        return $false
    }
}

# Funktion zum Warten auf Port
function Wait-ForPort {
    param([int]$Port, [int]$TimeoutSeconds = 30, [string]$ServiceName = "Dienst")
    Write-Info "Warte auf $ServiceName auf Port $Port..."
    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        if (Test-Port -Port $Port) {
            Write-Success "$ServiceName ist verfügbar!"
            return $true
        }
        Start-Sleep -Seconds 1
        $elapsed++
        if ($elapsed % 5 -eq 0) {
            Write-Host "  Warte noch... ($elapsed/$TimeoutSeconds)" -ForegroundColor Gray
        }
    }
    Write-Host ""
    Write-Warning "$ServiceName wurde nicht innerhalb von $TimeoutSeconds Sekunden gestartet"
    return $false
}

# PostgreSQL prüfen
Write-Header "Abhängigkeiten prüfen"
Write-Info "Prüfe PostgreSQL..."
if (Test-Port -Port 5432) {
    Write-Success "PostgreSQL läuft"
} else {
    Write-Error "PostgreSQL läuft nicht! Bitte PostgreSQL-Dienst starten."
    Write-Info "services.msc öffnen und PostgreSQL-Dienst starten"
    exit 1
}

# Redis prüfen
Write-Info "Prüfe Redis/Memurai..."
if (Test-Port -Port 6379) {
    Write-Success "Redis/Memurai läuft"
} else {
    Write-Warning "Redis/Memurai läuft nicht"
    Write-Info "Celery funktioniert möglicherweise nicht ohne Redis"
}

# Node.js prüfen
Write-Info "Prüfe Node.js..."
try {
    $nodeVersion = node --version 2>&1
    Write-Success "Node.js installiert: $nodeVersion"
} catch {
    Write-Error "Node.js ist nicht installiert!"
    exit 1
}

# Prozesse auf Ports beenden falls belegt
Write-Header "Ports freigeben"
$portsToKill = @(8000, 3000)
foreach ($port in $portsToKill) {
    if (Test-Port -Port $port) {
        Write-Warning "Port $port ist belegt, stoppe Prozess..."
        try {
            $processId = (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue).OwningProcess
            if ($processId) {
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
                Write-Success "Prozess auf Port $port gestoppt"
            }
        } catch {
            Write-Warning "Konnte Prozess auf Port $port nicht stoppen"
        }
    }
}

# Python-Abhängigkeiten installieren
Write-Header "Python-Abhängigkeiten installieren"
Push-Location $BackendDir
try {
    Write-Info "Aktiviere virtuelle Umgebung..."
    & .\venv\Scripts\Activate.ps1
    
    Write-Info "Aktualisiere pip..."
    python -m pip install --upgrade pip --quiet
    
    Write-Info "Prüfe Python-Pakete..."
    $pipList = python -m pip list 2>&1 | Out-String
    
    # Prüfen ob erforderliche Pakete installiert sind
    $needsInstall = $false
    $requiredPackages = @("fastapi", "uvicorn", "sqlalchemy", "asyncpg", "python-jose", "passlib")
    
    foreach ($pkg in $requiredPackages) {
        if (-not ($pipList -match $pkg)) {
            Write-Warning "Paket '$pkg' nicht gefunden"
            $needsInstall = $true
            break
        }
    }
    
    if ($needsInstall) {
        Write-Info "Installiere Python-Abhängigkeiten (kann 5-10 Minuten dauern)..."
        Write-Host "  Bitte warten, installiere: FastAPI, SQLAlchemy, Celery, etc..." -ForegroundColor Yellow
        Write-Host "  Dies ist eine EINMALIGE Installation, nachfolgende Starts sind schnell" -ForegroundColor Yellow
        python -m pip install -r requirements.txt
        Write-Success "Python-Abhängigkeiten erfolgreich installiert!"
    } else {
        Write-Success "Alle Python-Abhängigkeiten sind installiert"
    }
} catch {
    Write-Warning "Problem bei Abhängigkeitsinstallation: $_"
    Write-Info "Versuche trotzdem zu installieren..."
    python -m pip install -r requirements.txt
} finally {
    Pop-Location
}

# Datenbank initialisieren
Write-Header "Datenbank initialisieren"
Push-Location $BackendDir
try {
    Write-Info "Aktiviere virtuelle Umgebung..."
    & .\venv\Scripts\Activate.ps1
    
    Write-Info "Prüfe Datenbankinitialisierung..."
    $initOutput = python init_db.py 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0 -or $initOutput -match "already exists") {
        Write-Success "Datenbank ist bereit"
    } else {
        Write-Warning "Problem bei Datenbankinitialisierung (wird fortgesetzt)"
        Write-Host $initOutput -ForegroundColor Gray
    }
} catch {
    Write-Warning "Datenbankinitialisierung fehlgeschlagen: $_"
} finally {
    Pop-Location
}

# Backend API starten
Write-Header "Backend API starten"
Write-Info "Starte FastAPI-Server auf Port 8000..."

$backendScript = @'
$host.UI.RawUI.WindowTitle = 'CryptoCRM - Backend API'
Write-Host '========================================' -ForegroundColor Green
Write-Host '   CryptoCRM Backend API Server' -ForegroundColor Green  
Write-Host '========================================' -ForegroundColor Green
Write-Host ''
Set-Location '{0}'
Write-Host 'Aktiviere virtuelle Umgebung...' -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1
Write-Host ''
Write-Host 'Starte FastAPI-Server...' -ForegroundColor Cyan
Write-Host 'API Docs: http://localhost:8000/api/v1/docs' -ForegroundColor Yellow
Write-Host 'Backend: http://localhost:8000' -ForegroundColor Yellow
Write-Host ''
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
'@ -f $BackendDir

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Start-Sleep -Seconds 3

# Auf Backend warten
if (-not (Wait-ForPort -Port 8000 -TimeoutSeconds 30 -ServiceName "Backend API")) {
    Write-Error "Backend wurde nicht gestartet"
    exit 1
}

# Celery Worker starten (optional, nur wenn Redis läuft)
if (Test-Port -Port 6379) {
    Write-Header "Celery Worker starten"
    Write-Info "Starte Hintergrundaufgaben..."
    
    $celeryScript = @'
$host.UI.RawUI.WindowTitle = 'CryptoCRM - Celery Worker'
Write-Host '========================================' -ForegroundColor Green
Write-Host '   CryptoCRM Celery Worker' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Green
Write-Host ''
Set-Location '{0}'
Write-Host 'Aktiviere virtuelle Umgebung...' -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1
Write-Host 'Starte Celery Worker...' -ForegroundColor Cyan
Write-Host ''
python -m celery -A app.worker.celery_app worker --loglevel=info --pool=solo
'@ -f $BackendDir

    Start-Process powershell -ArgumentList "-NoExit", "-Command", $celeryScript
    Write-Success "Celery Worker gestartet"
    Start-Sleep -Seconds 2
} else {
    Write-Warning "Überspringe Celery Worker (Redis nicht verfügbar)"
}

# node_modules prüfen
Write-Header "Frontend prüfen"
Push-Location $FrontendDir
try {
    if (-not (Test-Path "node_modules")) {
        Write-Info "Installiere npm-Abhängigkeiten (kann eine Weile dauern)..."
        npm install
        Write-Success "Abhängigkeiten installiert"
    } else {
        Write-Success "npm-Abhängigkeiten bereits installiert"
    }
} catch {
    Write-Warning "npm install fehlgeschlagen: $_"
} finally {
    Pop-Location
}

# Frontend starten
Write-Header "Frontend starten"
Write-Info "Starte React-Entwicklungsserver..."

$frontendScript = @'
$host.UI.RawUI.WindowTitle = 'CryptoCRM - Frontend'
Write-Host '========================================' -ForegroundColor Green
Write-Host '   CryptoCRM Frontend (React)' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Green
Write-Host ''
cd '{0}'
Write-Host 'Starte React-Entwicklungsserver...' -ForegroundColor Cyan
Write-Host 'URL: http://localhost:3000' -ForegroundColor Yellow
Write-Host ''
npm start
'@ -f $FrontendDir

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Start-Sleep -Seconds 3

# Auf Frontend warten
if (-not (Wait-ForPort -Port 3000 -TimeoutSeconds 45 -ServiceName "Frontend")) {
    Write-Warning "Frontend startet möglicherweise noch..."
}

# Abschlussinformationen
Write-Host ""
Write-Header "Alle Dienste gestartet!"
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   CryptoCRM erfolgreich gestartet!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Info "Verfügbare URLs:"
Write-Host "  Frontend:           http://localhost:3000" -ForegroundColor Yellow
Write-Host "  Backend API:        http://localhost:8000" -ForegroundColor Yellow
Write-Host "  API Docs (Swagger): http://localhost:8000/api/v1/docs" -ForegroundColor Yellow
Write-Host ""
Write-Info "Standard-Anmeldedaten:"
Write-Host "  E-Mail:   admin@cryptocrm.com" -ForegroundColor Cyan
Write-Host "  Passwort: admin123" -ForegroundColor Cyan
Write-Host ""
Write-Warning "Zum Beenden: Alle PowerShell-Fenster schließen"
Write-Host ""

# Browser öffnen
if (-not $SkipBrowser) {
    Write-Info "Öffne Browser in 3 Sekunden..."
    Start-Sleep -Seconds 3
    
    # Frontend öffnen
    Start-Process "http://localhost:3000"
    
    Start-Sleep -Seconds 2
    
    # API Docs in neuem Tab öffnen
    Start-Process "http://localhost:8000/api/v1/docs"
    
    Write-Success "Browser geöffnet!"
}

Write-Host ""
Write-Host "Drücken Sie eine beliebige Taste zum Beenden dieses Fensters..." -ForegroundColor Gray
Write-Host "(Dienste laufen in anderen Fenstern weiter)" -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

