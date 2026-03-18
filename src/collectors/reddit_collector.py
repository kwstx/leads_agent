from typing import List
from .base_collector import BaseCollector
from ..schema.lead_schema import Lead

class RedditCollector(BaseCollector):
    def collect(self) -> List[Lead]:
        # Mocking Reddit search results
        return [
            Lead(
                username="reddit_user_99",
                platform="Reddit",
                content="I'm finding it hard to track leads across platforms.",
                problem="Lead tracking across platforms",
                source_link="https://reddit.com/r/SaaS/comments/789"
            ),
             Lead(
                username="startup_founder",
                platform="Reddit",
                content="Anyone using AI for lead enrichment?",
                problem="AI lead enrichment",
                source_link="https://reddit.com/r/startups/comments/012"
            )
        ]
