import argparse
import sys
from src.collectors.github_collector import GithubCollector
from src.collectors.reddit_collector import RedditCollector
from src.collectors.dev_collector import DevCollector
from src.collectors.medium_collector import MediumCollector
from src.collectors.hn_collector import HackerNewsCollector
from src.collectors.qiita_collector import QiitaCollector
from src.collectors.csdn_collector import CSDNCollector
from src.collectors.juejin_collector import JuejinCollector
from src.collectors.telegram_collector import TelegramCollector
from src.collectors.facebook_collector import FacebookCollector
from src.processors.data_processor import LeadProcessor
from src.processors.categorizer import LeadCategorizer
from src.enrichers.lead_enricher import LeadEnricher
from src.enrichers.contact_finder import HunterEnricher
from src.scorers.intent_scorer import IntentScorer
from src.output.csv_exporter import CSVExporter
from src.utils.logger import setup_logger
from src.utils.config import Config

logger = setup_logger("Main")

def parse_args():
    parser = argparse.ArgumentParser(description="Engram Lead Discovery System")
    parser.add_argument("--query", type=str, default="agentic-ai tool issues", help="Search query for collectors")
    parser.add_argument("--limit", type=int, default=10, help="Limit number of leads per collector")
    return parser.parse_args()

def main():
    args = parse_args()
    logger.info(f"Starting Engram Lead Discovery System with query: '{args.query}'")

    try:
        # Set up pipeline
        collectors = [
            GithubCollector(query=args.query),
            RedditCollector(),
            DevCollector(tags=["ai", "machinelearning", "backend"]),
            MediumCollector(tags=["ai", "machine-learning", "backend-development"]),
            HackerNewsCollector(query=args.query),
            QiitaCollector(query="エージェント AI"), # Japanese: Agent AI
            CSDNCollector(query="智能体 AI"), # Chinese: Agent AI
            JuejinCollector(query="智能体 AI"),
            TelegramCollector(), # Manual ingestion placeholder
            FacebookCollector()  # Manual ingestion placeholder
        ]
        processor = LeadProcessor()
        categorizer = LeadCategorizer()
        profiler = LeadEnricher()
        contact_finder = HunterEnricher()
        scorer = IntentScorer()
        exporter = CSVExporter()

        # 1. Collection
        logger.info(f"Running {len(collectors)} collectors...")
        all_raw_leads = []
        for collector in collectors:
            try:
                raw_leads = collector.collect()
                all_raw_leads.extend(raw_leads)
            except Exception as e:
                logger.error(f"Error in collector {collector.__class__.__name__}: {e}")
        
        if not all_raw_leads:
            logger.warning("No leads collected. exiting.")
            return

        exporter.export(all_raw_leads, "raw/all_leads.csv")

        # 2. Processing & Categorization
        logger.info("Processing and categorizing collected leads...")
        processed_leads = processor.process(all_raw_leads)
        categorized_leads = categorizer.categorize(processed_leads)
        exporter.export(categorized_leads, "processed/categorized_leads.csv")

        # 3. Enrichment
        logger.info("Enriching lead profiles...")
        enriched_leads = profiler.enrich(categorized_leads)
        enriched_leads = contact_finder.enrich(enriched_leads)
        exporter.export(enriched_leads, "enriched/enriched_leads.csv")

        # 4. Scoring
        logger.info("Scoring leads based on intent signals...")
        scored_leads = scorer.score(enriched_leads)

        # 5. Output
        logger.info("Finalizing export...")
        exporter.export(scored_leads, "final/final_leads_master.csv")

        logger.info("Lead discovery pipeline completed successfully!")

    except Exception as e:
        logger.critical(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
