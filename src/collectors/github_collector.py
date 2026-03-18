import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config

class GithubCollector(BaseCollector):
    def __init__(self, query: str = "help with agentic-ai"):
        super().__init__()
        self.query = query
        self.api_key = Config.GITHUB_API_KEY

    def collect(self) -> List[Lead]:
        if not self.api_key:
            # Fallback to mock data if no key is provided
            return [
                Lead(
                    username="dev_user1",
                    platform="GitHub",
                    content="Anyone know a good way to manage agent identities?",
                    problem="Identity management for AI agents",
                    source_link="https://github.com/issues/123",
                    tags=["identity", "ai-agents"]
                )
            ]
        
        # Real GitHub API call (simplified)
        headers = {"Authorization": f"token {self.api_key}"}
        url = f"https://api.github.com/search/issues?q={self.query}"
        response = requests.get(url, headers=headers)
        
        leads = []
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                leads.append(Lead(
                    username=item["user"]["login"],
                    platform="GitHub",
                    content=item["body"] or item["title"],
                    problem=item["title"],
                    source_link=item["html_url"],
                    tags=[self.query]
                ))
        return leads
