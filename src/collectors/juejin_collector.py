import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config
from src.utils.multilingual_keywords import get_keywords_by_lang

class JuejinCollector(BaseCollector):
    def __init__(self, languages: List[str] = ["zh", "en"]):
        super().__init__()
        self.languages = languages

    def collect(self) -> List[Lead]:
        leads = []
        url = "https://api.juejin.cn/search_api/v1/search"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json"
        }

        all_keywords = []
        for lang in self.languages:
            all_keywords.extend(get_keywords_by_lang(lang))
        
        for keyword in all_keywords:
            payload = {
                "key_word": keyword,
                "id_type": 0,
                "cursor": "0",
                "limit": 10,
                "search_type": 0
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("data", [])
                    for item in items:
                        article_info = item.get("result_model", {}).get("article_info", {})
                        author_info = item.get("result_model", {}).get("author_user_info", {})
                        if article_info:
                            leads.append(Lead(
                                username=author_info.get("user_name") or "juejin_user",
                                platform="Juejin",
                                content=article_info.get("brief_content") or article_info.get("title"),
                                problem=article_info.get("title"),
                                source_link=f"https://juejin.cn/post/{article_info.get('article_id')}",
                                tags=[keyword] + ([tag["tag_name"] for tag in article_info.get("tags", [])] if isinstance(article_info.get("tags"), list) else [])
                            ))
                else:
                    print(f"Juejin Search Error for '{keyword}': {response.status_code}")
            except Exception as e:
                print(f"Exception in JuejinCollector for '{keyword}': {e}")
            
        # Deduplicate
        unique_leads = {lead.source_link: lead for lead in leads}.values()
        return list(unique_leads)
