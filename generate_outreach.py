import pandas as pd
import os
import logging
import sys
from dotenv import load_dotenv

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.processors.outreach_generator import OutreachGenerator
from src.schema.lead_schema import Lead
from src.utils.logger import setup_logger

load_dotenv()

# Configuration
MASTER_LEADS_PATH = "data/final/final_leads_master.csv"
OUTPUT_FILE = "data/final/final_leads_with_messages.csv"

# Initialize Logger
logger = setup_logger("OutreachScript", log_file="outreach_run.log")

def run_outreach_generation():
    if not os.path.exists(MASTER_LEADS_PATH):
        logger.error(f"Master file not found at {MASTER_LEADS_PATH}")
        return

    logger.info(f"Loading leads from {MASTER_LEADS_PATH}...")
    df = pd.read_csv(MASTER_LEADS_PATH)
    
    # Ensure mandatory fields for Lead model exist
    # For now, let's just make sure we handle the data we have.
    # Our lead model: username, platform, content, problem, is_relevant, intent_score, contact_info, source_link, tags, outreach_message

    leads = []
    for _, row in df.iterrows():
        try:
            # Handle tags (might be string in CSV)
            tags = row.get('tags', '[]')
            if isinstance(tags, str):
                try:
                    import ast
                    tags_list = ast.literal_eval(tags)
                except:
                    tags_list = [t.strip() for t in tags.strip('[]').split(',') if t.strip()]
            else:
                tags_list = []

            lead = Lead(
                username=str(row.get('username', 'anonymous')),
                platform=str(row.get('platform', 'unknown')),
                content=str(row.get('content', '')),
                problem=str(row.get('problem', 'N/A')),
                is_relevant=bool(row.get('is_relevant', True)),
                intent_score=float(row.get('intent_score', 0.0)),
                contact_info=str(row.get('contact_info', '')) if pd.notna(row.get('contact_info')) else None,
                source_link=str(row.get('source_link', '')),
                tags=tags_list,
                outreach_message=str(row.get('outreach_message', '')) if pd.notna(row.get('outreach_message')) else None
            )
            leads.append(lead)
        except Exception as e:
            logger.error(f"Error parsing row: {e}")
            continue

    logger.info(f"Loaded {len(leads)} leads. Starting generation...")
    
    # Filter for relevant leads that don't have a message yet?
    # Or just run for the first few to demonstrate.
    # Given the file size (11k rows), we should probably limit for testing or run on relevant ones.
    
    relevant_leads = [l for l in leads if l.is_relevant]
    logger.info(f"Filtered to {len(relevant_leads)} relevant leads.")
    
    # Let's take the top 10 for demonstration and safety (since I don't know the budget)
    # But usually, I should be able to run it.
    # I'll run on top 5 if there's no limit specified.
    
    demo_limit = 5
    if len(relevant_leads) > demo_limit:
        logger.warning(f"Limiting to first {demo_limit} relevant leads for demo purposes.")
        to_process = relevant_leads[:demo_limit]
    else:
        to_process = relevant_leads

    generator = OutreachGenerator()
    processed_leads = generator.process_leads(to_process)
    
    # Update the messages in the dataframe
    for lead in processed_leads:
        df.loc[df['source_link'] == lead.source_link, 'outreach_message'] = lead.outreach_message

    # Save the updated file
    df.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"Successfully saved updated leads with outreach messages to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_outreach_generation()
