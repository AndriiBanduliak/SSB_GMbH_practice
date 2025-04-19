# generate_sales_reports

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
