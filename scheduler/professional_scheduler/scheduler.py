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

