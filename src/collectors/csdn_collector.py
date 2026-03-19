import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config
from src.utils.multilingual_keywords import get_keywords_by_lang

class CSDNCollector(BaseCollector):
    def __init__(self, languages: List[str] = ["zh", "en"]):
        super().__init__()
        self.languages = languages

    def collect(self) -> List[Lead]:
        leads = []
        url = "https://so.csdn.net/api/v3/search"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        all_keywords = []
        for lang in self.languages:
            all_keywords.extend(get_keywords_by_lang(lang))
        
        for keyword in all_keywords:
            params = {
                "q": keyword,
                "t": "all",
                "p": 1,
                "s": 0,
                "tm": 0,
                "lv": -1,
                "ft": 0,
                "l": "",
                "u": "",
                "f": ""
            }
            
            try:
                response = requests.get(url, params=params, headers=headers)
                # Handle encoding explicitly for Chinese content
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("result_vos", [])
                    for item in items:
                        leads.append(Lead(
                            username=item.get("nickname") or "csdn_user",
                            platform="CSDN",
                            content=item.get("description") or item.get("title"),
                            problem=item.get("title"),
                            source_link=item.get("url"),
                            tags=[tag for tag in item.get("tag", "").split(",") if tag] + [keyword]
                        ))
                else:
                    print(f"CSDN Search Error for '{keyword}': {response.status_code}")
            except Exception as e:
                print(f"Exception in CSDNCollector for '{keyword}': {e}")
            
        # Deduplicate
        unique_leads = {lead.source_link: lead for lead in leads}.values()
        return list(unique_leads)
