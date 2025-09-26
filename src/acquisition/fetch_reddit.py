# src/acquisition/fetch_reddit_data.py

import os
import praw
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv

# --- Configuration ---
# We will get this from the central config file when run from main.py
try:
    from src import config
except ImportError:
    config = None

# --- Noise Filtering ---
# We will filter out any post whose title contains one of these phrases (case-insensitive).
NOISE_PHRASES = [
    "daily general discussion",
    "what are you building?",
    "daily discussion",
    "daily thread",
]

# --- Helper Function ---
def get_mentioned_crypto(text, keywords):
    """Checks if any crypto keywords are present in the text and returns their symbols."""
    mentioned = []
    text_lower = text.lower()
    for crypto_symbol, keys in keywords.items():
        if any(key in text_lower for key in keys):
            mentioned.append(crypto_symbol)
    return mentioned if mentioned else None

# --- Main Function ---
def fetch_and_save_reddit_data(subreddits, keywords, output_dir, post_limit_per_sub=5000):
    """
    Scrapes the newest posts from subreddits, filters them, and saves to a Parquet file.

    This is a more aggressive scraper that iterates through the newest `post_limit_per_sub`
    posts for each subreddit, filters for keywords, and removes common noise.

    Args:
        subreddits (list[str]): A list of subreddit names to scrape.
        keywords (dict[str, list[str]]): A dictionary mapping crypto symbols to keywords.
        output_dir (str): The relative path to the directory for the output file.
        post_limit_per_sub (int): The max number of new posts to fetch from each sub.
                                  This is not a guarantee, but a high number to go back in time.
    Returns:
        None: Creates a descriptively named Parquet file in the output directory.
    """
    load_dotenv()
    print("--- Starting Reddit Data Scrape (Aggressive PRAW) ---")

    try:
        reddit = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            user_agent=os.environ["REDDIT_USER_AGENT"],
            username=os.environ["REDDIT_USERNAME"],
            password=os.environ["REDDIT_PASSWORD"],
        )
        print("Successfully authenticated with Reddit API.")
    except Exception as e:
        print(f"ERROR: Could not authenticate with Reddit. Check credentials. Details: {e}")
        return

    all_posts = {} # Use a dictionary with post_id as key to prevent duplicates

    for sub_name in subreddits:
        subreddit = reddit.subreddit(sub_name)
        print(f"\nFetching up to {post_limit_per_sub} newest posts from r/{sub_name}...")
        
        posts_collected_from_sub = 0
        try:
            for post in subreddit.new(limit=post_limit_per_sub):
                # 1. Noise Filter: Skip posts with titles containing noise phrases
                title_lower = post.title.lower()
                if any(phrase in title_lower for phrase in NOISE_PHRASES):
                    continue

                # 2. Keyword Filter
                combined_text = post.title + " " + post.selftext
                mentioned_cryptos = get_mentioned_crypto(combined_text, keywords)
                
                if mentioned_cryptos:
                    # Avoid adding duplicates if a post appears in multiple queries
                    if post.id not in all_posts:
                        all_posts[post.id] = {
                            "post_id": post.id,
                            "timestamp_utc": datetime.fromtimestamp(post.created_utc, tz=timezone.utc),
                            "subreddit": sub_name,
                            "title": post.title,
                            "body": post.selftext,
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "mentioned_crypto": mentioned_cryptos,
                        }
                        posts_collected_from_sub += 1

            print(f"  Collected {posts_collected_from_sub} new, relevant posts from this sub.")
        except Exception as e:
            print(f"An error occurred while fetching from r/{sub_name}: {e}")
            continue

    if not all_posts:
        print("\nWARNING: No relevant posts were found. The output file will not be created.")
        return

    # --- Convert collected posts to DataFrame and save ---
    print(f"\nCollected a total of {len(all_posts)} unique, relevant posts.")
    df = pd.DataFrame(list(all_posts.values()))
    
    filename = f"raw_reddit_data_aggressive-praw_limit{post_limit_per_sub}.parquet"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    df.to_parquet(filepath)

    print(f"Successfully saved data to '{filepath}'")
    print("--- Reddit Data Scrape Complete ---")
