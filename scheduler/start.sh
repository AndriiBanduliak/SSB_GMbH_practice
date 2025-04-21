#!/bin/bash
#
# scheduler.sh
# Sets up the project directory, creates a virtual environment,
# installs dependencies, and creates necessary files including README.md
# for the Python job scheduler project.
#

# Exit immediately if a command exits with a non-zero status
set -e

# Define the project directory name
PROJECT_DIR="professional_scheduler"

# --- 1. Create Project Directory ---
echo "Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
echo "Changed into directory: $(pwd)"

# --- 2. Create Virtual Environment ---
echo "Creating virtual environment named '.venv'..."
# Try python3 first, then fall back to python if python3 is not found/fails
# Use || true to not exit script immediately on first attempt failure before trying the second
python3 -m venv .venv 2>/dev/null || python -m venv .venv || { echo "Error: Could not create virtual environment using 'python3 -m venv' or 'python -m venv'. Please ensure Python 3 is installed and accessible via 'python' or 'python3' commands."; exit 1; }
echo "Virtual environment created."

# --- 3. Activate Virtual Environment ---
echo "Activating virtual environment..."
# Check if the activate script exists before sourcing
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated."
elif [ -f ".venv/Scripts/activate" ]; then # Check for Windows venv path
    source .venv/Scripts/activate
    echo "Virtual environment activated."
else
    echo "Error: Could not find virtual environment activation script."
    exit 1
fi


# --- 4. Create requirements.txt and Install Dependencies ---
echo "Creating requirements.txt..."
cat << EOF > requirements.txt
# requirements.txt
schedule==1.2.1
PyYAML==6.0.1
EOF

echo "Installing dependencies from requirements.txt..."
# Use -q for quiet install, --disable-pip-version-check to avoid version check messages
# Use || true to not exit script if --disable-pip-version-check fails on older pip (less critical)
pip install -r requirements.txt -q --disable-pip-version-check || pip install -r requirements.txt -q || { echo "Error: Failed to install dependencies."; exit 1; }
echo "Dependencies installed successfully."

# --- 5. Create Configuration File (config.yaml) ---
echo "Creating config.yaml..."
cat << EOF > config.yaml
# config.yaml
#
# Scheduler configuration file

# --- Logging Configuration ---
# Uses Python's logging.config.dictConfig format.
# You can define handlers (console, file), formatters, loggers, etc.
logging:
  version: 1
  disable_existing_loggers: False
  formatters:
    standard:
      format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  handlers:
    console:
      class: logging.StreamHandler
      formatter: standard
      level: INFO
      stream: ext://sys.stdout
    file:
      class: logging.handlers.RotatingFileHandler
      formatter: standard
      level: INFO
      filename: scheduler.log
      maxBytes: 1048576 # 1MB
      backupCount: 5
  loggers:
    # Root logger
    '':
      handlers: [console, file]
      level: INFO
      propagate: True
    # Example: configure a specific logger
    # 'tasks':
    #   handlers: [file]
    #   level: DEBUG
    #   propagate: False

# --- Task Definitions ---
# List of tasks to be scheduled.
# Each task requires a 'name', 'function', and 'schedule'.
# Optional: 'params' (dictionary of parameters passed to the task function).
tasks:
  - name: Daily Backup
    function: backup_task
    schedule:
      type: daily
      at: "09:00"
    params:
      backup_location: "/tmp/scheduler_backups" # Example parameter

  - name: Temporary Files Cleanup
    function: clean_temp_task
    schedule:
      type: every
      interval: 1
      unit: minutes # Supported units: seconds, minutes, hours, days, weeks
    params:
      temp_dir: "/tmp/scheduler_temp" # Example parameter
      age_days: 0 # Clean files older than 0 days (i.e., all) for testing

  - name: Weekly Report Generation
    function: report_task
    schedule:
      type: every # Using 'every' for demonstration purposes in a presentation
      interval: 3
      unit: minutes
    params:
      report_format: "txt" # Example parameter

  # Example of adding a simple task
  - name: Simple Greeting
    function: simple_greet_task
    schedule:
      type: every
      interval: 30
      unit: seconds

# Add more tasks as needed following the structure above.
EOF
echo "config.yaml created."
# Create dummy directories for the example tasks to not fail immediately
mkdir -p /tmp/scheduler_backups /tmp/scheduler_temp


