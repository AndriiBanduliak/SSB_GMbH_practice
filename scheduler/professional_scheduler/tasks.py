# tasks.py
#
# Module containing task functions for the scheduler.
# Each function represents a job to be performed.

import logging
from datetime import datetime
import time # Used for simulating work
import random # Used for simulating errors

# Get a logger specific to the tasks module
# This allows configuring logging for tasks separately if needed
logger = logging.getLogger(__name__)

def backup_task(**kwargs):
    """
    Task function: Creates a backup.

    Accepts keyword arguments for configuration (e.g., backup_location).
    Logs the start, progress, and completion/failure of the backup process.
    """
    backup_location = kwargs.get('backup_location', 'default_backup_location')
    logger.info(f"[BACKUP] Starting backup to {backup_location}...")

    try:
        # --- REAL BACKUP LOGIC GOES HERE ---
        # This is where you would interact with your system,
        # call backup tools, copy files, etc.
        # Example: Using a placeholder sleep to simulate work
        time.sleep(3) # Simulate a task taking 3 seconds

        # --- END OF REAL BACKUP LOGIC ---

        # Log success
        logger.info(f"[BACKUP] Backup completed successfully at {datetime.now().strftime('%H:%M:%S')} to {backup_location}")

    except Exception as e:
        # Log any errors that occur during the backup process
        logger.error(f"[BACKUP] Error during backup to {backup_location}: {e}", exc_info=True)
        # exc_info=True adds traceback information to the log

def clean_temp_task(**kwargs):
    """
    Task function: Cleans temporary files.

    Accepts keyword arguments for configuration (e.g., temp_dir, age_days).
    Logs the cleaning process.
    """
    temp_dir = kwargs.get('temp_dir', '/tmp')
    age_days = kwargs.get('age_days', 3) # Default to 3 days
    logger.info(f"[CLEAN] Starting cleanup of temporary files in {temp_dir} older than {age_days} days...")

    try:
        # --- REAL CLEANUP LOGIC GOES HERE ---
        # This is where you would list files, check modification dates,
        # and remove old temporary files.
        # Example: Simulate a random failure
        if random.random() < 0.05: # 5% chance of failure
             raise RuntimeError("Simulated cleanup failure: Disk full")

        # Example: Using a placeholder sleep
        time.sleep(1) # Simulate a task taking 1 second

        # --- END OF REAL CLEANUP LOGIC ---

        # Log success
        logger.info(f"[CLEAN] Temporary files cleanup completed at {datetime.now().strftime('%H:%M:%S')} in {temp_dir}")

    except Exception as e:
        # Log any errors during cleanup
        logger.error(f"[CLEAN] Error during temporary files cleanup in {temp_dir}: {e}", exc_info=True)


def report_task(**kwargs):
    """
    Task function: Generates a report.

    Accepts keyword arguments for configuration (e.g., report_format).
    Logs the report generation process.
    """
    report_format = kwargs.get('report_format', 'csv')
    logger.info(f"[REPORT] Starting report generation in {report_format} format...")

    try:
        # --- REAL REPORT GENERATION LOGIC GOES HERE ---
        # This is where you would query databases, process data,
        # and generate the report file.
        # Example: Using a placeholder sleep
        time.sleep(5) # Simulate a task taking 5 seconds

        # --- END OF REAL REPORT GENERATION LOGIC ---

        # Log success
        logger.info(f"[REPORT] Report generated successfully at {datetime.now().strftime('%H:%M:%S')} in {report_format} format")

    except Exception as e:
        # Log any errors during report generation
        logger.error(f"[REPORT] Error during report generation: {e}", exc_info=True)

# Dictionary mapping function names from config to actual functions
# This is crucial for dynamic task loading from the configuration
TASK_MAP = {
    "backup_task": backup_task,
    "clean_temp_task": clean_temp_task,
    "report_task": report_task,
}

# Example of adding a task that doesn't take parameters (still include **kwargs for consistency)
def simple_greet_task(**kwargs):
    """A simple task that just prints a greeting."""
    logger.info("Hello from simple_greet_task!")

TASK_MAP["simple_greet_task"] = simple_greet_task
