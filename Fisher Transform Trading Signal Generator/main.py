import ccxt
import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, Any

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
# Use constants for parameters that might change or be used in multiple places
SYMBOL = "BTC/USDT"
TIMEFRAME = "1h"
FETCH_LIMIT = 500
FISHER_PERIOD = 10
FISHER_SMOOTHING_PERIOD = 2 # Explicitly define the smoothing period
VALUE_CLIP_LIMIT = 0.999   # Constant for clipping the normalized value
EPSILON = 1e-9             # Small value to prevent division by zero

# --- Functions ---

def fetch_ohlcv_data(exchange: ccxt.Exchange, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
    """
    Fetches OHLCV data from the specified exchange.

    Args:
        exchange: An initialized ccxt exchange instance.
        symbol: The trading symbol (e.g., "BTC/USDT").
        timeframe: The timeframe string (e.g., "1h", "4h", "1d").
        limit: The maximum number of candles to fetch.

    Returns:
        A pandas DataFrame with OHLCV data and standardized column names
        ['timestamp', 'open', 'high', 'low', 'close', 'volume'], or None if fetching fails.
        Returns None on error.
    """
    logging.info(f"Fetching {limit} candles for {symbol} on timeframe {timeframe} from {exchange.id}")
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if not ohlcv:
            logging.warning(f"No data returned for {symbol} {timeframe}.")
            return None

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Ensure numeric columns have the correct data type
        for col in ["open", "high", "low", "close", "volume"]:
             df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove rows with NaN in price columns, as they cannot be used in calculations
        df.dropna(subset=["open", "high", "low", "close"], inplace=True)

        logging.info(f"Successfully fetched and processed {len(df)} candles.")
        return df
    except ccxt.NetworkError as e:
        logging.error(f"Network error fetching data for {symbol}: {e}")
        return None
    except ccxt.ExchangeError as e:
        logging.error(f"Exchange error fetching data for {symbol}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during data fetching: {e}")
        return None

def calculate_fisher_transform(df: pd.DataFrame, period: int = FISHER_PERIOD, smooth_period: Optional[int] = FISHER_SMOOTHING_PERIOD) -> pd.DataFrame:
    """
    Calculates the Fisher Transform indicator.

    Args:
        df: DataFrame with 'high' and 'low' columns.
        period: The lookback period for finding min/max of HL2.
        smooth_period: The period for smoothing the Fisher Transform.
                       If None, no smoothing is applied.

    Returns:
        The input DataFrame with a new 'fisher' column added.
    """
    if not all(col in df.columns for col in ['high', 'low']):
        raise ValueError("DataFrame must contain 'high' and 'low' columns.")
    if len(df) < period:
        logging.warning(f"DataFrame length ({len(df)}) is less than Fisher period ({period}). Cannot calculate Fisher Transform.")
        df['fisher'] = np.nan
        return df

    # Calculate HL2 (typical price)
    hl2 = (df["high"] + df["low"]) / 2

    # Find the minimum and maximum of HL2 over the period
    min_low = hl2.rolling(window=period).min()
    max_high = hl2.rolling(window=period).max()

    # Normalize the HL2 value to the range [-1, 1]
    # Add EPSILON to prevent division by zero if max_high == min_low
    normalized_value = 2 * ((hl2 - min_low) / (max_high - min_low + EPSILON) - 0.5)

    # Clip the value to avoid infinity in np.log for values exactly 1 or -1
    clipped_value = normalized_value.clip(-VALUE_CLIP_LIMIT, VALUE_CLIP_LIMIT)

    # Calculate the raw Fisher Transform
    # Formula: 0.5 * ln((1 + x) / (1 - x))
    raw_fisher = 0.5 * np.log((1 + clipped_value) / (1 - clipped_value))

    # Apply smoothing (if a period is specified and > 1)
    if smooth_period and smooth_period > 1:
         # Use rolling().mean() for smoothing
        df['fisher'] = raw_fisher.rolling(window=smooth_period).mean()
        logging.info(f"Calculated Fisher Transform with period={period} and smoothed over {smooth_period} periods.")
    else:
        df['fisher'] = raw_fisher
        logging.info(f"Calculated Fisher Transform with period={period} (unsmoothed).")

    # Handle initial NaN values resulting from the rolling window calculation
    # Optional: Fill NaNs with 0 if signals are needed from the very beginning
    # df['fisher'].fillna(0, inplace=True)

    return df

def generate_trading_signals(df: pd.DataFrame, fisher_col: str = 'fisher') -> pd.DataFrame:
    """
    Generates trading signals based on the Fisher Transform crossing the zero line.

    Args:
        df: DataFrame with the Fisher Transform column (e.g., 'fisher').
        fisher_col: Name of the column containing Fisher Transform values.

    Returns:
        DataFrame with a new 'signal' column:
         1: Bullish crossover (Fisher crosses above 0)
        -1: Bearish crossover (Fisher crosses below 0)
         0: No signal
    """
    if fisher_col not in df.columns:
         raise ValueError(f"Fisher column '{fisher_col}' not found in DataFrame.")

    df['signal'] = 0 # Initialize signal column with no signal

    # Long condition: current Fisher > 0 AND previous Fisher <= 0
    long_condition = (df[fisher_col] > 0) & (df[fisher_col].shift(1) <= 0)
    # Short condition: current Fisher < 0 AND previous Fisher >= 0
    short_condition = (df[fisher_col] < 0) & (df[fisher_col].shift(1) >= 0)

    # Assign signals based on conditions
    df.loc[long_condition, 'signal'] = 1
    df.loc[short_condition, 'signal'] = -1

    logging.info("Generated trading signals based on Fisher Transform zero crosses.")
    return df

# --- Main Execution Logic ---
def main():
    """
    Main function to run the Fisher Transform signal generation process.
    """
    # Initialize the exchange
    try:
        # API key/secret can be added here or within ccxt.binance({...}) if needed for private endpoints
        exchange = ccxt.binance()
        # Check API availability (optional but good practice)
        exchange.load_markets()
        logging.info(f"Successfully connected to {exchange.id}.")
    except Exception as e:
        logging.error(f"Failed to initialize exchange: {e}")
        return # Exit if connection fails

    # 1. Fetch Data
    df_ohlcv = fetch_ohlcv_data(exchange, SYMBOL, TIMEFRAME, FETCH_LIMIT)

    if df_ohlcv is None or df_ohlcv.empty:
        logging.error("Failed to fetch or process OHLCV data. Exiting.")
        return # Exit if no data is available

    # 2. Calculate Indicator
    try:
        # Create a copy to avoid modifying the original fetched data if reused
        df_with_fisher = calculate_fisher_transform(df_ohlcv.copy(), period=FISHER_PERIOD, smooth_period=FISHER_SMOOTHING_PERIOD)
        # Alternative: calculate without smoothing
        # df_with_fisher = calculate_fisher_transform(df_ohlcv.copy(), period=FISHER_PERIOD, smooth_period=None)
    except ValueError as e:
        logging.error(f"Error calculating Fisher Transform: {e}")
        return # Exit on calculation error

    # 3. Generate Signals
    try:
        df_final = generate_trading_signals(df_with_fisher)
    except ValueError as e:
        logging.error(f"Error generating trading signals: {e}")
        return # Exit on signal generation error

    # 4. Output Results (for demonstration)
    # In production, this step might be replaced by sending alerts, placing orders, storing to DB, etc.
    logging.info("Final DataFrame with signals (last 10 rows):")
    # Use print for DataFrame output as logging is not ideal for table formatting
    print(df_final[["timestamp", "close", "fisher", "signal"]].tail(10).to_string())

    # Placeholder for further actions: signal execution, notifications, etc.
    # e.g., execute_trade(df_final.iloc[-1]) if df_final.iloc[-1]['signal'] != 0 else None

if __name__ == "__main__":
    main()