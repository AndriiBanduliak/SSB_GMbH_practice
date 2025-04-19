#!/usr/bin/env bash
# =============================================================================
# Bash script to scaffold the antyvirus-data-processing project
# Creates the full directory structure, configuration files, source code,
# unit tests, CI workflow, and a comprehensive README.md in English.
# Usage:
#   chmod +x setup_project.sh
#   ./setup_project.sh
# =============================================================================

set -euo pipefail

# Define project directory and subdirectories
TARGET_DIR="antyvirus-data-processing"
SRC_DIR="$TARGET_DIR/src"
TESTS_DIR="$TARGET_DIR/tests"
CI_DIR="$TARGET_DIR/.github/workflows"

# Create directory structure
mkdir -p "$SRC_DIR"
mkdir -p "$TESTS_DIR"
mkdir -p "$CI_DIR"

# 1) pyproject.toml with Poetry and tool configuration
cat > "$TARGET_DIR/pyproject.toml" << 'EOF'
[tool.poetry]
name = "antyvirus-data-processing"
version = "0.1.0"
description = "Sales data processing toolkit with VAT calculations and summaries."
license = "MIT"

[tool.poetry.dependencies]
python = ">=3.8,<4.0"
pandas = "^1.5.0"

[tool.poetry.dev-dependencies]
pytest = "^7.0"
mypy = "^1.0"
black = "^23.3.0"
isort = "^5.10.1"
flake8 = "^6.0.0"

[tool.black]
line-length = 88

[tool.isort]
profile = "black"

[tool.mypy]
strict = true
EOF

# 2) setup.cfg for Flake8
cat > "$TARGET_DIR/setup.cfg" << 'EOF'
[flake8]
max-line-length = 88
extend-ignore = E203, W503
EOF

# 3) src/__init__.py
cat > "$SRC_DIR/__init__.py" << 'EOF'
# antyvirus-data-processing package initialization
EOF

# 4) src/processing.py
cat > "$SRC_DIR/processing.py" << 'EOF'
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
EOF

# 5) src/cli.py
cat > "$SRC_DIR/cli.py" << 'EOF'
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
EOF

# 6) tests/test_processing.py
cat > "$TESTS_DIR/test_processing.py" << 'EOF'
import pandas as pd
import pytest
from pathlib import Path
from src.processing import filter_sales, add_vat, summarize_by_manager

@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "Сумма": [5000, 20000, 15000],
        "Дата": pd.to_datetime(["2024-01-02", "2023-12-31", "2024-02-01"]),
        "Менеджер": ["A", "B", "A"]
    })

def test_filter_sales(sample_df):
    result = filter_sales(sample_df, "Сумма", "Дата", 10000, pd.to_datetime("2024-01-01"))
    assert len(result) == 1
    assert result.iloc[0]["Сумма"] == 15000

def test_add_vat(sample_df):
    df_vat = add_vat(sample_df.copy(), "Сумма", 1.2, "Сумма с НДС")
    assert "Сумма с НДС" in df_vat.columns
    assert df_vat.loc[0, "Сумма с НДС"] == pytest.approx(5000 * 1.2)

def test_summarize_by_manager(sample_df):
    df_vat = add_vat(sample_df.copy(), "Сумма", 1.2, "Сумма с НДС")
    summary = summarize_by_manager(df_vat, "Менеджер", "Сумма с НДС")
    total_A = 5000*1.2 + 15000*1.2
    assert summary.loc[summary["Менеджер"] == "A", "Сумма с НДС"].iloc[0] == pytest.approx(total_A)
EOF

# 7) CI workflow for GitHub Actions
cat > "$CI_DIR/ci.yml" << 'EOF'
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    - name: Format check (Black)
      run: poetry run black --check .
    - name: Import order check (isort)
      run: poetry run isort --check-only .
    - name: Type check (mypy)
      run: poetry run mypy src
    - name: Lint (Flake8)
      run: poetry run flake8
    - name: Run tests
      run: poetry run pytest --maxfail=1 --disable-warnings -q
EOF

# 8) README.md
cat > "$TARGET_DIR/README.md" << 'EOF'
# antyvirus-data-processing

A Python toolkit for processing sales data, applying VAT calculations, and generating summary reports.

## Features
- Load sales data from Excel.
- Filter rows based on configurable thresholds and dates.
- Compute VAT-inclusive amounts.
- Summarize VAT totals by manager.
- CLI interface with customizable parameters.
- Logging to console and file.
- Unit tests with pytest.
- Type checking with mypy.
- Code formatting with Black and isort.

## Installation

```bash
# Clone repository
git clone https://github.com/your-org/antyvirus-data-processing.git
cd antyvirus-data-processing

# Install dependencies via Poetry
poetry install
```

## Usage

Run the CLI tool:

```bash
poetry run python -m src.cli \
  --input sales.xlsx \
  --out-filtered filtered.xlsx \
  --out-summary summary.xlsx \
  --min-sum 10000 \
  --start-date 2024-01-01 \
  --vat-rate 1.20
```

## Development

- **Formatting**: `poetry run black .`
- **Import order**: `poetry run isort .`
- **Type checking**: `poetry run mypy src`
- **Linting**: `poetry run flake8`
- **Testing**: `poetry run pytest`

## CI

GitHub Actions workflow is defined in `.github/workflows/ci.yml`, covering formatting checks, type checks, linting, and running tests on push and pull requests.

## License

MIT
EOF

# Make the script executable
chmod +x setup_project.sh

echo "Project scaffolded in '$TARGET_DIR' successfully."
