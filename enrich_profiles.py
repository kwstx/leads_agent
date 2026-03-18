import os
import argparse
from src.enrichers.profile_scraper import ProfileScraper
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Enrich leads with profile metadata from GitHub, DEV, and Medium.")
    parser.add_argument("--input", default="cleaned_data.csv", help="Path to cleaned CSV file (default: cleaned_data.csv)")
    parser.add_argument("--output", default="enriched_leads.csv", help="Path to save enriched data (default: enriched_leads.csv)")
    
    args = parser.parse_args()
    
    scraper = ProfileScraper()
    
    # Enrichment logic
    scraper.enrich_csv(args.input, args.output)

if __name__ == "__main__":
    main()
