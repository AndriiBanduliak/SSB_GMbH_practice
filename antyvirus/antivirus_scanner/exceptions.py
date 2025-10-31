"""Custom exceptions for the antivirus scanner."""


class ScannerError(Exception):
    """Base exception for scanner-related errors."""
    pass


class ConfigError(ScannerError):
    """Raised when configuration loading or validation fails."""
    pass


class ScanError(ScannerError):
    """Raised when a scan operation fails."""
    pass


class ProcessAccessError(ScannerError):
    """Raised when access to a process is denied or fails."""
    pass

