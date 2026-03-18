import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config

class CSDNCollector(BaseCollector):
    def __init__(self, query: str = "智能体 AI / " + "agentic ai"):
        super().__init__()
        self.query = query

    def collect(self) -> List[Lead]:
        leads = []
        # CSDN search API endpoint
        url = "https://so.csdn.net/api/v3/search"
        params = {
            "q": self.query,
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
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
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
                        tags=[tag for tag in item.get("tag", "").split(",") if tag]
                    ))
            else:
                print(f"CSDN Search Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception in CSDNCollector: {e}")
            
        return leads
