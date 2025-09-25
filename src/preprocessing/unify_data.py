# src/processing/unify_data.py

import os
import pandas as pd

# --- Configuration ---
SENTIMENT_DATA_PATH = "data/processed/sentiment_data.parquet"
BTC_MARKET_DATA_PATH = "data/raw/btc_usd_market_data.parquet"
ETH_MARKET_DATA_PATH = "data/raw/eth_usd_market_data.parquet"
OUTPUT_DIR = "data/master"

# --- Main Function ---
def unify_and_save_data(sentiment_path, btc_path, eth_path, output_dir):
    """
    Unifies market and sentiment data into a single hourly time-series DataFrame.

    This function performs the following steps:
    1. Loads sentiment and market data.
    2. Aggregates post-level sentiment into hourly metrics (mean sentiment, post count).
    3. Pivots the sentiment data to create crypto-specific columns (e.g., BTC_sentiment).
    4. Merges the market data for BTC and ETH.
    5. Standardizes all timestamp indexes to UTC.
    6. Joins the aggregated sentiment data with the merged market data.
    7. Fills missing sentiment values with 0.
    8. Saves the final master DataFrame to a Parquet file.

    Args:
        sentiment_path (str): Path to the sentiment data Parquet file.
        btc_path (str): Path to the BTC market data Parquet file.
        eth_path (str): Path to the ETH market data Parquet file.
        output_dir (str): Directory to save the final master data file.

    Returns:
        None: Saves a file named `master_data.parquet` to the output directory.
    """
    print("--- Starting Data Unification ---")

    # --- Load All Datasets ---
    try:
        print("Loading datasets...")
        sentiment_df = pd.read_parquet(sentiment_path)
        btc_df = pd.read_parquet(btc_path)
        eth_df = pd.read_parquet(eth_path)
    except FileNotFoundError as e:
        print(f"ERROR: Could not find a required data file: {e}. "
              "Please ensure all acquisition and processing scripts have run successfully.")
        return

    # --- 1. Aggregate Sentiment Data ---
    print("Aggregating sentiment data to an hourly frequency...")
    sentiment_df = sentiment_df.explode('mentioned_crypto')
    sentiment_df.set_index('timestamp_utc', inplace=True)

    # Note: Corrected '1H' to '1h' to address Future Warning
    sentiment_agg = sentiment_df.groupby('mentioned_crypto').resample('1h').agg(
        sentiment_mean=('sentiment_score', 'mean'),
        post_count=('post_id', 'count')
    )
    sentiment_agg.reset_index(inplace=True)

    # --- 2. Pivot Sentiment Data ---
    print("Pivoting sentiment data to create crypto-specific columns...")
    sentiment_pivot = sentiment_agg.pivot(
        index='timestamp_utc',
        columns='mentioned_crypto',
        values=['sentiment_mean', 'post_count']
    )
    sentiment_pivot.columns = [f"{crypto.lower()}_{metric}" for metric, crypto in sentiment_pivot.columns]

    # --- 3. Merge and Standardize Datasets ---
    print("Merging market data and standardizing timezones to UTC...")
    btc_df = btc_df.add_prefix('btc_')
    eth_df = eth_df.add_prefix('eth_')
    market_df = btc_df.join(eth_df, how='outer')

    # --- THE FIX IS HERE ---
    # 1. Convert the timezone-aware market_df index to UTC.
    market_df.index = market_df.index.tz_convert('UTC')

    # 2. Make the timezone-naive sentiment_pivot index aware of its UTC nature.
    sentiment_pivot.index = sentiment_pivot.index.tz_localize('UTC')
    # --- END OF FIX ---

    # Now both indexes are timezone-aware and in UTC, so they can be joined.
    master_df = market_df.join(sentiment_pivot, how='left')

    # --- 4. Final Cleaning ---
    print("Cleaning the final master DataFrame...")
    sentiment_columns = [col for col in master_df.columns if 'sentiment' in col or 'post_count' in col]
    master_df[sentiment_columns] = master_df[sentiment_columns].fillna(0)
    master_df.ffill(inplace=True)

    # --- Save Master DataFrame ---
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "master_data.parquet")
    master_df.to_parquet(output_path)

    print(f"\nSuccessfully created and saved the master dataset with {len(master_df)} rows.")
    print(f"Master data saved to '{output_path}'")
    print("--- Data Unification Complete ---")

    print("\nSample of the master DataFrame:")
    print(master_df.head())
    print("\nDataFrame Info:")
    master_df.info()

# --- Script Execution ---
if __name__ == "__main__":
    unify_and_save_data(
        sentiment_path=SENTIMENT_DATA_PATH,
        btc_path=BTC_MARKET_DATA_PATH,
        eth_path=ETH_MARKET_DATA_PATH,
        output_dir=OUTPUT_DIR,
    )