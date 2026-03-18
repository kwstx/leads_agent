import pandas as pd
import os
from typing import List
from ..schema.lead_schema import Lead

class CSVExporter:
    def export(self, leads: List[Lead], filename: str):
        filepath = os.path.join("data", filename)
        df = pd.DataFrame([lead.to_dict() for lead in leads])
        df.to_csv(filepath, index=False)
        print(f"Exported {len(leads)} leads to {filepath}")
