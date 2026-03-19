from typing import List
from ..schema.lead_schema import Lead

class IntentScorer:
    def __init__(self):
        # Weights for different intent signals (multilingual)
        self.intent_weights = {
            # English
            "urgent": 0.4, "how to": 0.2, "problem": 0.3, "help": 0.3, "issue": 0.1, "error": 0.1, "anyone know": 0.2, "solution": 0.4,
            # Chinese
            "紧急": 0.4, "请教": 0.2, "问题": 0.3, "帮助": 0.3, "错误": 0.1, "解决方案": 0.4, "报错": 0.1, "困惑": 0.2,
            # Spanish
            "urgente": 0.4, "como": 0.2, "problema": 0.3, "ayuda": 0.3, "error": 0.1, "solucion": 0.4, "fallo": 0.1,
            # Portuguese
            "urgente": 0.4, "ajuda": 0.3, "erro": 0.1, "solucao": 0.4, "falha": 0.1, "ajudar": 0.2,
            # Japanese
            "緊急": 0.4, "方法": 0.2, "問題": 0.3, "助けて": 0.3, "エラー": 0.1, "解決策": 0.4, "困っています": 0.3
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