# --- 6. Create Task Module (tasks.py) ---
echo "Creating tasks.py..."
# Using single quotes around EOF ('EOF') to prevent shell expansion within the Python code
cat << 'EOF' > tasks.py
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
EOF
echo "tasks.py created."

# --- 7. Create Scheduler Script (scheduler.py) ---
echo "Creating scheduler.py..."
# Using single quotes around EOF ('EOF') to prevent shell expansion within the Python code
cat << 'EOF' > scheduler.py
# scheduler.py
#
# Main script for the professional job scheduler.
# Handles configuration loading, logging setup, task scheduling,
# and the main execution loop.

import schedule
import time
import logging
import logging.config
import yaml
import sys
import os
import argparse # For parsing command-line arguments
from typing import Dict, Any # For type hints
from datetime import datetime # Used for time validation in config

# Import the tasks and their mapping
from tasks import TASK_MAP

# Get a logger for the main scheduler script
logger = logging.getLogger(__name__)

# --- Helper function to run a task safely ---
def safe_run_task(task_func, task_name: str, *args: Any, **kwargs: Any):
    """
    Wrapper function to execute a task function safely.
    Catches exceptions raised by the task and logs them.
    Ensures one task's failure doesn't stop the entire scheduler loop.

    Args:
        task_func: The task function to execute.
        task_name: The name of the task (for logging).
        *args: Positional arguments to pass to the task function.
        **kwargs: Keyword arguments to pass to the task function.
    """
    try:
        logger.info(f"Executing task: '{task_name}'")
        # Pass parameters from config to the task function
        task_func(*args, **kwargs)
        logger.info(f"Task completed: '{task_name}'")
    except Exception as e:
        # Log the error, including traceback
        logger.error(f"Error executing task '{task_name}': {e}", exc_info=True)

