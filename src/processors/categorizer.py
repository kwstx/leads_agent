from typing import List
from ..schema.lead_schema import Lead

class LeadCategorizer:
    def __init__(self):
        self.categories = {
            "AI/ML": ["ai", "machine learning", "neural network", "transformer", "llm", "agent"],
            "DevOps": ["docker", "kubernetes", "deployment", "github actions", "pipeline"],
            "Frontend": ["react", "vue", "typescript", "ui", "ux", "browser"],
            "Security": ["auth", "identity", "security", "token", "password", "hack"]
        }

    def categorize(self, leads: List[Lead]) -> List[Lead]:
        for lead in leads:
            content_lower = f"{lead.content} {lead.problem}".lower()
            for category, keywords in self.categories.items():
                if any(keyword in content_lower for keyword in keywords):
                    if category not in lead.tags:
                        lead.tags.append(category)
        return leads
