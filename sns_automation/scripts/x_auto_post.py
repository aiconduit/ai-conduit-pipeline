import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import CONTENT_PLAN_JSON, LOG_FORMAT, LOG_DATE_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("x_auto_post")

X_API_KEY = os.environ.get("X_API_KEY", "")
X_API_SECRET = os.environ.get("X_API_SECRET", "")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET", "")

API_BASE = "https://api.twitter.com/2"
OAUTH_URL = "https://api.twitter.com/oauth2/token"
UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"

THREAD_COUNT = 5
HASHTAGS_CORE = ["#AIConduit", "#AI", "#DevTools", "#自動化", "#GitHub"]

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK", "")


def generate_oauth_header(method: str, url: str, params: dict[str, Any] | None = None) -> dict[str, str]:
    import base64
    # OAuth 1.0a (user context) - for v2 endpoints with write scope
    from requests_oauthlib import OAuth1
    oauth = OAuth1(
        client_key=X_API_KEY,
        client_secret=X_API_SECRET,
        resource_owner_key=X_ACCESS_TOKEN,
        resource_owner_secret=X_ACCESS_SECRET,
    )
    return oauth


def post_tweet(text: str, reply_to: str | None = None) -> dict[str, Any] | None:
    from requests_oauthlib import OAuth1

    oauth = OAuth1(
        client_key=X_API_KEY,
        client_secret=X_API_SECRET,
        resource_owner_key=X_ACCESS_TOKEN,
        resource_owner_secret=X_ACCESS_SECRET,
    )

    payload: dict[str, Any] = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}

    for attempt in range(3):
        try:
            resp = requests.post(
                f"{API_BASE}/tweets",
                json=payload,
                auth=oauth,
                timeout=15,
            )
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("retry-after", 60))
                logger.warning("Rate limited. Waiting %d seconds...", retry_after)
                time.sleep(retry_after)
                continue
            if resp.status_code == 403:
                error_data = resp.json()
                logger.error("Authorization error: %s", error_data)
                return None
            resp.raise_for_status()
            result = resp.json()
            tweet_id = result.get("data", {}).get("id", "")
            logger.info("Tweet posted: id=%s", tweet_id)
            return result.get("data", {})
        except requests.RequestException as e:
            logger.error("Attempt %d/3 failed: %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** attempt)
    return None


def build_thread(plan: dict[str, Any]) -> list[str]:
    topic = plan.get("topic", "話題のトレンド")
    hook = plan.get("hook", f"{topic}について解説します")
    script = plan.get("script_60s", "")
    reason = plan.get("reason", "")
    hashtags = plan.get("hashtags", ["#AIConduit"])
    tags = plan.get("tags", ["ai", "automation"])

    full_hashtags = " ".join(HASHTAGS_CORE + hashtags)

    tweets: list[str] = []

    tweet1 = f"🔥 {hook}\n\n{reason[:100]}\n\nこのツール、めちゃくちゃ話題になってます 👇\n{full_hashtags}"
    tweets.append(tweet1)

    lines = [s.strip() for s in script.replace("。", "。\n").split("\n") if s.strip()]
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) < 240:
            current += line
        else:
            if current:
                chunks.append(current)
            current = line
    if current:
        chunks.append(current)

    for i, chunk in enumerate(chunks[:3]):
        tweets.append(f"{'📌 ' if i == 0 else '⚡ '}{chunk}")

    tweet5 = (
        f"💡 AI Conduitを使えば、このトレンドを自動で収集→動画生成→SNS投稿まで完全自動化！\n\n"
        f"🚀 GitHubで無料公開中：https://github.com/jimmylee/AI_Conduit\n\n"
        f"フォローして最新の開発者トレンドをチェック 👉 @AIConduit\n"
        f"{full_hashtags}"
    )
    tweets.append(tweet5)

    return tweets


def load_content_plan() -> list[dict[str, Any]] | None:
    if not CONTENT_PLAN_JSON.exists():
        logger.error("content_plan.json not found at %s", CONTENT_PLAN_JSON)
        return None
    data = json.loads(CONTENT_PLAN_JSON.read_text(encoding="utf-8"))
    plans = data.get("plans", [])
    logger.info("Loaded %d plans from content_plan.json", len(plans))
    return plans


def post_thread(plan: dict[str, Any]) -> bool:
    tweets = build_thread(plan)
    logger.info("Posting thread with %d tweets for topic: %s", len(tweets), plan.get("topic", ""))

    previous_id: str | None = None
    success_count = 0

    for i, tweet_text in enumerate(tweets):
        logger.info("Posting tweet %d/%d...", i + 1, len(tweets))
        result = post_tweet(tweet_text, reply_to=previous_id)
        if result:
            previous_id = result.get("id", "")
            success_count += 1
            time.sleep(2)
        else:
            logger.error("Failed to post tweet %d/%d", i + 1, len(tweets))
            return False

    logger.info("Thread posted successfully (%d/%d tweets)", success_count, len(tweets))
    return success_count == len(tweets)


def post_all() -> int:
    plans = load_content_plan()
    if not plans:
        logger.warning("No content plans to post")
        return 0

    success_count = 0
    for i, plan in enumerate(plans):
        logger.info("Posting thread %d/%d: %s", i + 1, len(plans), plan.get("topic", "unknown"))
        if post_thread(plan):
            success_count += 1
            logger.info("Thread %d/%d posted successfully", i + 1, len(plans))
        else:
            logger.error("Failed to post thread %d/%d", i + 1, len(plans))
        time.sleep(30)

    return success_count


def send_slack_notification(message: str) -> None:
    if not SLACK_WEBHOOK:
        return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=10)
    except requests.RequestException as e:
        logger.warning("Slack notification failed: %s", e)


if __name__ == "__main__":
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
        logger.error("X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET must be set")
        sys.exit(1)

    posted = post_all()
    logger.info("Total threads posted: %d", posted)

    if posted == 0:
        send_slack_notification("X auto-post: 0 threads posted (failure)")
    else:
        logger.info("X auto-post completed: %d threads", posted)
