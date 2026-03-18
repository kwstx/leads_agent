import sys
import argparse
from src.processors.llm_processor import process_csv_with_llm

def main():
    parser = argparse.ArgumentParser(description="Process scraped leads through LLM for discovery.")
    parser.add_argument("input", help="Path to input CSV file (e.g., github_raw.csv, reddit_raw.csv)")
    parser.add_argument("output", help="Path to save processed leads (e.g., filtered_leads.csv)")
    parser.add_argument("--model", help="LLM Model to use (overrides config)")
    parser.add_argument("--base-url", help="LLM Base URL to use (e.g. for Ollama: http://localhost:11434/v1)")
    
    args = parser.parse_args()
    
    try:
        process_csv_with_llm(args.input, args.output, model=args.model, base_url=args.base_url)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
