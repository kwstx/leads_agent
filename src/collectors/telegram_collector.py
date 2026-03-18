import os
import json
from typing import List
from ..schema.lead_schema import Lead
from .base_collector import BaseCollector
from src.utils.config import Config

class TelegramCollector(BaseCollector):
    """
    Placeholder for Telegram ingestion.
    Can ingest from a manually exported JSON file or future API.
    """
    def __init__(self, export_path: str = "data/manual/telegram_export.json"):
        super().__init__()
        self.export_path = export_path

    def collect(self) -> List[Lead]:
        leads = []
        if not os.path.exists(self.export_path):
            print(f"Telegram export file not found at {self.export_path}. Skipping.")
            return leads
            
        try:
            with open(self.export_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Assume standard Telegram desktop export format
            messages = data.get("messages", [])
            for msg in messages:
                if msg.get("type") == "message" and msg.get("text"):
                    # Basic extraction logic
                    leads.append(Lead(
                        username=msg.get("from") or "telegram_user",
                        platform="Telegram",
                        content=str(msg.get("text")),
                        problem="Manual Telegram Ingestion",
                        source_link=f"telegram://msg/{msg.get('id')}",
                        tags=["telegram-import"]
                    ))
        except Exception as e:
            print(f"Exception in TelegramCollector: {e}")
            
        return leads
