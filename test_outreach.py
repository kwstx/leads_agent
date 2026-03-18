import sys
import os
import logging
from dotenv import load_dotenv

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.schema.lead_schema import Lead
from src.processors.outreach_generator import OutreachGenerator

# Simple test case
def test_generation():
    load_dotenv()
    
    # Check if OPENAI_API_KEY is present
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not found in environment. The generator might return error messages.")

    sample_lead = Lead(
        username="test_user",
        platform="Reddit",
        content="I'm building a multi-agent system for home automation, but my agents are struggling to share state and keep their schemas in sync. It's really frustrating and point-to-point connections are breaking.",
        problem="Brittle agent-to-agent communication and schema synchronization issues.",
        source_link="https://reddit.com/r/ai_agents/test",
        tags=["AI/ML", "Automation"]
    )
    
    generator = OutreachGenerator()
    message = generator.generate_message(sample_lead)
    
    print("--- GENERATED MESSAGE ---")
    print(message)
    print("--------------------------")

if __name__ == "__main__":
    test_generation()
