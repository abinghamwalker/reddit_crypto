# main.py

import sys
import os
import argparse # Import the library

# Add the project root to the Python path.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now we can import our modules from the 'src' package
from src import config
from src.acquisition.fetch_market import fetch_and_save_market_data
from src.acquisition.fetch_reddit import fetch_and_save_reddit_data
from src.processing.process_sentiment import process_and_save_sentiment
from src.processing.unify_data import unify_and_save_data
from src.processing.clean_reddit_data import clean_and_save_reddit_data
from src.processing.clean_market_data import clean_and_save_market_data
from src.analysis.correlation_analysis import run_correlation_sweep



def main():
    """Main function to orchestrate the data pipeline."""
    
    # --- 1. Set up Command-Line Argument Parsing ---
    parser = argparse.ArgumentParser(description="Run the Crypto Sentiment Analysis pipeline.")
    parser.add_argument(
        'stages',
        metavar='stage',
        nargs='*', # '*' means you can provide zero, one, or multiple stages
        help='The stage(s) of the pipeline to run: acquire, process, analyze. If no stages are provided, all will be run.'
    )
    args = parser.parse_args()
    
    # If no specific stages are provided, run all of them
    run_all = not args.stages
    
    print("--- Starting the Crypto Sentiment Analysis Pipeline ---")
    
    # --- 2. Define and Conditionally Run Each Stage ---

    # Stage 1: ACQUIRE
    if run_all or 'acquire' in args.stages:
        print("\n>>> STAGE: ACQUIRE - Fetching raw data...")
        
        print("\n> Sub-step: Fetching Market Data...")
        fetch_and_save_market_data(
            tickers=config.TICKERS,
            start=config.START_DATE,
            end=config.END_DATE,
            interval=config.MARKET_DATA_INTERVAL,
            output_dir=config.RAW_DATA_DIR
        )

        print("\n> Sub-step: Fetching Reddit Data...")
        fetch_and_save_reddit_data(
            subreddits=config.SUBREDDITS,
            keywords=config.KEYWORDS,
            output_dir=config.RAW_DATA_DIR,
            post_limit_per_sub=config.POST_LIMIT_PER_SUB
        )

    # Stage 2: CLEAN
    if run_all or 'clean' in args.stages:
        print("\n>>> STAGE: CLEAN - Cleaning raw Reddit data...")
        clean_and_save_reddit_data(
            input_path=config.RAW_REDDIT_DATA_PATH,
            output_dir=config.PROCESSED_DATA_DIR
        )

        print("\n> Sub-step: Cleaning BTC Market Data...")
        clean_and_save_market_data(
            input_path=config.RAW_BTC_MARKET_DATA_PATH,
            output_path=config.CLEANED_BTC_MARKET_DATA_PATH,
            ticker_name="BTC"
        )
        
        print("\n> Sub-step: Cleaning ETH Market Data...")
        clean_and_save_market_data(
            input_path=config.RAW_ETH_MARKET_DATA_PATH,
            output_path=config.CLEANED_ETH_MARKET_DATA_PATH,
            ticker_name="ETH"
        )

    # Stage 3: PROCESS
    if run_all or 'process' in args.stages:
        print("\n>>> STAGE: PROCESS - Processing and unifying data...")

        print("\n> Sub-step: Processing Sentiment...")
        process_and_save_sentiment(
            input_path=config.CLEANED_REDDIT_DATA_PATH,
            output_dir=config.PROCESSED_DATA_DIR
        )

        print("\n> Sub-step: Unifying Data...")
        unify_and_save_data(
            sentiment_path=config.PROCESSED_SENTIMENT_DATA_PATH, 
            btc_path=config.CLEANED_BTC_MARKET_DATA_PATH,
            eth_path=config.CLEANED_ETH_MARKET_DATA_PATH,
            output_dir=config.PROCESSED_DATA_DIR
        )
        
    # Stage 4: ANALYZE
    if run_all or 'analyze' in args.stages:
        print("\n>>> STAGE: ANALYZE - Running correlation analysis...")
        run_correlation_sweep(
            data_path=config.MASTER_DATA_PATH,
            output_dir=config.RESULTS_DIR
        )

    print("\n--- Pipeline Finished ---")


if __name__ == "__main__":
    main()