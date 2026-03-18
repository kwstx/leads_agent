import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector

class HackerNewsCollector(BaseCollector):
    def __init__(self, query: str = "agentic OR \"multi-agent\" OR \"LangChain\""):
        super().__init__()
        self.query = query
        self.api_url = "https://hn.algolia.com/api/v1/search"

    def collect(self) -> List[Lead]:
        leads = []
        try:
            # Algolia API for Hacker News
            params = {
                "query": self.query,
                "tags": "story", # We want stories (posts)
                "hitsPerPage": 50
            }
            response = requests.get(self.api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for hit in data.get("hits", []):
                    title = hit.get("title")
                    author = hit.get("author")
                    url = hit.get("url")
                    if not url:
                        url = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                    
                    snippet = hit.get("_highlightResult", {}).get("title", {}).get("value", "")
                    # Clean highlight tags from snippet if needed, but the original title is better for 'problem'
                    
                    leads.append(Lead(
                        username=author or "Anonymous",
                        platform="Hacker News",
                        content=title,
                        problem=title,
                        source_link=url or f"https://news.ycombinator.com/item?id={hit['objectID']}",
                        tags=hit.get("_tags", []) # Includes 'story', 'author_name', etc.
                    ))
            
            # Also search for comments to get more 'problem' signals
            params_comments = {
                "query": self.query,
                "tags": "comment",
                "hitsPerPage": 50
            }
            response_comments = requests.get(self.api_url, params=params_comments, timeout=10)
            if response_comments.status_code == 200:
                data_comments = response_comments.json()
                for hit in data_comments.get("hits", []):
                    author = hit.get("author")
                    comment_text = hit.get("comment_text", "")
                    # Clean HTML from comment text if necessary
                    from bs4 import BeautifulSoup
                    clean_text = BeautifulSoup(comment_text, "html.parser").get_text()
                    
                    parent_id = hit.get("story_id")
                    url = f"https://news.ycombinator.com/item?id={parent_id}#{hit['objectID']}"
                    
                    leads.append(Lead(
                        username=author or "Anonymous",
                        platform="Hacker News",
                        content=clean_text[:500], # Keep snippet
                        problem=hit.get("story_title", "Comment on HN"),
                        source_link=url,
                        tags=["comment"] + hit.get("_tags", [])
                    ))
                    
        except Exception as e:
            print(f"Error collecting from Hacker News: {e}")
            
        return leads
