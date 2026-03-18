import os
import pandas as pd
import re
from bs4 import BeautifulSoup
import glob

# Configuration
INPUT_FILES = [
    "github_raw.csv",
    "reddit_raw.csv",
    "data/raw/github_leads.csv",
    "data/raw/all_leads.csv"
]
OUTPUT_FILE = "cleaned_data.csv"
MAX_CONTENT_LENGTH = 1500

def clean_text(text):
    """
    Remove HTML tags, special characters, and normalize whitespace.
    """
    if pd.isna(text) or not isinstance(text, str):
        return ""
    
    # Remove HTML tags using BeautifulSoup
    try:
        # Use lxml parser for speed and robustness
        soup = BeautifulSoup(text, "lxml")
        text = soup.get_text(separator=' ')
    except Exception:
        # Fallback to regex if BS fails
        text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove special characters but keep common punctuation
    # We'll allow a-z, A-Z, 0-9, spaces, and basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\-()\'\"@#$€%&*+=/]', ' ', text)
    
    # Collapse multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def truncate_text(text, max_len=MAX_CONTENT_LENGTH):
    """
    Truncate text to a maximum length.
    """
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text

def infer_platform_from_url(url):
    """
    Guess the platform from a URL.
    """
    if pd.isna(url) or not isinstance(url, str):
        return "Unknown"
    
    url = url.lower()
    if "github.com" in url:
        return "GitHub"
    elif "reddit.com" in url:
        return "Reddit"
    elif "dev.to" in url:
        return "DEV Community"
    elif "medium.com" in url:
        return "Medium"
    elif "hackernews" in url or "news.ycombinator.com" in url:
        return "Hacker News"
    elif "qiita.com" in url:
        return "Qiita"
    elif "csdn.net" in url:
        return "CSDN"
    elif "juejin.cn" in url:
        return "Juejin"
    elif "t.me" in url or "telegram.org" in url:
        return "Telegram"
    elif "facebook.com" in url:
        return "Facebook"
    
    return "Web"

def standardize_columns(df):
    """
    Rename columns to a standard schema and add missing ones.
    """
    # Define mapping: Original variant -> Target standard
    mapping = {
        "post_title": "title",
        "post_body": "content",
        "subreddit_name": "source",
        "source_link": "url",
        "labels": "tags"
    }
    
    df = df.rename(columns=mapping)
    
    # If content is missing but we have it elsewhere, merge
    if "content" not in df.columns:
        if "post_body" in df.columns: # Should be handled by mapping, but just in case
            df["content"] = df["post_body"]
    
    # Ensure required columns exist
    required_cols = ["username", "platform", "content", "title", "source", "timestamp", "url"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
            
    # If platform is missing, infer it
    if "platform" not in df.columns or df["platform"].eq("").all():
        df["platform"] = df["url"].apply(infer_platform_from_url)
    
    return df[required_cols]

def process_raw_files():
    """
    Main function to load, merge, clean, and save the data.
    """
    all_dfs = []
    
    # Find all CSV files in current dir and data/raw (as requested: "loads all raw CSV files")
    raw_files = glob.glob("*.csv") + glob.glob("data/raw/*.csv")
    
    # Exclude output files if they already exist
    raw_files = [f for f in raw_files if os.path.basename(f) not in [OUTPUT_FILE, "cleaned_data.csv"]]
    
    print(f"Found candidate raw files: {raw_files}")
    
    for file in raw_files:
        try:
            print(f"Loading {file}...")
            df = pd.read_csv(file)
            if df.empty:
                continue
            
            df = standardize_columns(df)
            all_dfs.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")

    if not all_dfs:
        print("No data found to process.")
        return

    # Merge all
    merged_df = pd.concat(all_dfs, ignore_index=True)
    initial_count = len(merged_df)
    print(f"Merged {initial_count} records.")

    # Remove duplicates based on content and username
    # We remove whitespace/case differences for content deduplication
    merged_df["content_clean"] = merged_df["content"].fillna("").str.strip().str.lower()
    merged_df = merged_df.drop_duplicates(subset=["username", "content_clean"], keep="first")
    merged_df = merged_df.drop(columns=["content_clean"])
    
    print(f"Removed {initial_count - len(merged_df)} duplicates.")

    # Clean text fields
    print("Cleaning text fields...")
    merged_df["title"] = merged_df["title"].apply(clean_text)
    merged_df["content"] = merged_df["content"].apply(clean_text)
    
    # Truncate content
    print(f"Truncating content to {MAX_CONTENT_LENGTH} characters...")
    merged_df["content"] = merged_df["content"].apply(lambda x: truncate_text(x, MAX_CONTENT_LENGTH))

    # Normalize platform names (already partially done in infer_platform, but let's ensure consistency)
    merged_df["platform"] = merged_df["platform"].fillna("").replace("", "Unknown")
    
    # Ensure all records include required fields (as requested: "ensure all records include required fields")
    # According to our schema: username, content, platform
    before_drop = len(merged_df)
    merged_df = merged_df.dropna(subset=["username", "content", "platform"])
    merged_df = merged_df[merged_df["username"].ne("") & merged_df["content"].ne("") & merged_df["platform"].ne("")]
    
    print(f"Dropped {before_drop - len(merged_df)} records missing required fields.")

    # Save
    merged_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(merged_df)} cleaned records to {OUTPUT_FILE}.")

if __name__ == "__main__":
    process_raw_files()
