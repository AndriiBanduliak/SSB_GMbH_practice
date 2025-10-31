# Rechtsberatungs-Telegram-Bot

Ein professioneller KI-gestützter Rechtsberatungsbot, entwickelt mit Python und der Telegram Bot API. Der Bot bietet Rechtsberatung, Dokumentenanalyse, Vertragserstellung und die Erstellung formeller Anträge in mehreren Sprachen.

## Funktionen

### 🤖 KI-gestützter Rechtsassistent
- **Rechtsfragen**: Erhalten Sie detaillierte Antworten auf Rechtsfragen mit OpenAI GPT-4o-mini
- **Dokumentenanalyse**: Laden Sie rechtliche Dokumente hoch und lassen Sie sie analysieren (.txt, .docx, .pdf)
- **Dokumentenbearbeitung**: Fordern Sie spezifische Änderungen an rechtlichen Dokumenten an
- **Vertragserstellung**: Erstellen Sie professionelle Rechtsverträge
- **Formelle Antragserstellung**: Generieren Sie Anwaltsanfragen und rechtliche Dokumente

### 🌍 Mehrsprachige Unterstützung
- **Ukrainisch** (Українська) - Hauptsprache
- **Englisch** - Vollständige Übersetzung
- **Deutsch** - Vollständige Übersetzung

### 📊 Benutzerverwaltung
- Tägliche Nutzungslimits (konfigurierbar)
- Benutzerstatistiken-Tracking
- Kontaktinformationssammlung
- Sprachpräferenzen

### 🛡️ Stabilität & Zuverlässigkeit
- Umfassende Fehlerbehandlung
- Datenbankverbindungsmanagement
- API-Timeout-Schutz
- Elegante Fallback-Mechanismen
- Detailliertes Protokollierungssystem

## Technologie-Stack

- **Backend**: Python 3.8+
- **Bot-Framework**: python-telegram-bot
- **KI-Integration**: OpenAI GPT-4o-mini
- **Datenbank**: SQLite
- **Dokumentenverarbeitung**: python-docx, PyPDF2
- **Protokollierung**: Python logging-Modul
- **Umgebung**: python-dotenv

## Installation

