# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of Process Security Scanner
- Process scanning functionality with configurable keywords
- Whitelist support for trusted processes
- Comprehensive logging system with configurable levels
- CLI interface with argument parsing
- Configuration management with JSON files
- Custom exception classes for better error handling
- Unit tests with pytest
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks for code quality
- Professional documentation and README
- Type hints throughout the codebase

### Features
- Real-time process scanning using psutil
- Case-insensitive keyword matching
- Process information extraction (PID, name, path, cmdline)
- Graceful error handling for access denied and missing processes
- Configurable log levels and output destinations
- Command-line interface with multiple options

### Documentation
- Comprehensive README with installation and usage instructions
- Contributing guidelines
- Code examples and integration guides
- Project structure documentation

### Testing
- Unit tests for configuration management
- Unit tests for process scanner
- Integration tests for full workflow
- Test coverage reporting

### Infrastructure
- GitHub Actions CI/CD workflow
- Pre-commit hooks configuration
- Modern Python packaging with pyproject.toml
- Development dependencies management

---

## [Unreleased]

### Planned
- Daemon mode for continuous monitoring
- Alerting mechanisms (email, webhooks)
- Process signature matching
- Performance metrics and reporting
- GUI interface option
- Windows service support
- Configuration file validation schema

[1.0.0]: https://github.com/AndriiBanduliak/antyvirus/releases/tag/v1.0.0

