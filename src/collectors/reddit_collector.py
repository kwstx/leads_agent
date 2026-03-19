import praw
import os
from datetime import datetime
from typing import List
from .base_collector import BaseCollector
from ..schema.lead_schema import Lead
from ..utils.config import Config
from src.utils.multilingual_keywords import get_all_keywords

class RedditCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )
        self.keywords = get_all_keywords()

    def collect(self) -> List[Lead]:
        leads = []
        for keyword in self.keywords:
            try:
                # Search across all subreddits
                results = self.reddit.subreddit("all").search(keyword, limit=20)
                
                for post in results:
                    lead = Lead(
                        username=str(post.author) if post.author else "[deleted]",
                        platform="Reddit",
                        content=f"{post.title}\n{post.selftext}",
                        problem=f"Match for keyword: {keyword}",
                        source_link=f"https://reddit.com{post.permalink}" if hasattr(post, 'permalink') else post.url,
                        tags=[post.subreddit.display_name, keyword]
                    )
                    leads.append(lead)
            except Exception as e:
                print(f"Error collecting from Reddit for keyword '{keyword}': {str(e)}")
        
        # Deduplicate results by source_link
        unique_leads = {lead.source_link: lead for lead in leads}.values()
        return list(unique_leads)
