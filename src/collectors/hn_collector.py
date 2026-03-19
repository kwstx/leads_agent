import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.multilingual_keywords import get_keywords_by_lang, KEYWORDS

class HackerNewsCollector(BaseCollector):
    def __init__(self, languages: List[str] = None):
        super().__init__()
        self.languages = languages or list(KEYWORDS.keys())
        self.api_url = "https://hn.algolia.com/api/v1/search"

    def collect(self) -> List[Lead]:
        leads = []
        
        all_keywords = []
        for lang in self.languages:
            all_keywords.extend(get_keywords_by_lang(lang))
            
        for keyword in all_keywords:
            try:
                # Search for stories
                params = {
                    "query": keyword,
                    "tags": "story",
                    "hitsPerPage": 20
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
                        
                        leads.append(Lead(
                            username=author or "Anonymous",
                            platform="Hacker News",
                            content=title,
                            problem=title,
                            source_link=url,
                            tags=hit.get("_tags", []) + [keyword]
                        ))
                
                # Search for comments
                params_comments = {
                    "query": keyword,
                    "tags": "comment",
                    "hitsPerPage": 20
                }
                response_comments = requests.get(self.api_url, params=params_comments, timeout=10)
                if response_comments.status_code == 200:
                    data_comments = response_comments.json()
                    for hit in data_comments.get("hits", []):
                        author = hit.get("author")
                        comment_text = hit.get("comment_text", "")
                        from bs4 import BeautifulSoup
                        clean_text = BeautifulSoup(comment_text, "html.parser").get_text()
                        
                        parent_id = hit.get("story_id")
                        url = f"https://news.ycombinator.com/item?id={parent_id}#{hit['objectID']}"
                        
                        leads.append(Lead(
                            username=author or "Anonymous",
                            platform="Hacker News",
                            content=clean_text[:500],
                            problem=hit.get("story_title", "Comment on HN"),
                            source_link=url,
                            tags=["comment"] + hit.get("_tags", []) + [keyword]
                        ))
                        
            except Exception as e:
                print(f"Error collecting from Hacker News for keyword '{keyword}': {e}")
            
        # Deduplicate
        unique_leads = {lead.source_link: lead for lead in leads}.values()
        return list(unique_leads)
