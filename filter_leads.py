import pandas as pd
import os
import sys

def filter_qualified_leads(input_file='enriched_data.csv', output_file='qualified_leads.csv', threshold=6):
    """
    Reads enriched lead data and filters for high-quality, relevant leads.
    
    Args:
        input_file (str): Path to the enriched CSV file.
        output_file (str): Path to save the filtered leads.
        threshold (int): Minimum intent score to consider a lead qualified.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print(f"Please ensure you have run 'enrich_leads.py' first to generate '{input_file}'.")
        return False

    print(f"Loading data from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False

    initial_count = len(df)
    
    # Check if necessary columns exist
    if 'is_relevant' not in df.columns or 'intent_score' not in df.columns:
        print(f"Error: Missing required columns 'is_relevant' or 'intent_score' in {input_file}.")
        print(f"Available columns: {df.columns.tolist()}")
        return False

    # Filtering logic:
    # 1. User must be relevant (is_relevant == True)
    # 2. Intent score must be 6 or higher (intent_score >= threshold)
    
    print(f"Filtering {initial_count} entries with threshold {threshold}...")
    
    # Ensure intent_score is numeric
    df['intent_score'] = pd.to_numeric(df['intent_score'], errors='coerce').fillna(0)
    
    # Apply filters
    qualified_df = df[
        (df['is_relevant'] == True) & 
        (df['intent_score'] >= threshold)
    ]
    
    final_count = len(qualified_df)
    removed_count = initial_count - final_count
    
    # Save the filtered results
    try:
        qualified_df.to_csv(output_file, index=False)
        print(f"Successfully filtered leads!")
        print(f"--- Summary ---")
        print(f"Total leads analyzed: {initial_count}")
        print(f"Qualified leads found: {final_count}")
        print(f"Irrelevant/Low-quality removed: {removed_count}")
        print(f"Filtered data saved to: {output_file}")
        return True
    except Exception as e:
        print(f"Error saving filtered CSV: {e}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Filter enriched leads for high-quality prospects.")
    parser.add_argument("--input", default="enriched_data.csv", help="Input enriched CSV file")
    parser.add_argument("--output", default="qualified_leads.csv", help="Output qualified CSV file")
    parser.add_argument("--threshold", type=int, default=6, help="Minimum intent score (1-10)")
    
    args = parser.parse_args()
    
    filter_qualified_leads(args.input, args.output, args.threshold)

if __name__ == "__main__":
    main()
