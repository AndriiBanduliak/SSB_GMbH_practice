# Sales Data Processing Script

This script is designed to filter and aggregate sales data from an Excel file (`sales.xlsx`). It allows you to generate a report on sales for a specific period, grouped by managers, and outputs the results in two separate files: `filtered_sales.xlsx` (filtered data) and `summary_by_manager.xlsx` (summary information by manager).

## Functionality

*   **Data Loading:** The script loads sales data from the Excel file `sales.xlsx`.
*   **Filtering:** Data is filtered based on a sales amount (`SUM`) greater than 10000 and a date (`DATE`) starting from 2024-01-01.
*   **VAT Calculation:** A column (Sum with VAT) is added, calculated by multiplying the sum by a factor of 1.2 (20% VAT).
*   **Grouping and Aggregation:** Data is grouped by manager (`manager`) and the value of "Сумма с НДС" is summed for each manager. The results are sorted in descending order based on the sum with VAT.
*   **Saving Results:** Filtered data is saved to the file `filtered_sales.xlsx`, and summary information is saved to the file `summary_by_manager.xlsx`.

## Requirements

*   Python 3.6 or higher
*   The pandas library (install using: `pip install pandas`)
*   The openpyxl library (install using: `pip install openpyxl`)

## Configuration

Before running the script, make sure that the `sales.xlsx` file is in the same directory as the script. The following parameters can be modified:

*   **`INPUT_FILE`**: Name of the input Excel file (default: "sales.xlsx").
*   **`FILTERED_OUTPUT_FILE`**: Name of the output file containing filtered data (default: "filtered_sales.xlsx").
*   **`SUMMARY_OUTPUT_FILE`**: Name of the output file containing summary information by manager (default: "summary_by_manager.xlsx").
*   **`MIN_SUM_THRESHOLD`**: Minimum sales amount for filtering (default: 10000).
*   **`FILTER_START_DATE`**: Start date of the period for filtering in YYYY-MM-DD format (default: "2024-01-01").

## Running the Script

Run the script from the command line: `generate_sales_reports.py`

## Logging

The script uses the `logging` module to record information about the process, including errors and warnings. Detailed information can be found in the log file `data_processing.log`.  You can use the logging level DEBUG (e.g., `python generate_sales_reports.py -v`) for more detailed output.

## Error Handling

The script handles the following errors:

*   Missing input file.
*   Missing required columns in the file.
*   Unable to convert date string to date format.
*   Errors saving files.