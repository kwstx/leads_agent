import pandas as pd
import os
from typing import List
from ..schema.lead_schema import Lead

class CSVExporter:
    def export(self, leads: List[Lead], filename: str, append: bool = False):
        filepath = os.path.join("data", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df = pd.DataFrame([lead.to_dict() for lead in leads])
        
        mode = 'a' if append and os.path.exists(filepath) else 'w'
        header = not (append and os.path.exists(filepath))
        
        df.to_csv(filepath, index=False, mode=mode, header=header, encoding='utf-8-sig')
        print(f"Exported {len(leads)} leads to {filepath} (mode: {'append' if mode == 'a' else 'overwrite'})")
