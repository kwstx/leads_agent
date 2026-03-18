import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config

class QiitaCollector(BaseCollector):
    def __init__(self, query: str = "エージェント AI"):
        super().__init__()
        self.query = query
        self.api_key = Config.QIITA_API_KEY

    def collect(self) -> List[Lead]:
        leads = []
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        url = "https://qiita.com/api/v2/items"
        params = {
            "query": self.query,
            "per_page": 20,
            "page": 1
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                items = response.json()
                for item in items:
                    leads.append(Lead(
                        username=item["user"]["id"],
                        platform="Qiita",
                        content=item["body"] or item["title"],
                        problem=item["title"],
                        source_link=item["url"],
                        tags=[tag["name"] for tag in item["tags"]]
                    ))
            elif response.status_code == 403:
                # Often occurs due to rate limit
                print(f"Qiita API Rate Limit reached (or forbidden). Skipping.")
            else:
                print(f"Qiita API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception in QiitaCollector: {e}")
            
        return leads