# --- Function to load configuration ---
def load_config(config_path: str) -> Dict[str, Any]:
    """
    Loads configuration from a YAML file.

    Args:
        config_path: The path to the configuration YAML file.

    Returns:
        A dictionary containing the configuration.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
        ValueError: If the configuration structure is invalid (basic check).
        RuntimeError: For other unexpected file reading errors.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        if not isinstance(config, dict):
             raise ValueError("Configuration file does not contain a valid dictionary structure.")
        logger.info(f"Configuration successfully loaded from {config_path}")
        return config
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing configuration file {config_path}: {e}")
    except Exception as e:
        # Catch any other unexpected errors during file reading
        raise RuntimeError(f"An unexpected error occurred loading configuration {config_path}: {e}")


# --- Function to setup logging ---
def setup_logging(log_config: Dict[str, Any] | None):
    """
    Configures logging using a dictionary (e.g., from YAML config).
    If log_config is None or empty, sets up basic default logging.

    Args:
        log_config: A dictionary conforming to logging.config.dictConfig format, or None.
    """
    if log_config:
        try:
            # Validate the logging configuration dictionary structure minimally
            if not isinstance(log_config, dict) or 'version' not in log_config or log_config['version'] != 1:
                 raise ValueError("Invalid logging configuration dictionary structure.")

            logging.config.dictConfig(log_config)
            # Get the root logger to check handlers were configured
            # This helps catch cases where dictConfig parses but doesn't link handlers
            root_logger_handlers = logging.getLogger().handlers
            if not root_logger_handlers:
                 # This might happen if dictConfig parsed successfully but no handlers were defined/assigned
                 raise ValueError("Logging configuration parsed successfully but root logger has no handlers. Check 'handlers' and root logger config.")
            logger.info(f"Logging configured using dictConfig with handlers: {[h.__class__.__name__ for h in root_logger_handlers]}.")
        except Exception as e:
            # If dictConfig fails or configuration is invalid, fall back to basic logging and log the error
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logger.error(f"Failed to configure logging with dictConfig: {e}. Using basic config.", exc_info=True)
    else:
        # Fallback to basic logging if no log_config is provided or is None/empty
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger.warning("No logging configuration found in config.yaml or it is empty/invalid. Using basic config.")

    # After setting up logging, test it
    logger.debug("Debug level message (should only appear if level is DEBUG)")
    logger.info("Info level message: Logging setup complete.")


# --- Function to validate and schedule a single task ---
def _schedule_single_task(task_conf: Dict[str, Any]):
    """Helper function to parse and schedule a single task entry."""
    # Use .get for task_name to provide a default if missing for error reporting
    task_name = task_conf.get('name', 'Unnamed Task')
    logger.debug(f"Attempting to schedule task: {task_name}")

    # More robust validation for each task entry
    if not isinstance(task_conf, dict):
         raise ValueError("Task entry is not a dictionary.")
    if 'function' not in task_conf or not isinstance(task_conf['function'], str):
         raise ValueError("Task missing 'function' key or it's not a string.")
    if 'schedule' not in task_conf or not isinstance(task_conf['schedule'], dict):
         raise ValueError("Task missing 'schedule' key or it's not a dictionary.")

    func_name = task_conf['function']
    schedule_conf = task_conf['schedule']
    # Default params to an empty dict if missing or not a dict
    task_params = task_conf.get('params', {})
    if not isinstance(task_params, dict):
         logger.warning(f"Ignoring invalid 'params' for task '{task_name}': Expected a dictionary but got {type(task_params).__name__}.")
         task_params = {}


    # Get the actual function from the TASK_MAP
    if func_name not in TASK_MAP:
        logger.error(f"Unknown function '{func_name}' referenced by task '{task_name}'. Skipping task registration.")
        return # Skip this task

    task_func = TASK_MAP[func_name]

    # Wrap the task function with safe_run_task and bind parameters
    # The lambda captures the necessary context (task_func, name, params)
    # and passes them to safe_run_task when schedule calls the lambda.
    # This ensures parameters from config are passed to the task function.
    job_func_with_params = lambda name=task_name, func=task_func, params=task_params: safe_run_task(func, name, **params)

    # Parse the schedule configuration
    schedule_type = schedule_conf.get('type')
    if not schedule_type or not isinstance(schedule_type, str):
         raise ValueError("Schedule missing 'type' or it's not a string.")

    scheduler_job = None

    if schedule_type == 'every':
        interval = schedule_conf.get('interval')
        unit = schedule_conf.get('unit')
        if not isinstance(interval, (int, float)) or interval <= 0:
            raise ValueError("'every' schedule requires a positive number for 'interval'.")
        if not isinstance(unit, str) or not hasattr(schedule.every(1), unit):
             # Basic check if unit exists in schedule.every(1) methods
             raise ValueError(f"'every' schedule requires a valid 'unit' string (e.g., 'seconds', 'minutes', 'hours', 'days', 'weeks'). Invalid unit: '{unit}'")
        scheduler_job = schedule.every(interval).__getattribute__(unit)

    elif schedule_type == 'daily':
        at_time = schedule_conf.get('at')
        if not isinstance(at_time, str):
            raise ValueError("'daily' schedule requires 'at' (string, e.g., 'HH:MM' or 'HH:MM:SS').")
         # Basic format check for 'at' time
        try:
            # Try parsing HH:MM:SS first, then HH:MM
            datetime.strptime(at_time, '%H:%M:%S')
        except ValueError:
            try:
                 datetime.strptime(at_time, '%H:%M')
            except ValueError:
                 raise ValueError(f"Invalid time format for 'at' in daily schedule: '{at_time}'. Expected 'HH:MM' or 'HH:MM:SS'.")
        scheduler_job = schedule.every().day.at(at_time)

    elif schedule_type == 'weekly':
        day_of_week = schedule_conf.get('day')
        at_time = schedule_conf.get('at')
        if not isinstance(day_of_week, str) or not isinstance(at_time, str):
             raise ValueError("'weekly' schedule requires 'day' (string) and 'at' (string).")
        day_lower = day_of_week.lower()
        if day_lower not in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
             raise ValueError(f"Invalid day of week '{day_of_week}' for weekly schedule. Must be one of: monday, tuesday, ..., sunday.")
        # Basic format check for 'at' time
        try:
            datetime.strptime(at_time, '%H:%M:%S')
        except ValueError:
            try:
                 datetime.strptime(at_time, '%H:%M')
            except ValueError:
                 raise ValueError(f"Invalid time format for 'at' in weekly schedule: '{at_time}'. Expected 'HH:MM' or 'HH:MM:SS'.")

        scheduler_job = schedule.every().__getattribute__(day_lower).at(at_time)

    # Add support for other schedule types here if needed (e.g., 'hourly', 'monthly')
    # elif schedule_type == 'hourly':
    #     at_time = schedule_conf.get('at') # e.g., ":30" for every hour at 30 minutes past
    #     if not isinstance(at_time, str) or not at_time.startswith(':'):
    #          raise ValueError("'hourly' schedule requires 'at' (string, e.g., ':MM').")
    #     try:
    #          # Need a dummy date to parse ':MM' as a full time
    #          datetime.strptime(at_time, ':%M')
    #     except ValueError:
    #          raise ValueError(f"Invalid time format for 'at' in hourly schedule: '{at_time}'. Expected ':MM'.")
    #     scheduler_job = schedule.every().hour.at(at_time)


    else:
        # If we reached here, the schedule type was present but not recognized
        raise ValueError(f"Unsupported or invalid schedule type: '{schedule_type}'")


    if scheduler_job:
        # Finally, register the task with schedule
        # The do() method gets the wrapped function (our lambda)
        scheduler_job.do(job_func_with_params)
        logger.info(f"Task '{task_name}' ({func_name}) successfully scheduled.")
    else:
        # This case should ideally be caught by the ValueError above, but as a fallback:
        logger.error(f"Failed to create scheduler job object for task '{task_name}'. Skipping registration.")


# --- Function to schedule tasks from config ---
def schedule_tasks(config: Dict[str, Any]):
    """
    Registers tasks with the schedule library based on the configuration.

    Args:
        config: The loaded configuration dictionary.
                Assumes basic validation of the top-level structure is done.
    """
    # Use .get with default to handle missing 'tasks' key gracefully
    tasks_config_list = config.get('tasks', [])

    if not isinstance(tasks_config_list, list):
        logger.error("Configuration 'tasks' section is not a list. No tasks will be scheduled.")
        return

    if not tasks_config_list:
        logger.warning("No tasks defined in the configuration.")
        return

    logger.info(f"Found {len(tasks_config_list)} task definitions in config. Attempting to schedule...")

    for task_conf in tasks_config_list:
        # Process each task configuration item
        try:
            _schedule_single_task(task_conf)
        except (KeyError, ValueError, TypeError) as e:
            # Log specific errors related to parsing THIS task's configuration
            # Attempt to get task name even if conf is invalid
            task_name_for_log = task_conf.get('name', 'N/A') if isinstance(task_conf, dict) else 'N/A'
            logger.error(f"Configuration error for task '{task_name_for_log}': {e}. Skipping task registration.", exc_info=True)
        except Exception as e:
            # Log any other unexpected errors during single task processing
            task_name_for_log = task_conf.get('name', 'N/A') if isinstance(task_conf, dict) else 'N/A'
            logger.error(f"An unexpected error occurred while processing task configuration for '{task_name_for_log}': {e}. Skipping.", exc_info=True)

    # After iterating through all tasks, report total scheduled
    logger.info(f"Finished scheduling tasks. Total successfully scheduled: {len(schedule.get_jobs())}")


# --- Main entry point ---
if __name__ == "__main__":
    # Use argparse to handle command-line arguments
    parser = argparse.ArgumentParser(description="A professional job scheduler.")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the configuration YAML file (default: config.yaml)"
    )
    args = parser.parse_args()

    config = None # Initialize config variable

    # Setup basic logging initially, in case config loading fails
    # This ensures we can log errors even before setup_logging is called with full config
    # This basic config will be replaced by dictConfig if it succeeds.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Basic logging configured (will attempt to use config for advanced setup).")


    try:
        # Load configuration
        config = load_config(args.config)

        # Setup logging *after* loading config, using config settings
        # Provide the logging part of the config dictionary. Default to empty dict if missing.
        setup_logging(config.get('logging', {}))

        logger.info("Scheduler is starting...")

        # Schedule tasks based on the loaded configuration
        # Pass the loaded config dictionary. Default to empty dict if config was None (shouldn't happen due to load_config raises)
        schedule_tasks(config if config else {})

        # Check if any tasks were actually scheduled
        # schedule.get_jobs() returns a list of Job objects
        scheduled_jobs = schedule.get_jobs()
        if not scheduled_jobs:
            logger.warning("No tasks were successfully scheduled based on the configuration. The scheduler will run but perform no actions.")
            logger.info("Exiting scheduler.")
            sys.exit(0) # Exit cleanly if nothing is scheduled

        logger.info(f"Scheduler started with {len(scheduled_jobs)} tasks scheduled. Press Ctrl+C to exit.")

        # Main scheduler loop
        while True:
            # Check if any jobs are pending execution
            # This is non-blocking
            schedule.run_pending()
            # Wait for 1 second to avoid consuming 100% CPU
            time.sleep(1)

    except FileNotFoundError as e:
        # Catch specific file not found error from load_config
        # Logging might not be fully set up via dictConfig, so use basic logger or print
        logger.error(f"ERROR: Configuration file error: {e}")
        sys.exit(1) # Exit with an error code
    except yaml.YAMLError as e:
        # Catch YAML parsing errors
        logger.error(f"ERROR: Configuration YAML parsing error: {e}")
        sys.exit(1)
    except ValueError as e:
         # Catch validation errors during config loading or scheduling
         # These are handled by raising ValueErrors within functions
         logger.error(f"ERROR: Configuration validation error: {e}")
         sys.exit(1)
    except KeyboardInterrupt:
        # Handle clean shutdown on Ctrl+C
        # Use the logger which should be set up by now
        logger.info("Received interrupt signal (Ctrl+C). Shutting down scheduler.")
        # schedule.clear() # Optional: clear all jobs on shutdown if needed, typically not necessary
    except Exception as e:
        # Catch any other unexpected critical errors in the main loop
        # Logging should be set up, so use logger
        logger.critical(f"A critical unexpected error occurred in the main scheduler loop: {e}", exc_info=True)
        sys.exit(1) # Exit with an error code on critical failure
    finally:
        # This block always runs on exit (normal or exception)
        # Ensure final message is logged using the established logger
        logger.info("Scheduler stopped.")

EOF
echo "scheduler.py created."

# --- 8. Create README.md ---
echo "Creating README.md..."
# Using single quotes around EOF ('EOF') to prevent shell expansion within the Markdown content
cat << 'EOF' > README.md
# Professional Python Job Scheduler

This project implements a robust and professional job scheduler using the `schedule` library, designed for running recurring tasks based on a declarative configuration. It follows best practices for structure, configuration, logging, and error handling, making it suitable for integration into larger applications or deployment as a standalone service.

## Features

*   **Configuration-Driven:** All tasks and their schedules are defined in a human-readable YAML file (`config.yaml`).
*   **Modular Design:** Separation of concerns with dedicated files for tasks (`tasks.py`), configuration (`config.yaml`), and the core scheduler logic (`scheduler.py`).
*   **Robust Logging:** Utilizes Python's standard `logging` module with configurable output (console, file) and log levels via `config.yaml`.
*   **Safe Task Execution:** Tasks are wrapped to catch exceptions, preventing a single task failure from crashing the entire scheduler.
*   **Dynamic Task Loading:** Tasks are registered dynamically based on the `config.yaml`, mapping function names to actual Python functions via a dictionary.
*   **Task Parameters:** Tasks can receive configuration parameters directly from the `config.yaml`.
*   **Graceful Shutdown:** Handles `Ctrl+C` for a clean shutdown.
*   **Automated Setup:** Includes a bash script (`scheduler.sh`) to automate project setup, virtual environment creation, and dependency installation.
*   **Type Hinting:** Includes type hints for better code clarity and maintainability.

## Prerequisites

*   Python 3.6+
*   Basic understanding of the command line / terminal.

## Setup and Installation

The included `scheduler.sh` script automates the entire setup process.

1.  Save the bash script code (`scheduler.sh`) to your machine.
2.  Make the script executable:
    ```bash
    chmod +x scheduler.sh
    ```
3.  Run the script. This will create the project directory, set up a virtual environment, install dependencies, and create the necessary project files (`config.yaml`, `tasks.py`, `scheduler.py`, `requirements.txt`, `README.md`).
    ```bash
    ./scheduler.sh
    ```
    The script will output its progress and should leave you inside the activated virtual environment within the created project directory (`./professional_scheduler`).

EOF