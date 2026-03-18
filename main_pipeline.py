import os
import sys
import pandas as pd
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

# Import components from the src package
try:
    from src.collectors.github_collector import GithubCollector
    from src.collectors.reddit_collector import RedditCollector
    from src.collectors.dev_collector import DevCollector
    from src.collectors.medium_collector import MediumCollector
    from src.collectors.hn_collector import HackerNewsCollector
    from src.collectors.qiita_collector import QiitaCollector
    from src.collectors.csdn_collector import CSDNCollector
    from src.collectors.juejin_collector import JuejinCollector
    
    from src.processors.data_processor import LeadProcessor
    from src.processors.categorizer import LeadCategorizer
    from src.processors.llm_enricher import LeadEnricher as LLMEnricher
    from src.enrichers.lead_enricher import LeadEnricher as ProfileEnricher
    from src.enrichers.contact_finder import HunterEnricher
    from src.scorers.intent_scorer import IntentScorer
    from src.processors.outreach_generator import OutreachGenerator
    from src.output.csv_exporter import CSVExporter
    from src.utils.logger import setup_logger
    from upload_to_sheets import upload_leads
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Configuration
MASTER_LEADS_DIR = "data/final"
MASTER_LEADS_PATH = os.path.join(MASTER_LEADS_DIR, "final_leads_master.csv")
LOG_FILENAME = f"pipeline_run.log" # Overwrite same log for recent run or use date?

# Initialize Logger
logger = setup_logger("MainPipeline", log_file=LOG_FILENAME)

