import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config

class JuejinCollector(BaseCollector):
    def __init__(self, query: str = "智能体 AI / " + "agentic ai"):
        super().__init__()
        self.query = query

    def collect(self) -> List[Lead]:
        leads = []
        # Juejin search API endpoint
        url = "https://api.juejin.cn/search_api/v1/search"
        payload = {
            "key_word": self.query,
            "id_type": 0,
            "cursor": "0",
            "limit": 20,
            "search_type": 0
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", [])
                for item in items:
                    article_info = item.get("result_model", {}).get("article_info", {})
                    author_info = item.get("result_model", {}).get("author_user_info", {})
                    leads.append(Lead(
                        username=author_info.get("user_name") or "juejin_user",
                        platform="Juejin",
                        content=article_info.get("brief_content") or article_info.get("title"),
                        problem=article_info.get("title"),
                        source_link=f"https://juejin.cn/post/{article_info.get('article_id')}",
                        tags=article_info.get("tags", [])
                    ))
            else:
                print(f"Juejin Search Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception in JuejinCollector: {e}")
            
        return leads
