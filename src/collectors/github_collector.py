import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config

class GithubCollector(BaseCollector):
    def __init__(self, query: str = "multi-agent OR \"agent communication\" OR \"LangChain error\" OR \"integration issue\""):
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
        
        # Real GitHub API call
        headers = {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
        url = "https://api.github.com/search/issues"
        params = {
            "q": f"{self.query} type:issue",
            "per_page": 25,
            "sort": "created",
            "order": "desc"
        }
        
        leads = []
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    # Extract repository name (owner/repo)
                    repo_url_parts = item["repository_url"].split("/")
                    repo_name = f"{repo_url_parts[-2]}/{repo_url_parts[-1]}"
                    
                    # Extract labels
                    labels = [label["name"] for label in item["labels"]]
                    
                    leads.append(Lead(
                        username=item["user"]["login"],
                        platform="GitHub",
                        content=item["body"] or item["title"],
                        problem=item["title"],
                        source_link=item["html_url"],
                        tags=[repo_name] + labels
                    ))
            else:
                print(f"GitHub API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception in GithubCollector: {e}")
            
        return leads
