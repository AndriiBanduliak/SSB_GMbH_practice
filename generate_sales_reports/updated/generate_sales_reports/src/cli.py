#!/usr/bin/env python
import sys
import logging
import argparse
from pathlib import Path
import pandas as pd
from .processing import (
    load_data, filter_sales, add_vat, summarize_by_manager, save_reports
)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sales Data Processor for antyvirus-data-processing project"
    )
    parser.add_argument(
        "--input", "-i", type=Path, required=True,
        help="Input Excel file path"
    )
    parser.add_argument(
        "--out-filtered", "-f", type=Path, required=True,
        help="Output path for filtered data"
    )
    parser.add_argument(
        "--out-summary", "-s", type=Path, required=True,
        help="Output path for summary data"
    )
    parser.add_argument(
        "--min-sum", "-m", type=float, default=10000,
        help="Minimum sum threshold"
    )
    parser.add_argument(
        "--start-date", "-d", type=pd.to_datetime, default="2024-01-01",
        help="Start date for filtering (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--vat-rate", "-v", type=float, default=1.20,
        help="VAT rate multiplier"
    )
    return parser

def setup_logging(log_file: Path, level: int = logging.INFO) -> None:
    logger = logging.getLogger()
    logger.setLevel(level)
    fmt = "%(asctime)s %(levelname)-8s %(message)s"
    handlers = [logging.StreamHandler(), logging.FileHandler(log_file, encoding="utf-8")]
    for handler in handlers:
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)

def main() -> None:
    args = build_parser().parse_args()
    setup_logging(log_file=Path("data_processing.log"))
    logging.info("Starting sales data processing")

    df = load_data(args.input, date_col="Дата")
    df_filtered = filter_sales(
        df, "Сумма", "Дата", args.min_sum, args.start_date
    )
    if df_filtered.empty:
        logging.warning("No data after filtering. Exiting.")
        sys.exit(0)

    df_vat = add_vat(df_filtered, "Сумма", args.vat_rate, "Сумма с НДС")
    summary = summarize_by_manager(df_vat, "Менеджер", "Сумма с НДС")
    save_reports(df_vat, summary, args.out_filtered, args.out_summary)

    logging.info("Processing complete. Reports saved.")

if __name__ == "__main__":
    main()
