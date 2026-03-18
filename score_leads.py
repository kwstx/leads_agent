import pandas as pd
import re
import os

def calculate_lead_score(row):
    """
    Calculates a score from 0 to 100 for a lead based on various factors.
    """
    score = 0
    content = str(row.get('content', '')).lower()
    title = str(row.get('title', '')).lower()
    combined_text = title + " " + content

    # 1. Problem Keywords (30 points)
    problem_keywords = [
        'bug', 'error', 'fail', 'issue', 'problem', 'broken', 'mismatch', 
        'integration', 'failure', 'bottleneck', 'latency', 'exception', 
        'crash', 'fix', 'solved', 'not working', 'struggling'
    ]
    problem_found = any(kw in combined_text for kw in problem_keywords)
    if problem_found:
        score += 30

    # 2. Explicit Help Requests (30 points)
    help_keywords = [
        'help', 'how to', 'advice', 'suggestion', 'guide', 'support', 
        'question', 'assistance', 'stuck', 'wondering', 'recommend', 
        'can anyone', 'please', 'any ideas'
    ]
    help_found = any(kw in combined_text for kw in help_keywords)
    if help_found:
        score += 30

    # 3. Tool Mentions (20 points)
    tools = [
        'langchain', 'llamaindex', 'autogpt', 'babyagi', 'crewai', 
        'langgraph', 'haystack', 'semantic kernel', 'openai', 'anthropic', 
        'claude', 'gpt', 'llama', 'mistral', 'ollama', 'vllm'
    ]
    tool_found = any(tool in combined_text for tool in tools)
    if tool_found:
        score += 20

    # 4. Availability of Contact Information (20 points)
    # Check if 'contact_info' column exists and is valid
    contact_available = False
    if 'contact_info' in row and pd.notna(row['contact_info']) and str(row['contact_info']).strip() != '':
        contact_available = True
    else:
        # Search for email or discord patterns in content/username
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        discord_pattern = r'discord\.gg/[a-zA-Z0-9]+|discordapp\.com/users/[0-9]+'
        twitter_pattern = r'twitter\.com/[a-zA-Z0-9_]+|t\.me/[a-zA-Z0-9_]+'
        
        if re.search(email_pattern, combined_text) or \
           re.search(discord_pattern, combined_text) or \
           re.search(twitter_pattern, combined_text):
            contact_available = True
        
        # Check username for bot/automated accounts (negative factor?)
        # But here we just check availability. 
        # If username looks like a real handle, we might consider it.
    
    if contact_available:
        score += 20

    return score

def score_dataset(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    print("Calculating lead scores...")
    df['lead_score'] = df.apply(calculate_lead_score, axis=1)
    
    # Sort by lead_score descending
    df = df.sort_values(by='lead_score', ascending=False)
    
    print(f"Saving scored leads to {output_file}...")
    df.to_csv(output_file, index=False)
    print("Done!")

if __name__ == "__main__":
    # The user has cleaned_data.csv open, so let's use it as default source
    # unless they want enriched_leads.csv
    input_csv = 'cleaned_data.csv'
    output_csv = 'scored_leads.csv'
    
    # Check if cleaned_data.csv exists, if not maybe try other locations
    if not os.path.exists(input_csv):
        # Check standard data locations
        potential_inputs = [
            'data/enriched/enriched_leads.csv',
            'data/processed/categorized_leads.csv'
        ]
        for p in potential_inputs:
            if os.path.exists(p):
                input_csv = p
                break
    
    score_dataset(input_csv, output_csv)
