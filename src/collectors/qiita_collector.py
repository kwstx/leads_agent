import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config
from src.utils.multilingual_keywords import get_keywords_by_lang

class QiitaCollector(BaseCollector):
    def __init__(self, languages: List[str] = ["ja", "en"]):
        super().__init__()
        self.languages = languages
        self.api_key = Config.QIITA_API_KEY

    def collect(self) -> List[Lead]:
        leads = []
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        url = "https://qiita.com/api/v2/items"
        
        all_keywords = []
        for lang in self.languages:
            all_keywords.extend(get_keywords_by_lang(lang))
            
        for keyword in all_keywords:
            params = {
                "query": keyword,
                "per_page": 10,
                "page": 1
            }
            
            try:
                response = requests.get(url, headers=headers, params=params)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    items = response.json()
                    for item in items:
                        leads.append(Lead(
                            username=item["user"]["id"],
                            platform="Qiita",
                            content=item["rendered_body"] or item["body"] or item["title"],
                            problem=item["title"],
                            source_link=item["url"],
                            tags=[tag["name"] for tag in item["tags"]] + [keyword]
                        ))
                elif response.status_code == 403:
                    print(f"Qiita API Rate Limit reached for '{keyword}'. Skipping.")
                    break # Usually affects all subsequent calls
                else:
                    print(f"Qiita API Error for '{keyword}': {response.status_code}")
            except Exception as e:
                print(f"Exception in QiitaCollector for '{keyword}': {e}")
            
        # Deduplicate
        unique_leads = {lead.source_link: lead for lead in leads}.values()
        return list(unique_leads)
