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
