import os
import praw
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reddit_search(keywords, limit=25):
    """
    Search Reddit for specific keywords across multiple subreddits.
    """
    # Reddit API Credentials
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "EngramLeadScraper/1.0")
    )

    all_data = []

    for keyword in keywords:
        print(f"Searching for: {keyword}")
        # Searching across 'all' subreddits for high coverage
        search_results = reddit.subreddit("all").search(keyword, limit=limit)

        for post in search_results:
            # Extract post data
            post_data = {
                "username": str(post.author) if post.author else "[deleted]",
                "post_title": post.title,
                "post_body": post.selftext,
                "subreddit_name": post.subreddit.display_name,
                "timestamp": datetime.fromtimestamp(post.created_utc).isoformat(),
                "url": post.url
            }
            all_data.append(post_data)

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Drop duplicates if a post matches multiple keywords
    df = df.drop_duplicates(subset=["url"])
    
    return df

if __name__ == "__main__":
    # Define keywords as requested
    search_keywords = [
        "AI agents",
        "multi agent",
        "LangChain problem",
        "agent communication",
        "tool integration issue"
    ]

    print("Starting Reddit scraper...")
    try:
        results_df = reddit_search(search_keywords)
        
        # Save to CSV
        output_file = "reddit_raw.csv"
        results_df.to_csv(output_file, index=False)
        
        print(f"Successfully scraped {len(results_df)} posts.")
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"An error occurred during scraping: {str(e)}")
        print("Please ensure your .env file is correctly configured with Reddit API credentials.")
