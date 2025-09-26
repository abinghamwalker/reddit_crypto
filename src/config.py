# src/config.py

"""
Central configuration file for the crypto sentiment analysis project.
This file contains all the key parameters for data acquisition, processing,
and analysis to ensure consistency across all scripts.
"""
import os
from datetime import datetime, timedelta, timezone

# --- Data Acquisition Parameters ---

# Defines the tickers for market data fetching
TICKERS = ["BTC-USD", "ETH-USD"]

# Defines the subreddits for Reddit data scraping
SUBREDDITS = ["CryptoCurrency", "Bitcoin", "ethereum"]

# Defines the keywords to identify relevant posts for each crypto
KEYWORDS = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum", "eth", "ether"],
}

# --- Time and Interval Parameters ---

# Defines the frequency for market data (e.g., "1h", "4h", "1d")
MARKET_DATA_INTERVAL = "1h"

# Defines the total historical period for data collection
DAYS_OF_DATA = 365
END_DATE = datetime.now(timezone.utc)
START_DATE = END_DATE - timedelta(days=DAYS_OF_DATA)

# --- File Path Parameters ---

# Defines the directory for storing raw, unprocessed data
RAW_DATA_DIR = "data/raw"

# Defines the directory for storing processed, intermediate data
PROCESSED_DATA_DIR = "data/processed"

# Defines the directory for storing final analysis results
RESULTS_DIR = "results"

# --- Specific File Paths (Derived from above) ---

POST_LIMIT_PER_SUB = 5000

# Constructing raw data paths for easy access
RAW_BTC_MARKET_DATA_PATH = os.path.join(RAW_DATA_DIR, f"btc_usd_market_data_{MARKET_DATA_INTERVAL}.parquet")
RAW_ETH_MARKET_DATA_PATH = os.path.join(RAW_DATA_DIR, f"eth_usd_market_data_{MARKET_DATA_INTERVAL}.parquet")
start_tag = START_DATE.strftime('%Y%m%d')
end_tag = END_DATE.strftime('%Y%m%d')
RAW_REDDIT_DATA_PATH = os.path.join(RAW_DATA_DIR, f"raw_reddit_data_aggressive-praw_limit{POST_LIMIT_PER_SUB}.parquet")

# Constructin cleaned data paths
CLEANED_REDDIT_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "cleaned_reddit_data.parquet")
CLEANED_BTC_MARKET_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, f"cleaned_btc_market_data_{MARKET_DATA_INTERVAL}.parquet")
CLEANED_ETH_MARKET_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, f"cleaned_eth_market_data_{MARKET_DATA_INTERVAL}.parquet")
PROCESSED_SENTIMENT_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "sentiment_data.parquet")
MASTER_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "master_data.parquet")