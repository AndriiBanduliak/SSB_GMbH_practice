# Fisher Transform Trading Signal Generator

## Overview

This tool analyzes market data (e.g., hourly candles for BTC/USDT from Binance) using the **Fisher Transform** technical indicator. Its primary goal is to identify potential trend reversal points and generate clear trading signals based on them: **Buy (Long)** or **Sell (Short)**.

The tool is designed for traders looking for an automated way to identify potential entry or exit points based on a proven methodology.

## Key Features

*   **Automated Analysis:** Fetches up-to-date OHLCV (Open, High, Low, Close, Volume) market data.
*   **Fisher Transform Calculation:** Applies the Fisher mathematical transformation to highlight price extremes and reversals.
*   **Signal Generation:** Identifies moments when the indicator crosses the zero line, which is a classic signal for this strategy.
    *   `1`: Buy (Long) signal - indicator crossed above 0 from below.
    *   `-1`: Sell (Short) signal - indicator crossed below 0 from above.
*   **Configurable Parameters:** Allows easy modification of core settings (trading instrument, timeframe, indicator period) to adapt to different markets and strategies.
*   **Clear Output:** Presents results in a convenient table format, showing the timestamp, closing price, indicator value, and the generated signal.

## How It Works (Simplified)

1.  **Data Collection:** The script requests price history (candles) for the selected asset (e.g., BTC/USDT) from the exchange.
2.  **Transformation:** The price data is processed using the Fisher Transform. This transformation "stretches" the value scale, making peaks and troughs (potential reversals) more pronounced and sharper compared to the original price chart.
3.  **Signal Detection:** The tool monitors the Fisher Transform indicator's value. When it crosses the zero mark, it is interpreted as a signal to act:
    *   Crossing upwards (> 0) - potential start of an upward move.
    *   Crossing downwards (< 0) - potential start of a downward move.

## How to Use and Interpret Results

1.  **Run:** Execute the script (e.g., using the command `python your_script_name.py` in the terminal).
2.  **Configuration (if needed):** Before running, you can modify the parameters at the beginning of the script:
    *   `SYMBOL`: Trading pair (e.g., `"ETH/USDT"`, `"SOL/USDT"`).
    *   `TIMEFRAME`: Candle time interval (e.g., `"15m"`, `"4h"`, `"1d"`).
    *   `FISHER_PERIOD`: Indicator calculation period (affects sensitivity; standard is 9-10).
    *   `FETCH_LIMIT`: Number of recent candles to analyze.
3.  **Analyze Output:** The script will display the last few rows of data, including:
    *   `timestamp`: Date and time of the candle's close.
    *   `close`: Closing price for that candle.
    *   `fisher`: Calculated value of the Fisher Transform indicator.
    *   `signal`: The generated trading signal:
        *   **`1`**: A **Buy (Long)** signal was generated at the close of this candle. Consider entering a long position.
        *   **`-1`**: A **Sell (Short)** signal was generated at the close of this candle. Consider entering a short position.
        *   **`0`**: No new signal was generated on this candle.



## Important Notes

*   **Not Financial Advice:** This tool provides technical analysis and signals based on it. It is NOT investment advice. All trading decisions are made at your own risk.
*   **Confirmation Recommended:** Fisher Transform signals are most effective when used in conjunction with other analysis methods (e.g., trend analysis, support/resistance levels, volume, other indicators). Do not rely solely on one indicator.
*   **Optimization and Backtesting:** Signal effectiveness can vary depending on the chosen instrument, timeframe, and market conditions. It is recommended to perform backtesting (testing on historical data) and parameter optimization before using in live trading.
*   **Risk Management:** Always use stop-losses and other risk management techniques when trading.

## Requirements

The script requires the following Python libraries to be installed:
*   `ccxt`
*   `pandas`
*   `numpy`

You can install them using pip:
```bash
pip install ccxt pandas numpy