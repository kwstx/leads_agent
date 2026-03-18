import os
import argparse
from src.processors.llm_enricher import enrich_data
from src.utils.config import Config

def main():
    parser = argparse.ArgumentParser(description="Enrich cleaned data using LLM for lead discovery.")
    parser.add_argument("--input", default="cleaned_data.csv", help="Path to cleaned CSV file (default: cleaned_data.csv)")
    parser.add_argument("--output", default="enriched_data.csv", help="Path to save enriched data (default: enriched_data.csv)")
    
    args = parser.parse_args()
    
    # Check if API key is present
    if not Config.OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not found in .env file.")
        print("Please add 'OPENAI_API_KEY=your_key_here' to your .env file to enable LLM processing.")
        # We'll still try to run it, in case the environment has it or a local model is used.
    
    try:
        enrich_data(args.input, args.output)
    except Exception as e:
        print(f"Error during enrichment: {e}")

if __name__ == "__main__":
    main()
