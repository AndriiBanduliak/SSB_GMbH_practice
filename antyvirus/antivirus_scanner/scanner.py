"""Process scanner module for detecting suspicious processes."""

import logging
import psutil
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessInfo:
    """Information about a detected suspicious process."""
    
    pid: int
    name: str
    exe: Optional[str]
    cmdline: Optional[List[str]]
    create_time: Optional[float]
    
    def __str__(self) -> str:
        """String representation of process information."""
        exe_path = self.exe or "N/A"
        return (
            f"PID={self.pid} | "
            f"Name={self.name} | "
            f"Path={exe_path}"
        )


class ProcessScanner:
    """Scans system processes for suspicious activity."""
    
    def __init__(
        self,
        suspicious_keywords: Set[str],
        whitelist: Set[str],
        scan_attributes: Optional[List[str]] = None
    ) -> None:
        """
        Initialize process scanner.
        
        Args:
            suspicious_keywords: Set of keywords that indicate suspicious processes.
            whitelist: Set of process names to exclude from scanning.
            scan_attributes: List of process attributes to retrieve during scan.
        """
        self.suspicious_keywords = suspicious_keywords
        self.whitelist = whitelist
        self.scan_attributes = scan_attributes or [
            'pid', 'name', 'exe', 'cmdline', 'create_time'
        ]
        
    def scan(self) -> List[ProcessInfo]:
        """
        Scan all running processes for suspicious activity.
        
        Returns:
            List of ProcessInfo objects for detected suspicious processes.
        """
        alerts: List[ProcessInfo] = []
        processed_count = 0
        skipped_count = 0
        
        logger.debug(f"Starting process scan with {len(self.suspicious_keywords)} keywords")
        
        for proc in psutil.process_iter(self.scan_attributes):
            try:
                process_info = self._analyze_process(proc)
                if process_info:
                    alerts.append(process_info)
                processed_count += 1
            except psutil.NoSuchProcess:
                skipped_count += 1
                logger.debug(f"Process terminated during scan: PID={proc.pid}")
            except psutil.AccessDenied:
                skipped_count += 1
                logger.debug(f"Access denied to process: PID={proc.pid}")
            except Exception as e:
                skipped_count += 1
                logger.warning(f"Unexpected error processing process PID={proc.pid}: {e}")
        
        logger.info(
            f"Scan completed: {processed_count} processed, "
            f"{skipped_count} skipped, {len(alerts)} suspicious processes found"
        )
        
        return alerts
    
    def _analyze_process(self, proc: psutil.Process) -> Optional[ProcessInfo]:
        """
        Analyze a single process for suspicious activity.
        
        Args:
            proc: psutil.Process object to analyze.
            
        Returns:
            ProcessInfo if process is suspicious, None otherwise.
        """
        proc_info = proc.info
        name = (proc_info.get('name') or '').lower()
        
        # Check if process name contains suspicious keywords
        is_suspicious = any(keyword in name for keyword in self.suspicious_keywords)
        
        # Exclude whitelisted processes
        if name in self.whitelist:
            logger.debug(f"Process {name} (PID={proc_info.get('pid')}) is whitelisted")
            return None
        
        if is_suspicious:
            return ProcessInfo(
                pid=proc_info.get('pid', 0),
                name=proc_info.get('name', 'unknown'),
                exe=proc_info.get('exe'),
                cmdline=proc_info.get('cmdline'),
                create_time=proc_info.get('create_time')
            )
        
        return None
    
    def get_process_details(self, pid: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific process.
        
        Args:
            pid: Process ID to query.
            
        Returns:
            Dictionary with process details or None if process doesn't exist.
        """
        try:
            proc = psutil.Process(pid)
            return proc.as_dict()
        except psutil.NoSuchProcess:
            logger.warning(f"Process with PID={pid} does not exist")
            return None
        except psutil.AccessDenied:
            logger.warning(f"Access denied to process with PID={pid}")
            return None

