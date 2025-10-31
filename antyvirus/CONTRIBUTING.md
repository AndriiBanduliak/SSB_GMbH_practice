# Contributing to Process Security Scanner

Thank you for your interest in contributing to the Process Security Scanner project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its benefits
3. Consider implementation approach

### Pull Requests

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/antyvirus.git
   cd antyvirus
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Make Changes**
   - Write clean, readable code
   - Add tests for new features
   - Update documentation
   - Follow code style guidelines

5. **Run Tests**
   ```bash
   pytest
   pytest --cov=antivirus_scanner --cov-report=html
   ```

6. **Run Linters**
   ```bash
   black antivirus_scanner tests
   flake8 antivirus_scanner tests
   mypy antivirus_scanner
   ```

7. **Commit Changes**
   ```bash
   git commit -m "Add feature: description"
   ```

8. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## Code Style

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Write docstrings for all public functions/classes
- Keep functions focused and small

### Formatting

We use **Black** for code formatting:
```bash
black antivirus_scanner tests
```

### Type Checking

We use **mypy** for type checking:
```bash
mypy antivirus_scanner
```

### Linting

We use **flake8** for linting:
```bash
flake8 antivirus_scanner tests --max-line-length=100
```

## Testing Guidelines

- Write tests for new features
- Aim for >80% code coverage
- Use descriptive test names
- Test edge cases and error conditions

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=antivirus_scanner --cov-report=html

# Run specific test file
pytest tests/test_scanner.py -v

# Run with verbose output
pytest -v
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update type hints
- Keep comments clear and concise

## Commit Messages

Use clear, descriptive commit messages:

```
Add feature: Process filtering by memory usage
Fix bug: Handle AccessDenied exceptions gracefully
Update docs: Add installation instructions for macOS
Refactor: Improve config validation logic
```

## Review Process

1. Your PR will be reviewed by maintainers
2. Address any feedback or requested changes
3. Once approved, your PR will be merged

## Questions?

Feel free to open an issue for questions or reach out to the maintainers.

Thank you for contributing! 🎉

