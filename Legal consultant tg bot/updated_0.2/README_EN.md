# Legal Consultant Telegram Bot

A professional AI-powered legal consultation bot built with Python and Telegram Bot API. The bot provides legal advice, document analysis, contract generation, and formal request drafting in multiple languages.

## Features

### 🤖 AI-Powered Legal Assistant
- **Legal Questions**: Get detailed answers to legal questions using OpenAI GPT-4o-mini
- **Document Analysis**: Upload and analyze legal documents (.txt, .docx, .pdf)
- **Document Editing**: Request specific changes to legal documents
- **Contract Generation**: Create professional legal contracts
- **Formal Request Drafting**: Generate advocate requests and legal documents

### 🌍 Multi-Language Support
- **Ukrainian** (Українська) - Primary language
- **English** - Full translation
- **German** (Deutsch) - Full translation

### 📊 User Management
- Daily usage limits (configurable)
- User statistics tracking
- Contact information collection
- Language preferences

### 🛡️ Stability & Reliability
- Comprehensive error handling
- Database connection management
- API timeout protection
- Graceful fallback mechanisms
- Detailed logging system

## Technology Stack

- **Backend**: Python 3.8+
- **Bot Framework**: python-telegram-bot
- **AI Integration**: OpenAI GPT-4o-mini
- **Database**: SQLite
- **Document Processing**: python-docx, PyPDF2
- **Logging**: Python logging module
- **Environment**: python-dotenv

## Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Legal consultant tg bot/updated_0.2"
   ```

2. **Install dependencies**
   ```bash
   pip install python-telegram-bot openai python-dotenv python-docx PyPDF2 num2words
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4o-mini
   DB_NAME=multilang_bot.db
   LOG_LEVEL=INFO
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `DB_NAME` | SQLite database filename | `multilang_bot.db` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |

### Usage Limits

Configure daily limits in `config.py`:
```python
DAILY_QUESTION_LIMIT = 10  # Questions per day per user
DAILY_DOCUMENT_LIMIT = 10  # Document processing per day per user
```

## Project Structure

```
updated_0.2/
├── main.py                    # Main application entry point
├── config.py                  # Configuration and translations
├── database.py                # Database management
├── openai_service.py          # OpenAI API integration
├── error_handler.py           # Error handling utilities
├── utils.py                   # Utility functions
├── document_processor.py      # Document processing
├── keyboards.py               # Telegram keyboard layouts
├── handlers/                  # Bot command handlers
│   ├── __init__.py
│   ├── common.py             # Common handlers
│   ├── ai_interaction.py     # AI interaction handlers
│   ├── request_creation.py   # Request creation handlers
│   └── contract_creation.py  # Contract creation handlers
├── multilang_bot.db          # SQLite database
└── STABILITY_IMPROVEMENTS.md # Stability improvements documentation
```

## Usage

### Bot Commands

- `/start` - Initialize the bot and select language
- `/skip` - Skip optional fields in forms

### Bot Features

1. **Language Selection**: Choose your preferred language (Ukrainian, English, German)
2. **Main Menu**: Access all bot features through the main menu
3. **Legal Questions**: Ask legal questions and get AI-powered answers
4. **Document Analysis**: Upload documents for AI analysis
5. **Document Editing**: Request specific changes to documents
6. **Contract Generation**: Create professional legal contracts
7. **Request Drafting**: Generate formal advocate requests
8. **Contact Sharing**: Share contact information for better communication

### Supported Document Formats

- **Text files** (.txt)
- **Word documents** (.docx)
- **PDF files** (.pdf)
- **Maximum file size**: 20 MB

## API Integration

### OpenAI Integration

The bot uses OpenAI's GPT-4o-mini model for:
- Legal question answering
- Document analysis and editing
- Contract generation
- Request drafting

### Telegram Bot API

Features implemented:
- Inline keyboards for navigation
- Reply keyboards for contact sharing
- File upload handling
- Message editing and deletion
- Chat actions (typing indicators)

## Database Schema

### Users Table

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER PRIMARY KEY | Telegram user ID |
| `username` | TEXT | Telegram username |
| `first_name` | TEXT | User's first name |
| `phone_number` | TEXT | User's phone number |
| `questions_count` | INTEGER | Daily question count |
| `documents_count` | INTEGER | Daily document count |
| `last_reset_date` | TEXT | Last limit reset date |
| `language_code` | TEXT | User's language preference |

## Error Handling

The bot includes comprehensive error handling:

- **Database errors**: Graceful fallback to default values
- **API timeouts**: 60-second timeout with retry mechanisms
- **Network issues**: Automatic retry with exponential backoff
- **Invalid input**: User-friendly error messages
- **File processing**: Support for various file formats with error recovery

## Logging

The bot uses Python's built-in logging module with configurable levels:

- **DEBUG**: Detailed debugging information
- **INFO**: General operational messages
- **WARNING**: Warning messages
- **ERROR**: Error conditions
- **CRITICAL**: Critical errors requiring immediate attention

## Security Considerations

- **API Keys**: Stored in environment variables, never in code
- **User Data**: Stored locally in SQLite database
- **File Uploads**: Validated file types and size limits
- **Rate Limiting**: Daily usage limits per user
- **Error Messages**: Generic error messages to prevent information leakage

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

⚠️ **Important**: This bot provides informational legal assistance only. All responses are for informational purposes and do not constitute legal advice. For important legal decisions, always consult with qualified legal professionals.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation in `STABILITY_IMPROVEMENTS.md`

## Changelog

### Version 0.2
- ✅ Improved stability and error handling
- ✅ Added comprehensive logging
- ✅ Enhanced database error recovery
- ✅ Added API timeout protection
- ✅ Updated bot greeting to "Bandul Consultant"
- ✅ Created professional documentation

---

**Bandul Consultant** - Your AI Legal Assistant 🤖⚖️
