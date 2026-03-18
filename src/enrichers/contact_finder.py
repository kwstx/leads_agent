import requests
import os
from typing import List
from ..schema.lead_schema import Lead

class HunterEnricher:
    def __init__(self):
        self.api_key = os.getenv("HUNTER_API_KEY")

    def enrich_email(self, lead: Lead) -> Lead:
        if not self.api_key:
            # Mock enrichment
            lead.contact_info = f"{lead.username}@mock-domain.com"
            return lead
        
        # Real Hunter API call (placeholder)
        # hunter_url = f"https://api.hunter.io/v2/email-finder?full_name={lead.username}&domain=..."
        # response = requests.get(hunter_url, params={"api_key": self.api_key})
        # lead.contact_info = response.json().get("data", {}).get("email")
        
        return lead

    def enrich(self, leads: List[Lead]) -> List[Lead]:
        for lead in leads:
            self.enrich_email(lead)
        return leads