def main_pipeline():
    logger.info("==========================================")
    logger.info(f"Starting Engram Lead Pipeline Run: {datetime.now().isoformat()}")
    logger.info("==========================================")
    
    load_dotenv()
    
    try:
        # Phase 1: Data Collection
        logger.info("Phase 1: Collection from multiple platforms")
        query = os.getenv("SEARCH_QUERY", "agentic-ai tool issues")
        collectors = [
            GithubCollector(query=query),
            RedditCollector(),
            DevCollector(tags=["ai", "agents", "automation"]),
            MediumCollector(tags=["ai", "agents", "langchain"]),
            HackerNewsCollector(query=query),
            QiitaCollector(query="エージェント AI"),
            CSDNCollector(query="智能体 AI"),
            JuejinCollector(query="智能体 AI")
        ]
        
        all_raw_leads = []
        for collector in collectors:
            try:
                logger.info(f"Running collector: {collector.__class__.__name__}...")
                leads = collector.collect()
                if leads:
                    all_raw_leads.extend(leads)
                    logger.info(f"Successfully collected {len(leads)} leads from {collector.__class__.__name__}")
                else:
                    logger.info(f"No leads found from {collector.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to collect from {collector.__class__.__name__}: {str(e)}")

        if not all_raw_leads:
            logger.warning("No leads found across all collectors. Pipeline ending.")
            return

        # Phase 2: Deduplication against Master File
        logger.info("Phase 2: Deduplicating and checking for existing leads")
        processor = LeadProcessor()
        # Initial cleanup (e.g., internal duplicates within a run)
        processed_leads = processor.process(all_raw_leads)
        
        existing_sources = set()
        if os.path.exists(MASTER_LEADS_PATH):
            try:
                master_df = pd.read_csv(MASTER_LEADS_PATH)
                # Check different possible URL column names used over time
                for col in ['url', 'source_link', 'Link']:
                    if col in master_df.columns:
                        existing_sources.update(master_df[col].dropna().astype(str).tolist())
                logger.info(f"Loaded {len(existing_sources)} existing lead sources from {MASTER_LEADS_PATH}")
            except Exception as e:
                logger.error(f"Error reading master file: {e}. Starting fresh.")
        
        # Filter for truly NEW leads
        new_leads = [l for l in processed_leads if l.source_link not in existing_sources]
        logger.info(f"Filtered {len(processed_leads) - len(new_leads)} duplicates. {len(new_leads)} leads are NEW.")
        
        if not new_leads:
            logger.info("No fresh leads to process today. Exiting.")
            return

        # Phase 3: Categorization & LLM Enrichment
        logger.info("Phase 3: Categorization & LLM Enrichment (Filtering Relevance)")
        categorizer = LeadCategorizer()
        new_leads = categorizer.categorize(new_leads)
        
        # Identify high-value leads with LLM
        # This checks if they are BUILDING agents and have a PROBLEM.
        llm_enricher = LLMEnricher()
        qualified_new_leads = []
        
        for idx, lead in enumerate(new_leads):
            logger.info(f"[{idx+1}/{len(new_leads)}] Enriching: {lead.source_link}")
            try:
                enrichment = llm_enricher.enrich_row(lead.content)
                lead.is_relevant = enrichment.get('is_relevant', False)
                lead.problem = enrichment.get('problem_description', 'N/A')
                # Optional: use LLM's intent score too
                llm_intent = enrichment.get('intent_score', 1) / 10.0
                lead.intent_score = max(lead.intent_score, llm_intent)
                
                if lead.is_relevant:
                    qualified_new_leads.append(lead)
                else:
                    logger.info(f"Lead not relevant: {lead.username} ({lead.source_link})")
            except Exception as e:
                logger.error(f"Error enriching lead {lead.username}: {e}")
                # Keep it as is or skip? Let's treat it as potentially not relevant
                lead.is_relevant = False
        
        logger.info(f"Qualified {len(qualified_new_leads)} relevant prospects out of {len(new_leads)} new leads.")
        
        if not qualified_new_leads:
            logger.info("No relevant leads found in this batch after LLM enrichment.")
            return

        # Phase 4: Profile Enrichment & Scoring
        logger.info("Phase 4: Profile Enrichment, Contact Finding & Scoring")
        profile_enricher = ProfileEnricher()
        contact_finder = HunterEnricher()
        scorer = IntentScorer()
        
        qualified_new_leads = profile_enricher.enrich(qualified_new_leads)
        qualified_new_leads = contact_finder.enrich(qualified_new_leads)
        qualified_new_leads = scorer.score(qualified_new_leads)
        
        # Phase 5: Personalized Outreach Generation
        logger.info("Phase 5: Generating personalized outreach messages")
        outreach_generator = OutreachGenerator()
        qualified_new_leads = outreach_generator.process_leads(qualified_new_leads)
        
        # Phase 6: Merging with Master File
        logger.info("Phase 6: Syncing with Master Database")
        new_df = pd.DataFrame([l.to_dict() for l in qualified_new_leads])
        
        # Ensure we don't have schema mismatches between CSV and model
        if os.path.exists(MASTER_LEADS_PATH):
            master_df = pd.read_csv(MASTER_LEADS_PATH)
            # Standardize columns to match current Lead model if columns differ slightly
            updated_master_df = pd.concat([master_df, new_df], ignore_index=True)
            # Final dedupe check (URL is best primary key)
            if 'source_link' in updated_master_df.columns:
                updated_master_df = updated_master_df.drop_duplicates(subset=['source_link'], keep='last')
            elif 'url' in updated_master_df.columns:
                 updated_master_df = updated_master_df.drop_duplicates(subset=['url'], keep='last')
        else:
            updated_master_df = new_df
            
        # Save updated master
        os.makedirs(MASTER_LEADS_DIR, exist_ok=True)
        updated_master_df.to_csv(MASTER_LEADS_PATH, index=False)
        logger.info(f"Master file updated: {len(updated_master_df)} total records ({len(qualified_new_leads)} added).")

        # Phase 7: Output to Social Channels / Sheets
        logger.info("Phase 7: Exporting to Google Sheets")
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        try:
            upload_leads(MASTER_LEADS_PATH, spreadsheet_id)
            logger.info("Successfully updated Google Sheets!")
        except Exception as e:
            logger.error(f"Failed to upload to Sheets: {e}")

        logger.info("Pipeline completed successfully.")

    except Exception as e:
        logger.critical(f"Pipeline crashed with unhandled exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main_pipeline()
