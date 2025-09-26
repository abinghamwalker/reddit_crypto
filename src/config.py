# src/config.py

"""
Central configuration file for the crypto sentiment analysis project.
This file contains all the key parameters for data acquisition, processing,
and analysis to ensure consistency across all scripts.
"""

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

# Defines the total historical period for data collection
DAYS_OF_DATA = 365
END_DATE = datetime.now(timezone.utc)
START_DATE = END_DATE - timedelta(days=DAYS_OF_DATA)

# Defines the frequency for market data (e.g., "1h", "4h", "1d")
MARKET_DATA_INTERVAL = "1h"

# --- File Path Parameters ---

# Defines the directory for storing raw, unprocessed data
RAW_DATA_DIR = "data/raw"

# Defines the directory for storing processed, intermediate data
PROCESSED_DATA_DIR = "data/processed"

# Defines the directory for storing final analysis results
RESULTS_DIR = "results"