### Voraussetzungen
- Python 3.8 oder höher
- Telegram Bot Token (von [@BotFather](https://t.me/botfather))
- OpenAI API-Schlüssel

### Einrichtung

1. **Repository klonen**
   ```bash
   git clone <repository-url>
   cd "Legal consultant tg bot/updated_0.2"
   ```

2. **Abhängigkeiten installieren**
   ```bash
   pip install python-telegram-bot openai python-dotenv python-docx PyPDF2 num2words
   ```

3. **Umgebungsvariablen konfigurieren**
   Erstellen Sie eine `.env`-Datei im Projektverzeichnis:
   ```env
   TELEGRAM_BOT_TOKEN=ihr_telegram_bot_token
   OPENAI_API_KEY=ihr_openai_api_schluessel
   OPENAI_MODEL=gpt-4o-mini
   DB_NAME=multilang_bot.db
   LOG_LEVEL=INFO
   ```

4. **Bot starten**
   ```bash
   python main.py
   ```

## Konfiguration

### Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token von BotFather | Erforderlich |
| `OPENAI_API_KEY` | OpenAI API-Schlüssel | Erforderlich |
| `OPENAI_MODEL` | Zu verwendendes OpenAI-Modell | `gpt-4o-mini` |
| `DB_NAME` | SQLite-Datenbankdateiname | `multilang_bot.db` |
| `LOG_LEVEL` | Protokollierungsstufe (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |

### Nutzungslimits

Konfigurieren Sie tägliche Limits in `config.py`:
```python
DAILY_QUESTION_LIMIT = 10  # Fragen pro Tag pro Benutzer
DAILY_DOCUMENT_LIMIT = 10  # Dokumentenverarbeitung pro Tag pro Benutzer
```

## Projektstruktur

```
updated_0.2/
├── main.py                    # Hauptanwendungseinstiegspunkt
├── config.py                  # Konfiguration und Übersetzungen
├── database.py                # Datenbankverwaltung
├── openai_service.py          # OpenAI API-Integration
├── error_handler.py           # Fehlerbehandlungs-Utilities
├── utils.py                   # Hilfsfunktionen
├── document_processor.py      # Dokumentenverarbeitung
├── keyboards.py               # Telegram-Tastaturlayouts
├── handlers/                  # Bot-Befehls-Handler
│   ├── __init__.py
│   ├── common.py             # Allgemeine Handler
│   ├── ai_interaction.py     # KI-Interaktions-Handler
│   ├── request_creation.py   # Antragserstellungs-Handler
│   └── contract_creation.py  # Vertragserstellungs-Handler
├── multilang_bot.db          # SQLite-Datenbank
└── STABILITY_IMPROVEMENTS.md # Dokumentation der Stabilitätsverbesserungen
```

## Verwendung

### Bot-Befehle

- `/start` - Bot initialisieren und Sprache auswählen
- `/skip` - Optionale Felder in Formularen überspringen

### Bot-Funktionen

1. **Sprachauswahl**: Wählen Sie Ihre bevorzugte Sprache (Ukrainisch, Englisch, Deutsch)
2. **Hauptmenü**: Zugriff auf alle Bot-Funktionen über das Hauptmenü
3. **Rechtsfragen**: Stellen Sie Rechtsfragen und erhalten Sie KI-gestützte Antworten
4. **Dokumentenanalyse**: Laden Sie Dokumente für KI-Analyse hoch
5. **Dokumentenbearbeitung**: Fordern Sie spezifische Änderungen an Dokumenten an
6. **Vertragserstellung**: Erstellen Sie professionelle Rechtsverträge
7. **Antragserstellung**: Generieren Sie formelle Anwaltsanfragen
8. **Kontaktfreigabe**: Teilen Sie Kontaktinformationen für bessere Kommunikation

### Unterstützte Dokumentformate

- **Textdateien** (.txt)
- **Word-Dokumente** (.docx)
- **PDF-Dateien** (.pdf)
- **Maximale Dateigröße**: 20 MB

## API-Integration

### OpenAI-Integration

Der Bot verwendet OpenAIs GPT-4o-mini-Modell für:
- Beantwortung von Rechtsfragen
- Dokumentenanalyse und -bearbeitung
- Vertragserstellung
- Antragserstellung

### Telegram Bot API

Implementierte Funktionen:
- Inline-Tastaturen für Navigation
- Antwort-Tastaturen für Kontaktfreigabe
- Datei-Upload-Behandlung
- Nachrichtenbearbeitung und -löschung
- Chat-Aktionen (Tipp-Indikatoren)

## Datenbankschema

### Benutzertabelle

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `user_id` | INTEGER PRIMARY KEY | Telegram-Benutzer-ID |
| `username` | TEXT | Telegram-Benutzername |
| `first_name` | TEXT | Vorname des Benutzers |
| `phone_number` | TEXT | Telefonnummer des Benutzers |
| `questions_count` | INTEGER | Tägliche Fragenanzahl |
| `documents_count` | INTEGER | Tägliche Dokumentenanzahl |
| `last_reset_date` | TEXT | Datum des letzten Limit-Resets |
| `language_code` | TEXT | Sprachpräferenz des Benutzers |

## Fehlerbehandlung

Der Bot umfasst umfassende Fehlerbehandlung:

- **Datenbankfehler**: Elegante Fallback auf Standardwerte
- **API-Timeouts**: 60-Sekunden-Timeout mit Wiederholungsmechanismen
- **Netzwerkprobleme**: Automatische Wiederholung mit exponentieller Backoff
- **Ungültige Eingaben**: Benutzerfreundliche Fehlermeldungen
- **Dateiverarbeitung**: Unterstützung für verschiedene Dateiformate mit Fehlerwiederherstellung

## Protokollierung

Der Bot verwendet Pythons eingebautes Protokollierungsmodul mit konfigurierbaren Stufen:

- **DEBUG**: Detaillierte Debugging-Informationen
- **INFO**: Allgemeine Betriebsmeldungen
- **WARNING**: Warnmeldungen
- **ERROR**: Fehlerbedingungen
- **CRITICAL**: Kritische Fehler, die sofortige Aufmerksamkeit erfordern

## Sicherheitsüberlegungen

- **API-Schlüssel**: In Umgebungsvariablen gespeichert, niemals im Code
- **Benutzerdaten**: Lokal in SQLite-Datenbank gespeichert
- **Datei-Uploads**: Validierte Dateitypen und Größenlimits
- **Rate-Limiting**: Tägliche Nutzungslimits pro Benutzer
- **Fehlermeldungen**: Generische Fehlermeldungen zur Verhinderung von Informationslecks

## Beitragen

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/erstaunliche-funktion`)
3. Committen Sie Ihre Änderungen (`git commit -m 'Erstaunliche Funktion hinzufügen'`)
4. Pushen Sie zum Branch (`git push origin feature/erstaunliche-funktion`)
5. Öffnen Sie einen Pull Request

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die LICENSE-Datei für Details.

## Haftungsausschluss

⚠️ **Wichtig**: Dieser Bot bietet nur informelle Rechtsberatung. Alle Antworten dienen nur zu Informationszwecken und stellen keine Rechtsberatung dar. Für wichtige Rechtsentscheidungen wenden Sie sich immer an qualifizierte Rechtsanwälte.

## Support

Für Support und Fragen:
- Erstellen Sie ein Issue im Repository
- Kontaktieren Sie das Entwicklungsteam
- Überprüfen Sie die Dokumentation in `STABILITY_IMPROVEMENTS.md`

## Changelog

### Version 0.2
- ✅ Verbesserte Stabilität und Fehlerbehandlung
- ✅ Umfassende Protokollierung hinzugefügt
- ✅ Erweiterte Datenbankfehler-Wiederherstellung
- ✅ API-Timeout-Schutz hinzugefügt
- ✅ Bot-Begrüßung auf "Bandul Berater" aktualisiert
- ✅ Professionelle Dokumentation erstellt

---

**Bandul Berater** - Ihr KI-Rechtsassistent 🤖⚖️
