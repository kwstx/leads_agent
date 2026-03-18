import pandas as pd
from typing import List
from ..schema.lead_schema import Lead

class LeadProcessor:
    def process(self, leads: List[Lead]) -> List[Lead]:
        # Basic cleanup: remove duplicates, normalize case, etc.
        unique_leads = {}
        for lead in leads:
            unique_leads[lead.source_link] = lead # Dedup by source link
        return list(unique_leads.values())
