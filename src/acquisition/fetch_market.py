# src/acquisition/fetch_market.py

import os
import yfinance as yf
import pandas as pd
from src import config


# --- Main Function ---
def fetch_and_save_market_data(tickers, start, end, interval, output_dir):
    """
    Fetches historical market data for a list of tickers from Yahoo Finance
    and saves each ticker's data to a separate, efficient Parquet file.
    
    The output filename will include the data interval for clarity.

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
        print(f"\nFetching data for {ticker} at {interval} interval...")
        try:
            # Download data from Yahoo Finance
            data = yf.download(
                tickers=ticker, 
                start=start, 
                end=end, 
                interval=interval, 
                progress=False,
                auto_adjust=False
            )
            
            if data.empty:
                print(f"WARNING: No data found for {ticker} in the specified date range. Skipping.")
                continue

            # --- Data Cleaning ---
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            data.columns = [str(col).lower() for col in data.columns]
            
            if 'adj close' in data.columns:
                data.rename(columns={'adj close': 'adj_close'}, inplace=True)
            
            data.index.name = 'timestamp'
            
            print(f"Successfully downloaded {len(data)} rows of data for {ticker}.")

            # --- Save Data to Parquet with new filename format ---
            filename = f"{ticker.replace('-','_').lower()}_market_data_{interval}.parquet"
            filepath = os.path.join(output_dir, filename)
            data.to_parquet(filepath)
            print(f"Data saved to '{filepath}'")

        except Exception as e:
            print(f"ERROR: Could not fetch or process data for {ticker}. Reason: {e}")

    print("\n--- Market Data Download Complete ---")

