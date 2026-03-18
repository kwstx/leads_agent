import os
import json
import pandas as pd
from typing import List, Dict, Any
from openai import OpenAI
from src.utils.config import Config

load_dotenv()

class LLMLeadProcessor:
    def __init__(self, model: str = None, base_url: str = None):
        self.api_key = Config.OPENAI_API_KEY or "not-needed"
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def _get_prompt(self, title: str, body: str) -> str:
        # Prompt based on user requirements: Building AI Agents/Automation and experiencing a real problem.
        # This is a robust lead detection prompt for Engram's discovery system.
        return f"""You are a Lead Discovery Assistant for Engram. 
Analyze the following post and determine if the author is building AI agents or automation systems and experiencing a real problem.

Post Title: {title}
Post Content: {body}

Criteria:
1. Building AI/Automation: High (actively coding) or Low (just brainstorming).
2. Reality of Problem: Is there a specific technical bottleneck or architectural choice they are seeking help with?

Return JSON:
{{
  "is_lead": boolean,
  "detected_problem": "brief description of the core problem found",
  "intent_score": float (0-1),
  "reasoning": "short explanation"
}}"""

    def process_row(self, row: pd.Series) -> Dict[str, Any]:
        title = row.get('post_title', '')
        body = row.get('post_body', '')
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional lead analyzer for AI automation infrastructure."},
                    {"role": "user", "content": self._get_prompt(title, body)}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "is_lead": False,
                "detected_problem": "Error: " + str(e),
                "intent_score": 0.0,
                "reasoning": "Processing failed."
            }

def process_csv_with_llm(input_csv: str, output_csv: str, model: str = None, base_url: str = None):
    processor = LLMLeadProcessor(model=model, base_url=base_url)
    df = pd.read_csv(input_csv)
    
    print(f"Reading {len(df)} rows from {input_csv}...")
    
    results = []
    for index, row in df.iterrows():
        print(f"Processing row {index+1}/{len(df)}...")
        result = processor.process_row(row)
        results.append(result)

    # Add new details
    df['is_lead'] = [r.get('is_lead', False) for r in results]
    df['detected_problem'] = [r.get('detected_problem', 'N/A') for r in results]
    df['intent_score'] = [r.get('intent_score', 0.0) for r in results]
    df['llm_reasoning'] = [r.get('reasoning', '') for r in results]

    # Filter to only leads
    leads_only = df[df['is_lead'] == True]
    
    leads_only.to_csv(output_csv, index=False)
    print(f"Successfully processed. Found {len(leads_only)} leads. Result saved to {output_csv}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python llm_processor.py <input_csv> <output_csv>")
    else:
        process_csv_with_llm(sys.argv[1], sys.argv[2])
