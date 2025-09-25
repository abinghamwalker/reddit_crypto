# src/acquisition/fetch_reddit_data.py

import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from psaw import PushshiftAPI

# --- Configuration ---
SUBREDDITS = ["CryptoCurrency", "Bitcoin", "ethereum"]
KEYWORDS = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum", "eth", "ether"],
}
# Define the date range to match the market data script
END_DATE = datetime.now(timezone.utc)
START_DATE = END_DATE - timedelta(days=365)

OUTPUT_DIR = "data/raw"

# --- Helper Function ---
def get_mentioned_crypto(text, keywords):
    """Checks if any crypto keywords are present in the text and returns their symbols."""
    # This function remains the same
    mentioned = []
    text_lower = text.lower()
    for crypto, keys in keywords.items():
        if any(key in text_lower for key in keys):
            mentioned.append(crypto)
    return mentioned if mentioned else None

# --- Main Function ---
def fetch_and_save_reddit_data(subreddits, keywords, start_date, end_date, output_dir):
    """Scrapes posts from a specific date range using the Pushshift API.

    This function queries the Pushshift database for all submissions (posts) in
    the given subreddits that were created between the start and end dates.
    The filename of the output is generated dynamically based on the date range.

    Args:
        subreddits (list[str]): A list of subreddit names to scrape.
        keywords (dict[str, list[str]]): A dictionary for mapping keywords to crypto symbols.
        start_date (datetime): The starting date and time for the scrape (UTC).
        end_date (datetime): The ending date and time for the scrape (UTC).
        output_dir (str): The relative path to the directory for the output file.

    Returns:
        None: Creates a descriptively named Parquet file in the output directory.
    """
    load_dotenv()
    print("--- Starting Reddit Data Scrape (Historical) ---")

    api = PushshiftAPI()

    # Convert datetime objects to Unix timestamps for the API
    start_epoch = int(start_date.timestamp())
    end_epoch = int(end_date.timestamp())

    print(f"Searching for posts from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Search for submissions within the date range across all specified subreddits
    # PSAW can be slow for very large queries, but it is the correct tool for the job.
    generator = api.search_submissions(
        after=start_epoch,
        before=end_epoch,
        subreddit=",".join(subreddits), # Comma-separated list of subreddits
        filter=['id', 'created_utc', 'subreddit', 'title', 'selftext', 'score', 'num_comments'],
        limit=None # Set to None to get all results in the date range
    )

    all_posts = []
    print("Fetching posts from Pushshift... (This may take a while)")
    for post in generator:
        # PSAW returns a dictionary-like object, not a PRAW submission object
        # The 'd_' attribute provides a dictionary view
        post_data = post.d_
        
        # Some posts might be missing a title or body
        title = post_data.get('title', '')
        body = post_data.get('selftext', '')
        
        # Skip posts with removed body text
        if body in ['[removed]', '[deleted]']:
            continue
            
        combined_text = title + " " + body
        mentioned_cryptos = get_mentioned_crypto(combined_text, keywords)
        
        if mentioned_cryptos:
            all_posts.append({
                "post_id": post_data.get('id'),
                "timestamp_utc": datetime.fromtimestamp(post_data.get('created_utc'), tz=timezone.utc),
                "subreddit": post_data.get('subreddit'),
                "title": title,
                "body": body,
                "score": post_data.get('score'),
                "num_comments": post_data.get('num_comments'),
                "mentioned_crypto": mentioned_cryptos,
            })
        
        if len(all_posts) % 1000 == 0 and len(all_posts) > 0:
            print(f"  ... collected {len(all_posts)} relevant posts so far.")

    if not all_posts:
        print("\nWARNING: No relevant posts were found in the specified date range.")
        return

    # --- Save Data to Parquet with Descriptive Filename ---
    print(f"\nCollected a total of {len(all_posts)} relevant posts.")
    print("Converting collected data to DataFrame...")
    df = pd.DataFrame(all_posts)
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
    
    # Generate descriptive filename based on date range
    start_tag = start_date.strftime('%Y%m%d')
    end_tag = end_date.strftime('%Y%m%d')
    filename = f"raw_reddit_data_{start_tag}_to_{end_tag}.parquet"
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    df.to_parquet(filepath)

    print(f"Successfully saved data to '{filepath}'")
    print("--- Reddit Data Scrape Complete ---")

# --- Script Execution ---
if __name__ == "__main__":
    fetch_and_save_reddit_data(
        subreddits=SUBREDDITS,
        keywords=KEYWORDS,
        start_date=START_DATE,
        end_date=END_DATE,
        output_dir=OUTPUT_DIR,
    )