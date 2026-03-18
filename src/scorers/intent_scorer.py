from typing import List
from ..schema.lead_schema import Lead

class IntentScorer:
    def __init__(self):
        # Weights for different intent signals
        self.intent_weights = {
            "urgent": 0.4,
            "how to": 0.2,
            "problem": 0.3,
            "help": 0.3,
            "issue": 0.1,
            "error": 0.1,
            "anyone know": 0.2,
            "solution": 0.4
        }

    def score(self, leads: List[Lead]) -> List[Lead]:
        for lead in leads:
            score = 0.2 # Base baseline
            content_lower = f"{lead.content} {lead.problem}".lower()
            
            for word, weight in self.intent_weights.items():
                if word in content_lower:
                    score += weight
                    
            lead.intent_score = min(score, 1.0)
        return leads
