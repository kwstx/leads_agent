import os
import json
import pandas as pd
from typing import Dict, Any, List
from openai import OpenAI
from src.utils.config import Config
from dotenv import load_dotenv

load_dotenv()

class LeadEnricher:
    def __init__(self, model: str = None, base_url: str = None, api_key: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY or "not-needed"
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def _get_prompt(self, content: str) -> str:
        return f"""You are an expert at identifying high-value leads for an AI agent communication platform.
Analyze the following content and determine if the author is building AI agents and if they are experiencing technical challenges relevant to agent-to-agent communication or integration.

Content:
---
{content}
---

Specifically, check if they are building or deploying AI agents.
Then, identify if they are facing problems such as:
- Communication failures between agents or systems.
- Schema mismatches or data structure issues.
- Integration issues with third-party tools or other agents.
- Reliability, discovery, or orchestration challenges in multi-agent systems.

Return a JSON object with the following fields:
1. "is_relevant": (boolean) True if they are building AI agents AND experiencing relevant problems.
2. "problem_description": (string) A short, concise description of the specific technical problem they are facing. If "is_relevant" is False, this can be "N/A".
3. "intent_score": (integer, 1-10) A score from 1 to 10 based on how urgently they seem to need a solution for agent communication/integration. 10 is highest.

Response must be valid JSON only."""

    def enrich_row(self, content: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a lead enrichment assistant. You outputs structured JSON data."},
                    {"role": "user", "content": self._get_prompt(content)}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error enriching content: {e}")
            return {
                "is_relevant": False,
                "problem_description": f"Error: {str(e)}",
                "intent_score": 1
            }

def enrich_data(input_csv: str, output_csv: str):
    if not os.path.exists(input_csv):
        print(f"Input file {input_csv} not found.")
        return

    df = pd.read_csv(input_csv)
    enricher = LeadEnricher()
    
    print(f"Enriching {len(df)} rows from {input_csv}...")
    
    enriched_results = []
    for index, row in df.iterrows():
        content = str(row.get('content', ''))
        print(f"Processing row {index + 1}/{len(df)}...")
        result = enricher.enrich_row(content)
        enriched_results.append(result)

    # Extract fields from results
    df['is_relevant'] = [r.get('is_relevant', False) for r in enriched_results]
    df['problem_description'] = [r.get('problem_description', 'N/A') for r in enriched_results]
    df['intent_score'] = [r.get('intent_score', 1) for r in enriched_results]

    df.to_csv(output_csv, index=False)
    print(f"Successfully enriched data. Results saved to {output_csv}")

if __name__ == "__main__":
    enrich_data("cleaned_data.csv", "enriched_data.csv")
