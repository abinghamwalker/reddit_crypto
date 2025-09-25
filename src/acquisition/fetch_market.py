# src/acquisition/fetch_market.py

import os
import yfinance as yf
import pandas as pd
from datetime import date, timedelta


# --- Configuration ---
TICKERS = ["BTC-USD", "ETH-USD"]
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=365)
INTERVAL = "1h" 
# Use a relative path, which is better practice
OUTPUT_DIR = "data/raw"

# --- Main Function ---
def fetch_and_save_market_data(tickers, start, end, interval, output_dir):
    """
    Fetches historical market data for a list of tickers from Yahoo Finance
    and saves each ticker's data to a separate, efficient Parquet file.
    
    This function prints its progress to the console and handles cases where
    no data is found for a specific ticker by printing a warning and skipping it.

    Args:
        tickers (list[str]): A list of strings representing the crypto/stock tickers
                             to process (e.g., ["BTC-USD", "ETH-USD"]).
        start (datetime.date): The start date for the data download.
        end (datetime.date): The end date for the data download.
        interval (str): The data interval frequency. Valid yfinance intervals
                        include "1h", "1d", "5d", "1wk", "1mo".
        output_dir (str): The directory path to save the output Parquet files to.
                          The directory will be created if it does not exist.

    Returns:
        None: This function does not return any value. It saves files directly
              to the disk within the specified output_dir.
    """
    print("--- Starting Market Data Download ---")
    os.makedirs(output_dir, exist_ok=True)

    for ticker in tickers:
        print(f"\nFetching data for {ticker}...")
        try:
            # Download data from Yahoo Finance
            # Explicitly set auto_adjust=False to get 'Adj Close' column if needed,
            # though we are not using it here. It's good practice to be explicit.
            data = yf.download(
                tickers=ticker, 
                start=start, 
                end=end, 
                interval=interval, 
                progress=False,
                auto_adjust=False  # Being explicit can prevent future issues
            )
            
            if data.empty:
                print(f"WARNING: No data found for {ticker} in the specified date range. Skipping.")
                continue

            # --- ROBUST DATA CLEANING (THE FIX IS HERE) ---
            # 1. Handle potential MultiIndex columns returned by newer yfinance versions
            if isinstance(data.columns, pd.MultiIndex):
                # Flatten the MultiIndex by taking the first level
                data.columns = data.columns.get_level_values(0)

            # 2. Convert all column names to lowercase strings for consistency
            data.columns = [str(col).lower() for col in data.columns]
            
            # 3. Rename 'adj close' to 'adj_close' for consistency
            if 'adj close' in data.columns:
                data.rename(columns={'adj close': 'adj_close'}, inplace=True)
            
            # 4. Ensure the index has a name
            data.index.name = 'timestamp'
            
            print(f"Successfully downloaded {len(data)} rows of data for {ticker}.")

            # --- Save Data to Parquet ---
            filename = f"{ticker.replace('-','_').lower()}_market_data.parquet"
            filepath = os.path.join(output_dir, filename)
            data.to_parquet(filepath)
            print(f"Data saved to '{filepath}'")

        except Exception as e:
            print(f"ERROR: Could not fetch or process data for {ticker}. Reason: {e}")

    print("\n--- Market Data Download Complete ---")

# --- Script Execution ---
if __name__ == "__main__":
    fetch_and_save_market_data(
        tickers=TICKERS,
        start=START_DATE,
        end=END_DATE,
        interval=INTERVAL,
        output_dir=OUTPUT_DIR
    )