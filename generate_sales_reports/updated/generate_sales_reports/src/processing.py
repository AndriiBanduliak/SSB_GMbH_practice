from pathlib import Path
from typing import Tuple
import pandas as pd

# Type alias for pandas DataFrame
DF = pd.DataFrame

def load_data(path: Path, date_col: str) -> DF:
    """
    Load an Excel file and parse the specified date column.
    """
    return pd.read_excel(path, parse_dates=[date_col])

def filter_sales(
    df: DF, sum_col: str, date_col: str, min_sum: float, start_date: pd.Timestamp
) -> DF:
    """
    Filter rows where sum_col > min_sum and date_col >= start_date.
    """
    mask = (df[sum_col] > min_sum) & (df[date_col] >= start_date)
    return df.loc[mask].copy()

def add_vat(df: DF, sum_col: str, vat_rate: float, new_col: str) -> DF:
    """
    Add a new column with VAT-inclusive amounts.
    """
    df[new_col] = df[sum_col] * vat_rate
    return df

def summarize_by_manager(df: DF, manager_col: str, vat_col: str) -> DF:
    """
    Summarize total VAT amounts by manager.
    """
    summary = df.groupby(manager_col)[vat_col].sum().reset_index()
    return summary.sort_values(by=vat_col, ascending=False)

def save_reports(
    filtered: DF, summary: DF, filtered_path: Path, summary_path: Path
) -> Tuple[Path, Path]:
    """
    Save filtered and summary DataFrames to Excel files.
    """
    filtered.to_excel(filtered_path, index=False)
    summary.to_excel(summary_path, index=False)
    return filtered_path, summary_path
