import requests
from bs4 import BeautifulSoup
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector

class MediumCollector(BaseCollector):
    # Medium allows scraping their public RSS feeds for tags
    def __init__(self, tags: List[str] = ["ai", "machine-learning", "backend-development"]):
        super().__init__()
        self.tags = tags
        self.base_url = "https://medium.com/feed/tag/"

    def collect(self) -> List[Lead]:
        leads = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        for tag in self.tags:
            url = f"{self.base_url}{tag}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                
                # Using BeautifulSoup to parse the RSS XML
                # We use regular find since XML structure is simple
                soup = BeautifulSoup(response.text, 'xml')
                items = soup.find_all('item')
                
                for item in items:
                    title_tag = item.find('title')
                    if not title_tag: continue
                    title = title_tag.get_text(strip=True)
                    
                    link_tag = item.find('link')
                    link = link_tag.get_text(strip=True) if link_tag else ""
                    
                    # Medium RSS uses <dc:creator> for author
                    author_tag = item.find('dc:creator') or item.find('creator')
                    author = author_tag.get_text(strip=True) if author_tag else "Unknown"
                    
                    # Content/Snippet
                    content_tag = item.find('content:encoded') or item.find('description')
                    content = content_tag.get_text(strip=True)[:500] if content_tag else title
                    
                    categories = [cat.get_text() for cat in item.find_all('category')]
                    
                    leads.append(Lead(
                        username=author,
                        platform="Medium",
                        content=content,
                        problem=title,
                        source_link=link,
                        tags=categories or [tag]
                    ))
            except Exception as e:
                print(f"Error collecting from Medium (tag: {tag}): {e}")
                
        return leads
