import pandas as pd
import os
import logging
from datetime import datetime

# --- Constants for better maintainability ---
INPUT_FILE = "sales.xlsx"
FILTERED_OUTPUT_FILE = "filtered_sales.xlsx"
SUMMARY_OUTPUT_FILE = "summary_by_manager.xlsx"

MIN_SUM_THRESHOLD = 10000
VAT_RATE = 1.20 # VAT coefficient (100% + 20% VAT)

# Column names (easy to change if needed)
COL_SUM = "Сумма"
COL_DATE = "Дата"
COL_MANAGER = "Менеджер"
COL_SUM_VAT = "Сумма с НДС"

FILTER_START_DATE_STR = "2024-01-01"

# --- Logging Setup ---
LOG_FILE = "data_processing.log"
# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
# INFO is a good level for normal execution (shows key steps)
# ERROR if you only want to see errors
LOG_LEVEL = logging.INFO

# Create logger
# __name__ is the standard logger name for the current module/script
logger = logging.getLogger(__name__)
# Set the overall level for the logger
logger.setLevel(LOG_LEVEL)

# Check if handlers already exist to prevent duplication on re-runs/imports
if not logger.handlers:
    # Create a file handler - for writing logs to a file
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL) # Level for the file

    # Create a console handler - for outputting logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Usually INFO and above is sufficient for console

    # Create a formatter - defines the format of messages in the log
    # %(asctime)s - time | %(name)s - logger name | %(levelname)s - level | %(message)s - the message itself
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# --- Main Logic ---

logger.info("--- Data Processing Script Started ---")
logger.info(f"Input file: {INPUT_FILE}")
logger.info(f"Filtering by '{COL_SUM}' > {MIN_SUM_THRESHOLD} and '{COL_DATE}' >= {FILTER_START_DATE_STR}")

df = None # Initialize DataFrame

try:
    # 🔹 Load the Excel file
    # Check if the file exists before reading
    if not os.path.exists(INPUT_FILE):
        logger.error(f"Error: Input file '{INPUT_FILE}' not found.")
        # exit() # Could terminate the script
        raise FileNotFoundError(f"File not found: {INPUT_FILE}") # Better to raise an exception

    logger.info(f"Attempting to read file: {INPUT_FILE}")
    # Read the file, explicitly telling pandas to parse the date column as dates
    df = pd.read_excel(INPUT_FILE, parse_dates=[COL_DATE])
    logger.info(f"File '{INPUT_FILE}' read successfully. Original number of rows: {len(df)}")

    # Check for required columns
    required_cols = [COL_SUM, COL_DATE, COL_MANAGER]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
         logger.error(f"Error: Required columns are missing in file '{INPUT_FILE}': {', '.join(missing)}")
         # exit()
         raise ValueError(f"Required columns are missing: {', '.join(missing)}")
    logger.info("Required columns check passed.")

except FileNotFoundError as e:
     logger.error("Script terminated due to missing input file.", exc_info=True) # exc_info=True adds exception info and traceback to the log
     exit()
except ValueError as e:
     logger.error("Script terminated due to missing required columns.", exc_info=True)
     exit()
except Exception as e:
    logger.error(f"An unexpected error occurred while reading the file: {e}", exc_info=True)
    exit() # Terminate execution on any other reading error

# If we reach here, the file was read successfully and columns are present

# Convert the filter start date string to a datetime object
try:
    filter_start_date_dt = pd.to_datetime(FILTER_START_DATE_STR)
    logger.debug(f"Filter start date converted to datetime: {filter_start_date_dt}")
except Exception as e:
     logger.error(f"Error: Could not convert filter date string '{FILTER_START_DATE_STR}' to date format: {e}", exc_info=True)
     exit()

# Ensure the date column in the DataFrame has the correct type (just in case)
# read_excel(parse_dates) should handle this, but explicit check/conversion is safer
try:
    df[COL_DATE] = pd.to_datetime(df[COL_DATE])
    # logger.debug(f"Column '{COL_DATE}' successfully converted to datetime.") # This might be redundant if parse_dates worked
except Exception as e:
     logger.error(f"Error: Could not convert column '{COL_DATE}' to date format: {e}", exc_info=True)
     exit()


# 🔹 Filter by date and sum
logger.info("Performing data filtering...")
df_filtered = df[
    (df[COL_SUM] > MIN_SUM_THRESHOLD) &
    (df[COL_DATE] >= filter_start_date_dt)
].copy() # Add .copy()
logger.info(f"Filtering complete. Rows remaining: {len(df_filtered)}")

# Check if any data remained after filtering
if df_filtered.empty:
    logger.warning("No data remained after filtering. Reports will not be created.")
    logger.info("--- Data Processing Script Finished (no data after filtering) ---")
    exit()


# 🔹 Add "Amount with VAT" column
logger.info(f"Adding column '{COL_SUM_VAT}'...")
# Use constants
df_filtered[COL_SUM_VAT] = df_filtered[COL_SUM] * VAT_RATE
# logger.debug("Column 'Amount with VAT' added.") # Detailed logging for DEBUG level

# 🔹 Group by manager and calculate sum of VAT amount
logger.info(f"Grouping by '{COL_MANAGER}' and summing '{COL_SUM_VAT}'...")
# Use constants
grouped = df_filtered.groupby(COL_MANAGER)[COL_SUM_VAT].sum().reset_index()
# logger.debug(f"Grouping complete. Obtained {len(grouped)} managers.") # Detailed logging for DEBUG level


# 🔹 Sort results by VAT amount in descending order
logger.info(f"Sorting results by '{COL_SUM_VAT}'...")
grouped = grouped.sort_values(by=COL_SUM_VAT, ascending=False)
# logger.debug("Sorting complete.") # Detailed logging for DEBUG level

# 🔹 Save the results
logger.info(f"Attempting to save results to files: '{FILTERED_OUTPUT_FILE}' and '{SUMMARY_OUTPUT_FILE}'")
try:
    df_filtered.to_excel(FILTERED_OUTPUT_FILE, index=False)
    logger.info(f"File '{FILTERED_OUTPUT_FILE}' saved successfully.")

    grouped.to_excel(SUMMARY_OUTPUT_FILE, index=False)
    logger.info(f"File '{SUMMARY_OUTPUT_FILE}' saved successfully.")

    print(f"✅ Reports successfully created: '{FILTERED_OUTPUT_FILE}' and '{SUMMARY_OUTPUT_FILE}'. Details in log file: {LOG_FILE}")

except Exception as e:
    logger.error(f"An error occurred while saving files: {e}", exc_info=True)
    print(f"❌ An error occurred while saving files. Details in log file: {LOG_FILE}")

logger.info("--- Data Processing Script Finished ---")