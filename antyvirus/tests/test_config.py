"""Tests for configuration management module."""

import json
import tempfile
from pathlib import Path
import pytest

from antivirus_scanner.config import ConfigManager
from antivirus_scanner.exceptions import ConfigError


class TestConfigManager:
    """Test suite for ConfigManager class."""

    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        config_data = {
            "keywords": ["test", "malware"],
            "whitelist": ["system.exe"],
            "scan_interval": 30,
            "log_level": "DEBUG"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            manager = ConfigManager(config_path)
            config = manager.load()
            
            assert config == config_data
            assert manager.suspicious_keywords == {"test", "malware"}
            assert manager.whitelist == {"system.exe"}
            assert manager.scan_interval == 30
            assert manager.log_level == "DEBUG"
        finally:
            config_path.unlink()

    def test_load_missing_file(self):
        """Test error handling for missing configuration file."""
        config_path = Path("nonexistent_config.json")
        manager = ConfigManager(config_path)
        
        with pytest.raises(ConfigError, match="Configuration file not found"):
            manager.load()

    def test_load_invalid_json(self):
        """Test error handling for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            config_path = Path(f.name)
        
        try:
            manager = ConfigManager(config_path)
            with pytest.raises(ConfigError, match="Invalid JSON"):
                manager.load()
        finally:
            config_path.unlink()

    def test_merge_defaults(self):
        """Test merging default values for missing keys."""
        config_data = {"keywords": ["test"]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            manager = ConfigManager(config_path)
            config = manager.load()
            
            assert "whitelist" in config
            assert config["whitelist"] == []
            assert "scan_interval" in config
            assert config["scan_interval"] == 60
            assert "log_level" in config
            assert config["log_level"] == "INFO"
        finally:
            config_path.unlink()

    def test_keywords_property_lowercase(self):
        """Test that keywords are converted to lowercase."""
        config_data = {
            "keywords": ["TEST", "Malware", "spyware"],
            "whitelist": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            manager = ConfigManager(config_path)
            manager.load()
            
            assert manager.suspicious_keywords == {"test", "malware", "spyware"}
        finally:
            config_path.unlink()

    def test_whitelist_property_lowercase(self):
        """Test that whitelist items are converted to lowercase."""
        config_data = {
            "keywords": [],
            "whitelist": ["SYSTEM.EXE", "Explorer.exe"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            manager = ConfigManager(config_path)
            manager.load()
            
            assert manager.whitelist == {"system.exe", "explorer.exe"}
        finally:
            config_path.unlink()

    def test_invalid_keywords_type(self):
        """Test error handling for invalid keywords type."""
        config_data = {"keywords": "not a list", "whitelist": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            manager = ConfigManager(config_path)
            with pytest.raises(ConfigError, match="must be a list"):
                manager.load()
        finally:
            config_path.unlink()

    def test_invalid_whitelist_type(self):
        """Test error handling for invalid whitelist type."""
        config_data = {"keywords": [], "whitelist": "not a list"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            manager = ConfigManager(config_path)
            with pytest.raises(ConfigError, match="must be a list"):
                manager.load()
        finally:
            config_path.unlink()

    def test_filter_non_string_keywords(self):
        """Test filtering out non-string keywords."""
        config_data = {
            "keywords": ["test", 123, None, "malware", [], "valid"],
            "whitelist": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            manager = ConfigManager(config_path)
            manager.load()
            
            # Should only contain string keywords
            assert manager.suspicious_keywords == {"test", "malware", "valid"}
        finally:
            config_path.unlink()

