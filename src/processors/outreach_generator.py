import os
import json
import logging
from typing import List
from openai import OpenAI
from src.schema.lead_schema import Lead
from src.utils.config import Config
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("MessageGenerator")

class OutreachGenerator:
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY or "not-needed"
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def _get_system_prompt(self) -> str:
        return """You are a highly effective, empathetic growth marketing expert at Engram.
Engram is an AI agent communication middleware platform.
Key capabilities:
- Provides a standard for AI-to-AI (A2A) communication.
- Supports Model Context Protocol (MCP) and other agent communication standards.
- Solves: Brittle agent integrations, schema mismatches, synchronization issues, discovery, and orchestration in multi-agent systems.
- Value prop: Makes multi-agent stacks reliable, scalable, and easy to build by providing a unified communication layer.

Your goal is to write a SHORT (max 2-3 sentences), highly personalized message to a lead.
You must use the provided "problem" (the issue they mentioned) and "user context" (the original post/content) to show you understand their specific pain point.
Explain clearly how Engram solves that EXACT problem.
Tone: Professional, helpful, concise, and technical (engineering-focused).
Do not use generic outreach filler ("Hope you are well", "I represents..."). Get straight to the value.
Response format: Only the message text, no quotes or metadata."""

    def generate_message(self, lead: Lead) -> str:
        try:
            prompt = f"""User Context: {lead.content}
Problem Description: {lead.problem}
Platform: {lead.platform}

Write a personalized message for {lead.username}:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            message = response.choices[0].message.content.strip()
            # Clean up if the model includes quotes
            if message.startswith('"') and message.endswith('"'):
                message = message[1:-1]
            return message
            
        except Exception as e:
            logger.error(f"Error generating message for {lead.username}: {e}")
            return f"Hi {lead.username}, I saw you're working with {lead.tags[0] if lead.tags else 'AI agents'} and having issues with {lead.problem}. Engram's communication middleware could help bridge that gap."

    def process_leads(self, leads: List[Lead]) -> List[Lead]:
        logger.info(f"Generating outreach messages for {len(leads)} leads...")
        for i, lead in enumerate(leads):
            if lead.is_relevant:
                logger.info(f"[{i+1}/{len(leads)}] Generating message for {lead.username}...")
                lead.outreach_message = self.generate_message(lead)
            else:
                lead.outreach_message = None
        return leads
