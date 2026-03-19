import requests
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config
from src.utils.multilingual_keywords import get_combined_query, KEYWORDS

class GithubCollector(BaseCollector):
    def __init__(self, languages: List[str] = None):
        super().__init__()
        self.languages = languages or list(KEYWORDS.keys())
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
        
        all_leads = []
        headers = {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
        url = "https://api.github.com/search/issues"
        
        for lang in self.languages:
            keywords = KEYWORDS.get(lang, KEYWORDS["en"])
            for kw in keywords:
                # Wrap multi-word keywords in quotes for better search accuracy
                query_term = f'"{kw}"' if " " in kw else kw
                params = {
                    "q": f"{query_term} type:issue",
                    "per_page": 10,  # Smaller limit per keyword to keep it fast
                    "sort": "created",
                    "order": "desc"
                }
                
                try:
                    response = requests.get(url, headers=headers, params=params)
                    # Ensure we handle encoding correctly
                    response.encoding = 'utf-8'
                    
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get("items", []):
                            # Extract repository name (owner/repo)
                            repo_url_parts = item["repository_url"].split("/")
                            repo_name = f"{repo_url_parts[-2]}/{repo_url_parts[-1]}"
                            
                            # Extract labels
                            labels = [label["name"] for label in item["labels"]]
                            
                            all_leads.append(Lead(
                                username=item["user"]["login"],
                                platform="GitHub",
                                content=item["body"] or item["title"],
                                problem=item["title"],
                                source_link=item["html_url"],
                                tags=[repo_name, lang] + labels
                            ))
                    elif response.status_code == 403:
                        # Rate limit hit, skip this keyword or log it
                        print(f"GitHub Rate Limit hit for {lang}/{kw}. Skipping...")
                        continue
                    else:
                        print(f"GitHub API Error for {lang}/{kw}: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"Exception in GithubCollector for {lang}/{kw}: {e}")
                
        # Deduplicate results by source_link
        unique_leads = {lead.source_link: lead for lead in all_leads}.values()
        return list(unique_leads)
