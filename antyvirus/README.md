# Process Security Scanner

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A professional, production-ready security monitoring tool that scans system processes and detects suspicious activity based on configurable criteria. Built with Python and designed for security professionals and system administrators.

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Development](#-development)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

## ✨ Features

- **🔍 Real-time Process Scanning**: Monitors all running system processes
- **⚙️ Configurable Detection**: Customizable suspicious keywords and whitelist
- **📊 Comprehensive Logging**: Detailed logs with configurable levels
- **🛡️ Robust Error Handling**: Graceful handling of access denied and process errors
- **🎯 Whitelist Support**: Exclude trusted processes from scanning
- **📈 Performance Optimized**: Efficient scanning using `psutil`
- **🔧 CLI Interface**: Easy-to-use command-line interface
- **✅ Type Hints**: Full type annotations for better code quality
- **🧪 Test Coverage**: Comprehensive unit tests

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/AndriiBanduliak/antyvirus.git
cd antyvirus
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🏃 Quick Start

1. **Configure the scanner** by editing `config.json`:
```json
{
    "keywords": ["suspicious", "hack", "malware", "trojan"],
    "whitelist": ["system.exe", "explorer.exe"],
    "scan_interval": 60,
    "log_level": "INFO"
}
```

2. **Run the scanner**:
```bash
python main.py
```

3. **Check the results**:
   - Console output shows real-time scan results
   - Detailed logs are written to `antivirus.log`

## ⚙️ Configuration

The scanner uses a JSON configuration file (`config.json`) with the following options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `keywords` | `List[str]` | Suspicious keywords to detect in process names | `[]` |
| `whitelist` | `List[str]` | Process names to exclude from scanning | `[]` |
| `scan_interval` | `int` | Interval between scans in seconds (for future daemon mode) | `60` |
| `log_level` | `str` | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL | `"INFO"` |

### Example Configuration

```json
{
    "keywords": [
        "suspicious",
        "hack",
        "malware",
        "trojan",
        "virus",
        "spyware"
    ],
    "whitelist": [
        "system.exe",
        "explorer.exe",
        "svchost.exe",
        "winlogon.exe"
    ],
    "scan_interval": 60,
    "log_level": "INFO"
}
```

## 💻 Usage

### Basic Usage

```bash
# Run a single scan
python main.py

# Scan with verbose logging
python main.py --log-level DEBUG

# Specify custom config file
python main.py --config custom_config.json
```

### Return Codes

- `0`: Success - No suspicious processes found
- `1`: Warning - Suspicious processes detected or error occurred

### Integration Examples

#### Bash Script

```bash
#!/bin/bash
python main.py
if [ $? -eq 1 ]; then
    echo "Alert: Suspicious processes detected!"
    # Add your notification logic here
fi
```

#### Python Integration

```python
from antivirus_scanner.config import ConfigManager
from antivirus_scanner.scanner import ProcessScanner

# Load configuration
config = ConfigManager('config.json').load()

# Initialize scanner
scanner = ProcessScanner(
    suspicious_keywords=ConfigManager('config.json').suspicious_keywords,
    whitelist=ConfigManager('config.json').whitelist
)

# Perform scan
findings = scanner.scan()
if findings:
    print(f"Found {len(findings)} suspicious processes")
```

## 🛠️ Development

### Project Structure

```
antyvirus/
├── antivirus_scanner/       # Main package
│   ├── __init__.py
│   ├── scanner.py          # Process scanning logic
│   ├── config.py           # Configuration management
│   └── logger_config.py    # Logging setup
├── tests/                  # Unit tests
│   ├── __init__.py
│   ├── test_scanner.py
│   ├── test_config.py
│   └── test_integration.py
├── main.py                 # Entry point
├── config.json            # Configuration file
├── requirements.txt       # Dependencies
├── pyproject.toml        # Project metadata
├── .gitignore           # Git ignore rules
├── README.md           # This file
└── LICENSE             # License file
```

### Code Style

This project follows PEP 8 style guidelines and uses:
- **Black** for code formatting
- **mypy** for type checking
- **flake8** for linting

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run code formatter
black .

# Run type checker
mypy antivirus_scanner/

# Run linter
flake8 antivirus_scanner/
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=antivirus_scanner --cov-report=html

# Run specific test file
pytest tests/test_scanner.py -v
```

### Test Coverage

The project aims for >80% test coverage. View the HTML coverage report:
```bash
pytest --cov=antivirus_scanner --cov-report=html
open htmlcov/index.html  # or open in browser
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Andrii Banduliak**

- GitHub: [@AndriiBanduliak](https://github.com/AndriiBanduliak)
- Profile: [https://github.com/AndriiBanduliak](https://github.com/AndriiBanduliak)

## 🙏 Acknowledgments

- Built with [psutil](https://github.com/giampaolo/psutil) for cross-platform system process utilities
- Inspired by security monitoring best practices

---

**⭐ If you find this project useful, please consider giving it a star!**

## 📚 Additional Resources

- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE)

## 🔗 Related Projects

Check out other projects by [@AndriiBanduliak](https://github.com/AndriiBanduliak) on GitHub!

