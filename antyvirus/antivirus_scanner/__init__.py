"""
Process Scanner - A professional security monitoring tool.

This package provides functionality for scanning system processes
and detecting suspicious activity based on configurable criteria.
"""

__version__ = "1.0.0"
__author__ = "Andrii Banduliak"
__email__ = ""

from antivirus_scanner.scanner import ProcessScanner, ProcessInfo
from antivirus_scanner.config import ConfigManager
from antivirus_scanner.exceptions import (
    ScannerError,
    ConfigError,
    ScanError,
    ProcessAccessError
)

__all__ = [
    "ProcessScanner",
    "ProcessInfo",
    "ConfigManager",
    "ScannerError",
    "ConfigError",
    "ScanError",
    "ProcessAccessError",
]

