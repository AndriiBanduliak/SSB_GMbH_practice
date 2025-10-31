#!/usr/bin/env python3
"""
Process Scanner - Main Entry Point

A professional security monitoring tool that scans system processes
and detects suspicious activity based on configurable criteria.

Author: Andrii Banduliak
GitHub: https://github.com/AndriiBanduliak
"""

import argparse
import sys
from pathlib import Path

from antivirus_scanner.config import ConfigManager
from antivirus_scanner.exceptions import ConfigError
from antivirus_scanner.scanner import ProcessScanner
from antivirus_scanner.logger_config import setup_logging


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Process Security Scanner - Detect suspicious system processes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with default config.json
  %(prog)s -c custom.json           # Use custom config file
  %(prog)s --log-level DEBUG        # Enable debug logging
  %(prog)s --no-console             # Disable console output
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        type=Path,
        default=None,
        help='Path to configuration file (default: config.json in current directory)'
    )
    
    parser.add_argument(
        '-l', '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=None,
        help='Override log level from config file'
    )
    
    parser.add_argument(
        '--log-file',
        type=Path,
        default=None,
        help='Path to log file (default: antivirus.log in current directory)'
    )
    
    parser.add_argument(
        '--no-console',
        action='store_true',
        help='Disable console output (log only to file)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output (equivalent to --log-level DEBUG)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the process scanner.
    
    Returns:
        Exit code: 0 for success, 1 for suspicious processes found or errors.
    """
    args = parse_arguments()
    
    # Setup paths
    base_dir = Path(__file__).parent
    config_path = args.config or (base_dir / 'config.json')
    log_file = args.log_file or (base_dir / 'antivirus.log')
    
    # Determine log level
    log_level = args.log_level or "INFO"
    if args.verbose:
        log_level = "DEBUG"
    
    # Setup logging (basic setup before config is loaded)
    setup_logging(log_file=log_file, log_level=log_level, enable_console=not args.no_console)
    logger = __import__('logging').getLogger(__name__)
    
    try:
        # Load configuration
        config_manager = ConfigManager(config_path)
        config = config_manager.load()
        
        # Override log level from command line if specified
        if args.log_level or args.verbose:
            log_level = args.log_level if not args.verbose else "DEBUG"
            setup_logging(log_file=log_file, log_level=log_level, enable_console=not args.no_console)
        else:
            # Update logging level from config
            log_level = config_manager.log_level
            setup_logging(log_file=log_file, log_level=log_level, enable_console=not args.no_console)
        
        logger.info("=" * 60)
        logger.info("Process Scanner - Starting scan")
        logger.info(f"Configuration: {config_path}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Log level: {log_level}")
        logger.info("=" * 60)
        
        # Initialize scanner
        scanner = ProcessScanner(
            suspicious_keywords=config_manager.suspicious_keywords,
            whitelist=config_manager.whitelist
        )
        
        logger.debug(f"Scanning with {len(config_manager.suspicious_keywords)} keywords")
        logger.debug(f"Whitelist contains {len(config_manager.whitelist)} processes")
        
        # Perform scan
        findings = scanner.scan()
        
        # Report results
        if findings:
            logger.warning("=" * 60)
            logger.warning(f"⚠️  Found {len(findings)} suspicious process(es):")
            logger.warning("=" * 60)
            
            for idx, process in enumerate(findings, 1):
                logger.warning(f"  {idx}. {process}")
            
            logger.warning("=" * 60)
            logger.warning("Action recommended: Review the listed processes and investigate.")
            logger.warning("=" * 60)
            return 1
        else:
            logger.info("=" * 60)
            logger.info("✅ All processes are clean. No suspicious activity detected.")
            logger.info("=" * 60)
            return 0
            
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your configuration file and try again.")
        return 1
    except KeyboardInterrupt:
        logger.info("\n⚠️  Scan interrupted by user")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
        logger.error("Please report this issue with the error details above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
