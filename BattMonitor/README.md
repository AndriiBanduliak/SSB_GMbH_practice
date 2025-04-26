
# Battery Monitor - Python Script

This script provides real-time battery status monitoring using the `psutil` library and displays it in a visually appealing format with the `rich` library. It continuously tracks battery percentage, charging state, and estimated remaining time, updating the display periodically.

## Overview

The `BattMonitor.py` script retrieves battery information from your operating system (using `psutil`) and presents it to the user via a rich text interface.  It handles potential errors gracefully and provides clear feedback on the monitoring process.

## Features

*   **Real-time Monitoring:** Continuously tracks battery percentage, charging status, and estimated remaining time.
*   **Rich Text Display:** Uses the `rich` library for a visually appealing and informative display.
*   **Error Handling:** Includes robust error handling to gracefully manage situations where battery information is unavailable or inaccessible.
*   **Clear Feedback:** Provides clear messages to the user about the monitoring status, including startup messages, errors, and exit notifications.
*   **Keyboard Interrupt Support:** Allows users to stop the script using Ctrl+C.

## Prerequisites

*   **Python 3.7 or higher:**  This script is written for Python 3.
*   **`psutil` library:** This library provides access to system information, including battery status. Install it using: `pip install psutil`
*   **`rich` library:** This library enhances the display with rich text formatting and progress bars. Install it using: `pip install rich`

## Installation & Usage

1.  **Save the code:** Save the provided Python code as a file named `BattMonitor.py`.
2.  **Run the script:** Open your terminal or command prompt, navigate to the directory where you saved the file, and run it using: `BattMonitor.py`

## Configuration

The script does not require any configuration beyond ensuring that `psutil` and `rich` are installed.

## Output & Display

The script will display a progress bar with the following information:

*   **Battery Status:**  Indicates whether the battery is charging, discharging, or at 100% capacity.
*   **Percentage:** Shows the current battery percentage (e.g., "85%").
*   **Remaining Time:** Displays an estimate of how much time remains until the battery is depleted (in hours and minutes).  If the battery is unlimited or unknown, it will display “∞ (Unlimited)” or “?? (Unknown)”, respectively.

## Error Handling & Exit Conditions

The script handles the following error conditions:

*   **No Battery Found:** If no battery information can be retrieved during initialization, the script will print an error message and exit gracefully.
*   **Battery Data Unavailable During Monitoring:**  If battery data becomes unavailable while the script is running (e.g., due to system changes), the script will print an error message and exit.
*   **Keyboard Interrupt:** Pressing Ctrl+C will interrupt the script's execution, printing a notification message before exiting.

## Notes & Considerations

*   The accuracy of the remaining time estimate depends on the operating system’s battery monitoring capabilities.
*   This script is designed for general use and may require adjustments depending on your specific environment.
*   For more advanced features or customization options, consider exploring the `psutil` and `rich` libraries further.

## License

[MIT License](https://opensource.org/licenses/MIT) (Feel free to adapt this as needed.)
```

