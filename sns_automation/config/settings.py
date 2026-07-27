import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUT_DIR = BASE_DIR / "output"
VIDEOS_DIR = OUTPUT_DIR / "videos"
SCRIPTS_OUTPUT_DIR = OUTPUT_DIR / "scripts"

TRENDING_JSON = BASE_DIR / "trending_topics.json"
CONTENT_PLAN_JSON = BASE_DIR / "content_plan.json"
SCRIPTS_JSON = BASE_DIR / "scripts.json"

NICHE_FILTER = [
    "ai", "machine learning", "deep learning", "llm", "gpt",
    "automation", "dev-tools", "developer-tools", "cli",
    "open-source", "python", "data-science", "mlops",
    "agi", "artificial intelligence", "neural network",
    "api", "chatbot", "rag", "agent", "vector-database",
    "langchain", "pipeline", "workflow", "productivity",
]

EXCLUDE_KEYWORDS = [
    "game", "gaming", "crypto", "nft", "blockchain",
    "minecraft", "cryptocurrency", "wallet",
]

GITHUB_API_BASE = "https://api.github.com"

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-71eab12699f047a5891e62268c66c241")
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
