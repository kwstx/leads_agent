import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def github_search(keywords, limit=25):
    """
    Search GitHub for specific keywords in issues and pull requests.
    """
    api_key = os.getenv("GITHUB_API_KEY")
    if not api_key:
        print("Warning: GITHUB_API_KEY not found in environment. Using unauthenticated requests (rate limited).")
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if api_key:
        headers["Authorization"] = f"token {api_key}"
    
    all_data = []

    for keyword in keywords:
        print(f"Searching GitHub for: '{keyword}'...")
        # GitHub search issues endpoint
        # The query 'q' can include the keyword and type:issue
        url = "https://api.github.com/search/issues"
        params = {
            "q": f"{keyword} type:issue",
            "per_page": limit,
            "sort": "created",
            "order": "desc"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 401:
                print("Error: Unauthorized. Please check your GITHUB_API_KEY.")
                break
            elif response.status_code == 403:
                print("Error: Forbidden (Rate Limit reached?).")
                continue
            elif response.status_code != 200:
                print(f"Error fetching data from GitHub: {response.status_code}")
                continue
                
            data = response.json()
            items = data.get("items", [])
            
            for item in items:
                # Extract repository name from repository_url: https://api.github.com/repos/owner/repo
                # A more reliable way is to extract owner/repo from the repository_url
                repo_url_parts = item["repository_url"].split("/")
                repo_name = f"{repo_url_parts[-2]}/{repo_url_parts[-1]}"
                
                # Extract labels as a comma-separated string
                labels = ", ".join([label["name"] for label in item["labels"]])
                
                # Normalize to Reddit schema: username,post_title,post_body,subreddit_name,timestamp,url
                # We also add 'labels' as specifically requested
                issue_data = {
                    "username": item["user"]["login"],
                    "post_title": item["title"],
                    "post_body": item["body"] if item["body"] else "",
                    "subreddit_name": repo_name, # Mapping repository name to subreddit_name
                    "timestamp": item["created_at"],
                    "url": item["html_url"],
                    "labels": labels
                }
                all_data.append(issue_data)
        except Exception as e:
            print(f"Exception during request for '{keyword}': {e}")

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Drop duplicates by URL if an issue matches multiple keywords
    if not df.empty:
        df = df.drop_duplicates(subset=["url"])
    
    return df

if __name__ == "__main__":
    # Define keywords as requested
    search_keywords = [
        "multi-agent",
        "agent communication",
        "LangChain error",
        "integration issue"
    ]

    print("--- Starting GitHub Scraper ---")
    try:
        results_df = github_search(search_keywords)
        
        if not results_df.empty:
            # Save to CSV
            output_file = "github_raw.csv"
            
            # Ensure the order of columns matches the normalization requirement
            # and includes the requested labels
            columns_order = ["username", "post_title", "post_body", "subreddit_name", "timestamp", "url", "labels"]
            results_df = results_df[columns_order]
            
            results_df.to_csv(output_file, index=False)
            
            print(f"Successfully scraped {len(results_df)} GitHub issues.")
            print(f"Results saved to {output_file}")
        else:
            print("No issues found for the given keywords.")
            
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    print("--- GitHub Scraper Completed ---")
