# src/processing/process_sentiment.py

import os
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- Configuration ---
INPUT_FILE = "data/raw/raw_reddit_data.parquet"
OUTPUT_DIR = "data/processed"

# --- Main Function ---
def process_and_save_sentiment(input_path, output_dir):
    """Loads raw Reddit data, calculates sentiment scores, and saves the results.

    This function uses the VADER sentiment analysis tool to score the combined
    text of each post's title and body. It adds a 'sentiment_score' column
    to the DataFrame.

    Args:
        input_path (str): The file path for the input Parquet file containing
                          raw Reddit posts.
        output_dir (str): The directory path to save the output Parquet file to.

    Returns:
        None: Saves a file named `sentiment_data.parquet` to the output directory.
    """
    print("--- Starting Sentiment Processing ---")

    # --- Load Data ---
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found at '{input_path}'. "
              "Please run the Reddit data acquisition script first.")
        return

    print(f"Loading raw data from '{input_path}'...")
    df = pd.read_parquet(input_path)

    # --- Sentiment Analysis ---
    print("Initializing VADER sentiment analyzer...")
    analyzer = SentimentIntensityAnalyzer()

    def get_vader_score(text):
        """Calculates the VADER compound sentiment score for a given text."""
        # The 'compound' score is a single, normalized metric from -1 to +1.
        return analyzer.polarity_scores(text)['compound']

    print("Calculating sentiment scores for each post...")
    # Combine title and body for a more comprehensive sentiment analysis
    df['text'] = df['title'] + " " + df['body'].fillna('')
    df['sentiment_score'] = df['text'].apply(get_vader_score)

    # We can now drop the combined text column as it's no longer needed
    df.drop(columns=['text'], inplace=True)

    # --- Save Data ---
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sentiment_data.parquet")
    df.to_parquet(output_path)

    print(f"\nSuccessfully processed {len(df)} posts.")
    print(f"Sentiment data saved to '{output_path}'")
    print("--- Sentiment Processing Complete ---")
    
    # Display a sample of the results
    print("\nSample of the output data:")
    print(df[['timestamp_utc', 'title', 'sentiment_score']].head())


# --- Script Execution ---
if __name__ == "__main__":
    process_and_save_sentiment(
        input_path=INPUT_FILE,
        output_dir=OUTPUT_DIR
    )