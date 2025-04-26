# battery_monitor.py
import psutil
import time
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, ProgressColumn, Task
from rich import print as rprint
from rich.text import Text
from rich.style import Style

# --- Constants ---
UPDATE_INTERVAL = 2
BATTERY_FULL_STATUS_TEXT = "[bold green]Fully Charged[/bold green]"
BATTERY_PLUGGED_TEXT = "[bold blue]🔌 Charging[/bold blue]"
BATTERY_DISCHARGING_TEXT = "[bold yellow]🔋 Discharging[/bold yellow]"
TIME_REMAINING_FORMAT = "Remaining: {}"

# --- Functions ---

def get_battery_status():
    """
    Retrieves the current battery status using psutil.

    Returns:
        A psutil.sensors_battery() object or None if battery information is unavailable
        or incomplete (e.g., percent is None).
    """
    try:
        battery = psutil.sensors_battery()
        if battery is None or battery.percent is None:
             return None
        return battery
    except Exception as e:
        rprint(f"[bold red]Error retrieving battery status: {e}[/bold red]")
        return None

def format_time(seconds):
    """Formats seconds into a human-readable 'H hr M min' string."""
    if seconds == psutil.POWER_TIME_UNLIMITED:
        return "∞ (Unlimited)"
    elif seconds == psutil.POWER_TIME_UNKNOWN:
        return "?? (Unknown)"
    elif seconds is None or seconds < 0:
         return "??"
    else:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return f"{h} hr {m} min"

def get_status_text(percent, plugged, secsleft):
    """Generates the status text string based on battery state."""
    time_info = ""
    if plugged:
        if percent == 100:
            state_text = BATTERY_FULL_STATUS_TEXT
            time_info = ""
        else:
            state_text = BATTERY_PLUGGED_TEXT
            pass
    else: # Not plugged (discharging)
        state_text = BATTERY_DISCHARGING_TEXT
        formatted_time_left = format_time(secsleft)
        if formatted_time_left not in ("?? (Unknown)", "??"):
             time_info = TIME_REMAINING_FORMAT.format(formatted_time_left)
        else:
             time_info = formatted_time_left

    combined_text = state_text
    if time_info:
         combined_text += f" | {time_info}"

    return combined_text.strip(" | ")

# --- Custom Rich Progress Column ---

class StatusTextColumn(ProgressColumn):
    """A column that displays the status text from task.fields['status_text']."""

    def render(self, task: Task) -> Text:
        """Render the status text for a given task."""
        # Now we are more confident the field is set upon task creation/first update.
        # We can still use .get() for safety, but the default can be empty or a simple placeholder.
        status_text_value = task.fields.get("status_text", "") # Default to empty string
        status_text_string = str(status_text_value)
        return Text(status_text_string, style="white")

# --- Main Monitoring Function ---

def monitor_battery():
    """
    Monitors battery status and displays it using a rich progress bar.
    Handles initial checks and updates the display periodically.
    """
    rprint("[bold green] Starting Battery Monitor [/bold green]")
    rprint("Press Ctrl+C to exit.")

    # --- Perform the second initial status check *before* entering Progress ---
    initial_status = get_battery_status()

    if initial_status is None:
         rprint("\n[bold red]Error: Battery data unavailable during initialization. Exiting.[/bold red]")
         return # Exit the function entirely

    # Calculate the initial status text *here*, before creating the Progress bar
    initial_percent = initial_status.percent
    initial_plugged = initial_status.power_plugged
    initial_secsleft = initial_status.secsleft
    initial_status_text = get_status_text(initial_percent, initial_plugged, initial_secsleft)

    # --- DEBUG PRINT ---
    rprint(f"[DEBUG] Calculated initial_status_text: {initial_status_text!r}")
    # --- END DEBUG PRINT ---

    # --- If status is available, proceed with Progress bar ---
    with Progress(
        SpinnerColumn("dots"),
        TextColumn("[bold]Battery:[/bold]"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        StatusTextColumn(), # Use the custom column here
        # console=console
    ) as progress:

        # Add the task. Set the initial status text field *directly here*.
        # Use start=True now, as the field is already populated at creation.
        task_id = progress.add_task(
            "",
            total=100,
            completed=initial_percent, # Set initial completion here
            start=True, # Start rendering immediately
            fields={"status_text": initial_status_text} # *** Set the actual initial value here ***
        )

        # We still call update immediately after start_task, but the essential field
        # is already there from add_task. This update just confirms/reinforces it.
        # It might be slightly redundant for the field, but needed for other task properties.
        progress.update(
             task_id,
             completed=initial_percent, # Ensure percent is updated
             fields={"status_text": initial_status_text} # Ensure field is updated
        )


        # --- Main Monitoring Loop ---
        try:
            while True:
                # Get status for subsequent updates within the loop
                current_status = get_battery_status()

                # --- Handle Errors or Battery Not Found *within the loop* ---
                if current_status is None:
                    rprint("\n[bold red]Error: Battery data became unavailable during monitoring. Exiting.[/bold red]")
                    break

                # --- Extract and Format Status Information ---
                percent = current_status.percent
                plugged = current_status.power_plugged
                secsleft = current_status.secsleft

                # Generate the status text for the current state
                status_text = get_status_text(percent, plugged, secsleft)

                # --- Update the Progress Bar Task ---
                progress.update(
                    task_id,
                    completed=percent,
                    fields={"status_text": status_text} # Update the field with current data
                )

                # --- Pause before the next update ---
                time.sleep(UPDATE_INTERVAL)

        except KeyboardInterrupt:
            rprint("\n[bold yellow]Battery monitor stopped by user.[/bold yellow]")
            # The Progress context manager automatically cleans up its display area upon exit.

# --- Entry Point ---
if __name__ == "__main__":
    # Perform an initial check to see if a battery is present at all.
    initial_status_check = get_battery_status()
    if initial_status_check is None:
         rprint("[bold red]No battery found at startup. Exiting.[/bold red]")
    else:
        monitor_battery()