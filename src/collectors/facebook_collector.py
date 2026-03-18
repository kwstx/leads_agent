import os
import csv
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config

class FacebookCollector(BaseCollector):
    """
    Placeholder for Facebook Group ingestion.
    Accepts manually exported CSV data.
    """
    def __init__(self, export_path: str = "data/manual/facebook_export.csv"):
        super().__init__()
        self.export_path = export_path

    def collect(self) -> List[Lead]:
        leads = []
        if not os.path.exists(self.export_path):
            print(f"Facebook export file not found at {self.export_path}. Skipping.")
            return leads
            
        try:
            with open(self.export_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    leads.append(Lead(
                        username=row.get("author") or "fb_user",
                        platform="Facebook",
                        content=row.get("message") or "",
                        problem="Manual Facebook Ingestion",
                        source_link=row.get("link") or "https://facebook.com",
                        tags=["facebook-import"]
                    ))
        except Exception as e:
            print(f"Exception in FacebookCollector: {e}")
            
        return leads
