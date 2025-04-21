#  Job Scheduler

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

