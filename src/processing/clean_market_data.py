# src/processing/clean_market_data.py

import os
import pandas as pd

# --- Configuration ---
try:
    from src import config
except ImportError:
    config = None

# --- Main Cleaning Function ---
def clean_and_save_market_data(input_path, output_path, ticker_name):
    """
    Loads raw market data, applies cleaning and validation rules, and saves the result.

    Cleaning & Validation Rules:
    1.  Checks for and forward-fills missing timestamps in the hourly index.
    2.  Removes any duplicate timestamps.
    3.  Removes rows where 'close' price is zero or negative.
    4.  Removes rows where the OHLC logic is invalid (e.g., low > high).
    5.  Logs a warning if a significant number of zero-volume hours are present.

    Args:
        input_path (str): The file path for the raw market data Parquet file.
        output_path (str): The full file path to save the cleaned data to.
        ticker_name (str): The name of the ticker (e.g., "BTC") for logging.

    Returns:
        None: Saves the cleaned data to the specified output_path.
    """
    print(f"--- Starting Market Data Cleaning for {ticker_name.upper()} ---")

    # --- Load Data ---
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found at '{input_path}'.")
        return

    df = pd.read_parquet(input_path)
    initial_rows = len(df)
    print(f"Loaded {initial_rows} raw data points.")

    # --- Apply Cleaning Rules ---
    # 1. Ensure complete hourly index and forward-fill gaps
    full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='1h')
    df = df.reindex(full_range).ffill()
    if len(df) > initial_rows:
        print(f"  - Filled {len(df) - initial_rows} missing timestamps.")

    # 2. Remove duplicate timestamps
    df = df[~df.index.duplicated(keep='first')]
    if len(df) < initial_rows:
        print(f"  - Removed {initial_rows - len(df)} duplicate timestamps.")
    
    initial_rows = len(df) # Reset row count for next checks

    # 3. Validate Price Sanity (close price <= 0)
    df = df[df['close'] > 0]
    if len(df) < initial_rows:
        print(f"  - Removed {initial_rows - len(df)} rows with zero or negative close price.")

    initial_rows = len(df)

    # 4. Validate OHLC Logic
    invalid_ohlc = (df['high'] < df['low']) | \
                   (df['high'] < df['open']) | \
                   (df['high'] < df['close']) | \
                   (df['low'] > df['open']) | \
                   (df['low'] > df['close'])
    df = df[~invalid_ohlc]
    if len(df) < initial_rows:
        print(f"  - Removed {initial_rows - len(df)} rows with invalid OHLC logic.")
        
    # 5. Check for Zero Volume
    zero_volume_count = (df['volume'] == 0).sum()
    if zero_volume_count > 0:
        print(f"  - INFO: Found {zero_volume_count} hours ({zero_volume_count/len(df):.2%}) with zero volume.")

    # --- Save Cleaned Data ---
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    df.to_parquet(output_path)
    
    print(f"\nCleaned data has {len(df)} rows.")
    print(f"Cleaned {ticker_name.upper()} data saved to '{output_path}'")
    print(f"--- Market Data Cleaning Complete for {ticker_name.upper()} ---")

