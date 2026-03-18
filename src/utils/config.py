import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
    HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
    
    # LLM Config
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

    # Reddit Config
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "EngramLeadScraper/1.0 by /u/Engram")
    
    # Regional Platforms
    QIITA_API_KEY = os.getenv("QIITA_API_KEY")
    # For CSDN and Juejin, we might use public endpoints, but having keys for future use is good.
    CSDN_API_KEY = os.getenv("CSDN_API_KEY")
    JUEJIN_API_KEY = os.getenv("JUEJIN_API_KEY")
    
    # Storage Paths
    DATA_DIR = "data"
    RAW_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
    ENRICHED_DIR = os.path.join(DATA_DIR, "enriched")
    FINAL_DIR = os.path.join(DATA_DIR, "final")

    # Intent Scoring Constants
    BASE_INTENT_SCORE = 0.2
    HIGH_INTENT_KEYWORDS = {
        "urgent": 0.4,
        "how to": 0.2,
        "problem": 0.3,
        "help": 0.3,
        "issue": 0.1,
        "error": 0.1,
        "anyone know": 0.2,
        "solution": 0.4
    }

    # Categories
    CATEGORIES = {
        "AI/ML": ["ai", "machine learning", "neural network", "transformer", "llm", "agent"],
        "DevOps": ["docker", "kubernetes", "deployment", "github actions", "pipeline"],
        "Frontend": ["react", "vue", "typescript", "ui", "ux", "browser"],
        "Security": ["auth", "identity", "security", "token", "password", "hack"]
    }
