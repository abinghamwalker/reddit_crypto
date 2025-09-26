# src/processing/clean_data.py

import os
import pandas as pd

# --- Configuration ---
try:
    from src import config
except ImportError:
    config = None

# --- Main Cleaning Function ---
def clean_and_save_reddit_data(input_path, output_dir):
    """
    Loads raw Reddit data, applies cleaning rules, and saves the cleaned data.

    Current Cleaning Rules:
    1.  Filters out any post that contains 'http' in its title or body.
    2.  Removes posts with a body of '[removed]' or '[deleted]'.

    Args:
        input_path (str): The file path for the raw Reddit data Parquet file.
        output_dir (str): The directory to save the cleaned output Parquet file to.

    Returns:
        None: Saves a file named `cleaned_reddit_data.parquet` to the output directory.
    """
    print("--- Starting Data Cleaning ---")

    # --- Load Data ---
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found at '{input_path}'. "
              "Please run the 'acquire' stage first.")
        return

    print(f"Loading raw data from '{input_path}'...")
    df = pd.read_parquet(input_path)
    initial_rows = len(df)
    print(f"Loaded {initial_rows} posts.")

    # --- Apply Cleaning Rules ---
    # Rule 1: Remove posts with '[removed]' or '[deleted]' body text.
    df = df[~df['body'].isin(['[removed]', '[deleted]'])]
    rows_after_removed = len(df)
    print(f"  - Removed {initial_rows - rows_after_removed} posts with '[removed]'/'[deleted]' body.")

    # Rule 2: Remove any posts containing a URL in the title OR body.
    df = df[~df['title'].str.contains('http', case=False, na=False) & 
            ~df['body'].fillna('').str.contains('http', case=False, na=False)]
    rows_after_urls = len(df)
    print(f"  - Removed {rows_after_removed - rows_after_urls} posts containing URLs.")
    
    # --- Save Cleaned Data ---
    if len(df) == 0:
        print("WARNING: All posts were removed after cleaning. No output file will be created.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    filename = "cleaned_reddit_data.parquet"
    output_path = os.path.join(output_dir, filename)
    df.to_parquet(output_path)
    
    print(f"\nCleaned data has {len(df)} posts (retained {len(df)/initial_rows:.2%}).")
    print(f"Cleaned data saved to '{output_path}'")
    print("--- Data Cleaning Complete ---")

