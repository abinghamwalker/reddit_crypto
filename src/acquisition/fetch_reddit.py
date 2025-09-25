# src/acquisition/fetch_reddit_data.py

import os
import praw
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# --- Configuration ---
SUBREDDITS = ["CryptoCurrency", "Bitcoin", "ethereum"]
# For development, limit the number of posts to fetch per subreddit.
# Set to None to fetch the maximum allowed by PRAW (around 1000).
POST_LIMIT = 250

KEYWORDS = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum", "eth", "ether"],
}
OUTPUT_DIR = "data/raw"

# --- Helper Function ---
def get_mentioned_crypto(text, keywords):
    """Checks if any crypto keywords are present in the text and returns their symbols.

    Args:
        text (str): The input text (e.g., a post's title and body combined).
        keywords (dict[str, list[str]]): A dictionary where keys are crypto symbols
            (e.g., "BTC") and values are lists of corresponding keywords
            (e.g., ["bitcoin", "btc"]).

    Returns:
        list[str] | None: A list of mentioned crypto symbols (e.g., ["BTC", "ETH"])
                          if found, otherwise None.
    """
    mentioned = []
    text_lower = text.lower()
    for crypto, keys in keywords.items():
        if any(key in text_lower for key in keys):
            mentioned.append(crypto)
    return mentioned if mentioned else None

# --- Main Function ---
def fetch_and_save_reddit_data(subreddits, keywords, limit, output_dir):
    """Scrapes posts from subreddits, tags them, and saves them to a Parquet file.

    This function authenticates with the Reddit API using credentials stored in a
    `.env` file in the project's root directory. The required variables are:
    - REDDIT_CLIENT_ID
    - REDDIT_CLIENT_SECRET
    - REDDIT_USER_AGENT
    - REDDIT_USERNAME
    - REDDIT_PASSWORD

    Args:
        subreddits (list[str]): A list of subreddit names to scrape, without the
                                "r/" prefix.
        keywords (dict[str, list[str]]): A dictionary for mapping keywords to
                                         cryptocurrency symbols.
        limit (int | None): The maximum number of new posts to fetch from each
                            subreddit. Use None for the PRAW default limit (~1000).
        output_dir (str): The relative path to the directory where the output
                          Parquet file will be saved.

    Returns:
        None: This function does not return a value. Its side effect is creating a
              file named `raw_reddit_data.parquet` in the output directory.
    """
    # Load environment variables from the .env file in the project root
    load_dotenv()
    print("--- Starting Reddit Data Scrape ---")

    # Authenticate with Reddit using environment variables
    try:
        reddit = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            user_agent=os.environ["REDDIT_USER_AGENT"],
            username=os.environ["REDDIT_USERNAME"],
            password=os.environ["REDDIT_PASSWORD"],
        )
        print("Successfully authenticated with Reddit API.")
    except KeyError as e:
        print(f"ERROR: Missing environment variable: {e}. "
              "Please ensure your .env file is correctly set up.")
        return

    all_posts = []

    for sub_name in subreddits:
        print(f"\nFetching posts from r/{sub_name}...")
        subreddit = reddit.subreddit(sub_name)
        
        post_count = 0
        try:
            # Fetch the newest posts. For deep historical data, other tools are needed.
            for post in subreddit.new(limit=limit):
                combined_text = post.title + " " + post.selftext
                mentioned_cryptos = get_mentioned_crypto(combined_text, keywords)
                
                if mentioned_cryptos:
                    all_posts.append({
                        "post_id": post.id,
                        "timestamp_utc": datetime.utcfromtimestamp(post.created_utc),
                        "subreddit": sub_name,
                        "title": post.title,
                        "body": post.selftext,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "mentioned_crypto": mentioned_cryptos,
                    })
                    post_count += 1
        except Exception as e:
            print(f"An error occurred while fetching from r/{sub_name}: {e}")
            continue # Move to the next subreddit

        print(f"Found and saved {post_count} relevant posts from r/{sub_name}.")

    if not all_posts:
        print("\nWARNING: No relevant posts were found across all subreddits. "
              "The output file will not be created.")
        return

    # --- Save Data to Parquet ---
    print("\nConverting collected data to DataFrame...")
    df = pd.DataFrame(all_posts)
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "raw_reddit_data.parquet")
    df.to_parquet(filepath)

    print(f"Successfully saved {len(df)} total posts to '{filepath}'")
    print("--- Reddit Data Scrape Complete ---")

# --- Script Execution ---
if __name__ == "__main__":
    fetch_and_save_reddit_data(
        subreddits=SUBREDDITS,
        keywords=KEYWORDS,
        limit=POST_LIMIT,
        output_dir=OUTPUT_DIR,
    )