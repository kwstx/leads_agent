from typing import List
from ..schema.lead_schema import Lead

class LeadEnricher:
    def enrich(self, leads: List[Lead]) -> List[Lead]:
        # Mocking enrichment with public profile links as contact info
        for lead in leads:
            if not lead.contact_info:
                lead.contact_info = f"https://{lead.platform.lower()}.com/{lead.username}"
        return leads
