import json
import logging
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    GITHUB_API_BASE,
    NICHE_FILTER,
    EXCLUDE_KEYWORDS,
    TRENDING_JSON,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("trending_collector")


def fetch_trending_repos(language: str = "", days: int = 1) -> list[dict[str, Any]]:
    url = f"{GITHUB_API_BASE}/search/repositories"
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    qualifiers = ["stars:>500", f"pushed:>{cutoff}"]
    if language:
        qualifiers.append(f"language:{language}")
    query = " ".join(qualifiers)
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": 50}

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AI-Conduit-Trending-Collector/1.0",
        "Authorization": "Bearer " + os.environ.get("API_SEARCH_PAT", ""),
    }

    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code == 403:
                retry_after = int(resp.headers.get("Retry-After", 60))
                logger.warning("Rate limited. Waiting %d seconds...", retry_after)
                time.sleep(retry_after)
                continue
            resp.raise_for_status()
            data = resp.json()
            logger.info("Fetched %d repos from GitHub API", len(data.get("items", [])))
            return data.get("items", [])
        except requests.RequestException as e:
            logger.error("Attempt %d/3 failed: %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** attempt)
    logger.error("Failed to fetch trending repos after 3 attempts")
    return []


def is_relevant(repo: dict[str, Any]) -> bool:
    text = (
        f"{repo.get('name', '')} {repo.get('description', '')} "
        f"{' '.join(repo.get('topics', []))} {repo.get('language', '')}"
    ).lower()

    for ex in EXCLUDE_KEYWORDS:
        if ex in text:
            return False

    return any(keyword in text for keyword in NICHE_FILTER)


def extract_repo_info(repo: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": repo.get("full_name", ""),
        "url": repo.get("html_url", ""),
        "description": repo.get("description", ""),
        "language": repo.get("language"),
        "topics": repo.get("topics", []),
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "today_stars": repo.get("stargazers_count", 0),
        "owner": repo.get("owner", {}).get("login", ""),
        "created_at": repo.get("created_at", ""),
        "updated_at": repo.get("updated_at", ""),
    }


def collect_and_save() -> None:
    logger.info("Starting GitHub trending collection (daily)")

    all_repos = fetch_trending_repos(days=1)
    relevant = [r for r in all_repos if is_relevant(r)]
    relevant.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)

    items = [extract_repo_info(r) for r in relevant]

    output = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "since": "1-day",
        "total_fetched": len(all_repos),
        "relevant_count": len(items),
        "topics": items[:20],
    }

    TRENDING_JSON.parent.mkdir(parents=True, exist_ok=True)
    TRENDING_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Saved %d relevant repos to %s", len(items), TRENDING_JSON)


if __name__ == "__main__":
    collect_and_save()
