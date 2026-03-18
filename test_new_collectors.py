import sys
import os
# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.collectors.dev_collector import DevCollector
from src.collectors.medium_collector import MediumCollector
from src.collectors.hn_collector import HackerNewsCollector
from dotenv import load_dotenv

load_dotenv()

def test_collectors():
    print("Testing DEV Community Collector...")
    dev = DevCollector(tags=["ai"])
    leads = dev.collect()
    print(f"Found {len(leads)} leads from DEV Community")
    if leads:
        print(f"Sample: {leads[0].problem} by {leads[0].username}")
    
    print("\nTesting Medium Collector...")
    medium = MediumCollector(tags=["ai"])
    leads = medium.collect()
    print(f"Found {len(leads)} leads from Medium")
    if leads:
        print(f"Sample: {leads[0].problem} by {leads[0].username}")
        
    print("\nTesting Hacker News Collector...")
    hn = HackerNewsCollector(query="agentic ai")
    leads = hn.collect()
    print(f"Found {len(leads)} leads from Hacker News")
    if leads:
        # Check if we got comments too
        platforms = [l.platform for l in leads]
        print(f"Sample: {leads[0].problem} by {leads[0].username}")
        print(f"Comment leads: {len([l for l in leads if 'comment' in l.tags])}")

if __name__ == "__main__":
    test_collectors()
