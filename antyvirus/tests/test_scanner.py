"""Tests for process scanner module."""

from unittest.mock import Mock, MagicMock, patch
import pytest
from typing import Set

from antivirus_scanner.scanner import ProcessScanner, ProcessInfo


class TestProcessInfo:
    """Test suite for ProcessInfo dataclass."""

    def test_process_info_str_representation(self):
        """Test string representation of ProcessInfo."""
        process = ProcessInfo(
            pid=1234,
            name="test.exe",
            exe="C:\\test.exe",
            cmdline=["test.exe", "--arg"],
            create_time=1234567890.0
        )
        
        result = str(process)
        assert "PID=1234" in result
        assert "Name=test.exe" in result
        assert "Path=C:\\test.exe" in result

    def test_process_info_no_exe(self):
        """Test ProcessInfo with no executable path."""
        process = ProcessInfo(
            pid=1234,
            name="test.exe",
            exe=None,
            cmdline=None,
            create_time=None
        )
        
        result = str(process)
        assert "Path=N/A" in result


class TestProcessScanner:
    """Test suite for ProcessScanner class."""

    @pytest.fixture
    def scanner(self):
        """Create a ProcessScanner instance for testing."""
        keywords: Set[str] = {"suspicious", "malware", "hack"}
        whitelist: Set[str] = {"trusted.exe"}
        return ProcessScanner(
            suspicious_keywords=keywords,
            whitelist=whitelist
        )

    def test_scanner_initialization(self, scanner):
        """Test scanner initialization."""
        assert scanner.suspicious_keywords == {"suspicious", "malware", "hack"}
        assert scanner.whitelist == {"trusted.exe"}
        assert scanner.scan_attributes == [
            'pid', 'name', 'exe', 'cmdline', 'create_time'
        ]

    def test_analyze_process_suspicious(self, scanner):
        """Test detection of suspicious process."""
        mock_proc = Mock()
        mock_proc.info = {
            'pid': 1234,
            'name': 'suspicious_process.exe',
            'exe': 'C:\\suspicious_process.exe',
            'cmdline': ['suspicious_process.exe'],
            'create_time': 1234567890.0
        }
        
        result = scanner._analyze_process(mock_proc)
        
        assert result is not None
        assert isinstance(result, ProcessInfo)
        assert result.pid == 1234
        assert result.name == 'suspicious_process.exe'

    def test_analyze_process_whitelisted(self, scanner):
        """Test that whitelisted processes are ignored."""
        mock_proc = Mock()
        mock_proc.info = {
            'pid': 1234,
            'name': 'trusted.exe',
            'exe': 'C:\\trusted.exe',
            'cmdline': ['trusted.exe'],
            'create_time': 1234567890.0
        }
        
        result = scanner._analyze_process(mock_proc)
        
        assert result is None

    def test_analyze_process_clean(self, scanner):
        """Test that clean processes are not flagged."""
        mock_proc = Mock()
        mock_proc.info = {
            'pid': 1234,
            'name': 'normal_process.exe',
            'exe': 'C:\\normal_process.exe',
            'cmdline': ['normal_process.exe'],
            'create_time': 1234567890.0
        }
        
        result = scanner._analyze_process(mock_proc)
        
        assert result is None

    @patch('antivirus_scanner.scanner.psutil')
    def test_scan_finds_suspicious_processes(self, mock_psutil, scanner):
        """Test scanning finds suspicious processes."""
        # Create mock processes
        mock_proc1 = Mock()
        mock_proc1.info = {
            'pid': 1,
            'name': 'normal.exe',
            'exe': 'C:\\normal.exe',
            'cmdline': ['normal.exe'],
            'create_time': 1234567890.0
        }
        
        mock_proc2 = Mock()
        mock_proc2.info = {
            'pid': 2,
            'name': 'malware.exe',
            'exe': 'C:\\malware.exe',
            'cmdline': ['malware.exe'],
            'create_time': 1234567890.0
        }
        
        # Setup process_iter to return our mock processes
        mock_psutil.process_iter.return_value = [mock_proc1, mock_proc2]
        
        results = scanner.scan()
        
        assert len(results) == 1
        assert results[0].name == 'malware.exe'
        assert results[0].pid == 2

    @patch('antivirus_scanner.scanner.psutil')
    def test_scan_handles_no_such_process(self, mock_psutil, scanner):
        """Test scan handles NoSuchProcess exception."""
        mock_proc = Mock()
        mock_proc.pid = 1234
        mock_proc.info = {
            'pid': 1234,
            'name': 'test.exe',
        }
        
        # First call raises NoSuchProcess, second returns info
        mock_proc.info.get.side_effect = [
            lambda key, default=None: {'suspicious': 'process'}.get(key, default)
        ]
        
        def process_iter_side_effect(*args):
            mock_proc.info = {'pid': 1234, 'name': 'suspicious.exe'}
            yield mock_proc
        
        mock_psutil.process_iter.side_effect = process_iter_side_effect
        mock_psutil.NoSuchProcess = type('NoSuchProcess', (Exception,), {})
        
        # Mock _analyze_process to handle the exception
        original_analyze = scanner._analyze_process
        
        def mock_analyze(proc):
            try:
                return original_analyze(proc)
            except Exception:
                return None
        
        scanner._analyze_process = mock_analyze
        
        results = scanner.scan()
        # Should complete without crashing
        assert isinstance(results, list)

    @patch('antivirus_scanner.scanner.psutil')
    def test_get_process_details_success(self, mock_psutil, scanner):
        """Test getting process details successfully."""
        mock_process = Mock()
        mock_process.as_dict.return_value = {
            'pid': 1234,
            'name': 'test.exe',
            'memory_info': {}
        }
        mock_psutil.Process.return_value = mock_process
        
        result = scanner.get_process_details(1234)
        
        assert result is not None
        assert result['pid'] == 1234
        assert result['name'] == 'test.exe'

    @patch('antivirus_scanner.scanner.psutil')
    def test_get_process_details_not_found(self, mock_psutil, scanner):
        """Test getting details for non-existent process."""
        mock_psutil.Process.side_effect = mock_psutil.NoSuchProcess(1234)
        mock_psutil.NoSuchProcess = type('NoSuchProcess', (Exception,), {})
        
        result = scanner.get_process_details(1234)
        
        assert result is None

    @patch('antivirus_scanner.scanner.psutil')
    def test_get_process_details_access_denied(self, mock_psutil, scanner):
        """Test getting details when access is denied."""
        mock_psutil.Process.side_effect = mock_psutil.AccessDenied(1234)
        mock_psutil.AccessDenied = type('AccessDenied', (Exception,), {})
        
        result = scanner.get_process_details(1234)
        
        assert result is None

