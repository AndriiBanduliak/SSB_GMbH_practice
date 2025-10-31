"""Integration tests for the antivirus scanner."""

import json
import tempfile
from pathlib import Path
import pytest

from antivirus_scanner.config import ConfigManager
from antivirus_scanner.scanner import ProcessScanner


class TestIntegration:
    """Integration tests for the full scanner workflow."""

    def test_full_workflow_with_valid_config(self):
        """Test the complete workflow from config loading to scanning."""
        # Create a temporary config file
        config_data = {
            "keywords": ["suspicious", "malware"],
            "whitelist": ["system.exe"],
            "log_level": "INFO"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            # Load configuration
            config_manager = ConfigManager(config_path)
            config = config_manager.load()
            
            assert config is not None
            
            # Initialize scanner
            scanner = ProcessScanner(
                suspicious_keywords=config_manager.suspicious_keywords,
                whitelist=config_manager.whitelist
            )
            
            assert scanner is not None
            assert len(scanner.suspicious_keywords) == 2
            
            # Perform scan (will scan actual system processes)
            # This is a real scan, so results depend on system state
            findings = scanner.scan()
            
            # Just verify the scan completes and returns a list
            assert isinstance(findings, list)
        finally:
            config_path.unlink()

    def test_scanner_with_empty_config(self):
        """Test scanner with empty configuration."""
        config_data = {
            "keywords": [],
            "whitelist": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            config_manager = ConfigManager(config_path)
            config_manager.load()
            
            scanner = ProcessScanner(
                suspicious_keywords=config_manager.suspicious_keywords,
                whitelist=config_manager.whitelist
            )
            
            # With no keywords, should find nothing
            findings = scanner.scan()
            assert len(findings) == 0
        finally:
            config_path.unlink()

    def test_scanner_keyword_case_insensitive(self):
        """Test that keyword matching is case-insensitive."""
        # Create config with uppercase keywords
        config_data = {
            "keywords": ["SUSPICIOUS", "MALWARE"],
            "whitelist": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            config_manager = ConfigManager(config_path)
            config_manager.load()
            
            # Keywords should be lowercase
            assert "suspicious" in config_manager.suspicious_keywords
            assert "SUSPICIOUS" not in config_manager.suspicious_keywords
            
            scanner = ProcessScanner(
                suspicious_keywords=config_manager.suspicious_keywords,
                whitelist=config_manager.whitelist
            )
            
            # Test that lowercase process names are matched
            from unittest.mock import Mock
            mock_proc = Mock()
            mock_proc.info = {
                'pid': 1234,
                'name': 'suspicious_lowercase.exe',  # lowercase
                'exe': 'C:\\test.exe',
                'cmdline': ['test.exe'],
                'create_time': 1234567890.0
            }
            
            result = scanner._analyze_process(mock_proc)
            assert result is not None
        finally:
            config_path.unlink()

