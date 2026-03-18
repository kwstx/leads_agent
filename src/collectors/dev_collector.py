import requests
from bs4 import BeautifulSoup
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector

class DevCollector(BaseCollector):
    def __init__(self, tags: List[str] = ["ai", "machinelearning", "backend"]):
        super().__init__()
        self.tags = tags
        self.base_url = "https://dev.to"

    def collect(self) -> List[Lead]:
        leads = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        for tag in self.tags:
            url = f"{self.base_url}/t/{tag}/latest"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('div', class_='crayons-story')
                
                for article in articles:
                    title_tag = article.find('h3', class_='crayons-story__title') or article.find('h2', class_='crayons-story__title')
                    if not title_tag: continue
                    
                    title = title_tag.get_text(strip=True)
                    link_tag = title_tag.find('a')
                    if not link_tag: continue
                    
                    link = link_tag['href']
                    if link.startswith('/'):
                        link = self.base_url + link
                    
                    author_tag = article.find('a', class_='crayons-story__author-name')
                    author = author_tag.get_text(strip=True) if author_tag else "Anonymous"
                    
                    snippet_tag = article.find('div', class_='crayons-story__description') or article.find('p', class_='crayons-story__snippet')
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                    
                    # Extract tags for the lead
                    article_tags = [t.get_text(strip=True) for t in article.find_all('span', class_='crayons-tag__name')]
                    
                    leads.append(Lead(
                        username=author,
                        platform="DEV Community",
                        content=snippet if snippet else title,
                        problem=title,
                        source_link=link,
                        tags=article_tags or [tag]
                    ))
            except Exception as e:
                print(f"Error collecting from DEV Community (tag: {tag}): {e}")
                
        return leads
