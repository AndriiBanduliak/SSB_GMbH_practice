"""Configuration management module for the process scanner."""

import json
import logging
from pathlib import Path
from typing import Dict, Set, Any, Optional

from antivirus_scanner.exceptions import ConfigError

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages loading and validation of configuration file."""
    
    DEFAULT_CONFIG = {
        "keywords": [],
        "whitelist": [],
        "scan_interval": 60,
        "log_level": "INFO"
    }
    
    def __init__(self, config_path: Path) -> None:
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to the JSON configuration file.
            
        Raises:
            ConfigError: If configuration file is invalid or missing.
        """
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dictionary containing configuration settings.
            
        Raises:
            ConfigError: If configuration cannot be loaded or is invalid.
        """
        if not self.config_path.exists():
            raise ConfigError(f"Configuration file not found: {self.config_path}")
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in configuration file: {e}")
        except IOError as e:
            raise ConfigError(f"Error reading configuration file: {e}")
            
        self._validate()
        self._merge_defaults()
        
        logger.info(f"Configuration loaded successfully from {self.config_path}")
        return self._config
    
    def _validate(self) -> None:
        """Validate configuration structure."""
        required_keys = ['keywords', 'whitelist']
        missing_keys = [key for key in required_keys if key not in self._config]
        
        if missing_keys:
            logger.warning(
                f"Missing configuration keys: {missing_keys}. "
                f"Using empty lists as defaults."
            )
        
        # Validate types
        if 'keywords' in self._config and not isinstance(self._config['keywords'], list):
            raise ConfigError("'keywords' must be a list")
        if 'whitelist' in self._config and not isinstance(self._config['whitelist'], list):
            raise ConfigError("'whitelist' must be a list")
    
    def _merge_defaults(self) -> None:
        """Merge default values for missing configuration keys."""
        for key, default_value in self.DEFAULT_CONFIG.items():
            if key not in self._config:
                self._config[key] = default_value
                logger.debug(f"Using default value for '{key}': {default_value}")
    
    @property
    def suspicious_keywords(self) -> Set[str]:
        """Get set of suspicious keywords."""
        keywords = self._config.get('keywords', [])
        return {kw.lower() for kw in keywords if isinstance(kw, str)}
    
    @property
    def whitelist(self) -> Set[str]:
        """Get set of whitelisted process names."""
        whitelist = self._config.get('whitelist', [])
        return {name.lower() for name in whitelist if isinstance(name, str)}
    
    @property
    def scan_interval(self) -> int:
        """Get scan interval in seconds."""
        return self._config.get('scan_interval', 60)
    
    @property
    def log_level(self) -> str:
        """Get log level."""
        return self._config.get('log_level', 'INFO')

