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
from config.settings import LOG_FORMAT, LOG_DATE_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("instagram_dm_bot")

INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ID = os.environ.get("INSTAGRAM_BUSINESS_ID", "")
GIFT_LINK = os.environ.get("GIFT_LINK", "https://github.com/jimmylee/AI_Conduit")

GRAPH_API_BASE = "https://graph.facebook.com/v22.0"
POLL_INTERVAL = 900  # 15 minutes

TRIGGER_KEYWORDS = [
    "FREE", "free", "無料", "プレゼント", "ゲット", "欲しい", "ください",
    "参加", "どうやる", "使い方", "方法", "link", "Link", "送って",
    "すごい", "いいね", "欲しいです", "ほしい", "dm", "DM",
    "get", "want", "interested", "how to", "tutorial",
]

DM_TEMPLATE = """🎁 AI Conduit 無料プレゼントについて

ご質問・コメントありがとうございます！
AI Conduitの完全自動化テンプレートを無料でお渡ししています。

こちらから受け取ってください 👇
{gift_link}

これを使えば、今日からGitHubトレンドを自動収集→動画生成まで
完全自動化できます！

さらに質問があればいつでもどうぞ！"""


def get_media_comments(media_id: str, since: str | None = None) -> list[dict[str, Any]]:
    url = f"{GRAPH_API_BASE}/{media_id}/comments"
    params: dict[str, Any] = {
        "access_token": INSTAGRAM_ACCESS_TOKEN,
        "fields": "id,text,username,timestamp,from{id,username}",
        "limit": 100,
    }
    if since:
        params["since"] = since

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
    except requests.RequestException as e:
        logger.error("Failed to fetch comments for media %s: %s", media_id, e)
        return []


def get_recent_media() -> list[dict[str, Any]]:
    url = f"{GRAPH_API_BASE}/{INSTAGRAM_BUSINESS_ID}/media"
    params: dict[str, Any] = {
        "access_token": INSTAGRAM_ACCESS_TOKEN,
        "fields": "id,caption,timestamp,permalink,comments_count",
        "limit": 25,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
    except requests.RequestException as e:
        logger.error("Failed to fetch recent media: %s", e)
        return []


def is_follower(user_id: str) -> bool:
    url = f"{GRAPH_API_BASE}/{user_id}"
    params: dict[str, Any] = {
        "access_token": INSTAGRAM_ACCESS_TOKEN,
        "fields": "followed_by",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("followed_by", False)
    except requests.RequestException as e:
        logger.warning("Follower check failed for user %s: %s", user_id, e)
        return False


def send_dm(recipient_id: str) -> bool:
    url = f"{GRAPH_API_BASE}/{INSTAGRAM_BUSINESS_ID}/messages"
    payload = {
        "access_token": INSTAGRAM_ACCESS_TOKEN,
        "recipient": {"id": recipient_id},
        "message": {"text": DM_TEMPLATE.format(gift_link=GIFT_LINK)},
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 400:
                error_data = resp.json()
                logger.warning("DM send failed (attempt %d/3): %s", attempt + 1, error_data)
                if "rate" in str(error_data).lower():
                    time.sleep(60)
                    continue
                return False
            resp.raise_for_status()
            logger.info("DM sent to user %s", recipient_id)
            return True
        except requests.RequestException as e:
            logger.error("DM send error (attempt %d/3): %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** attempt)
    return False


def reply_to_comment(comment_id: str, text: str) -> bool:
    url = f"{GRAPH_API_BASE}/{comment_id}/replies"
    payload = {
        "access_token": INSTAGRAM_ACCESS_TOKEN,
        "message": text,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Replied to comment %s", comment_id)
        return True
    except requests.RequestException as e:
        logger.error("Failed to reply to comment %s: %s", comment_id, e)
        return False


def matches_trigger(text: str) -> bool:
    return any(kw in text for kw in TRIGGER_KEYWORDS)


def load_processed_comments() -> set[str]:
    path = Path(__file__).resolve().parent / "processed_comments.json"
    if path.exists():
        return set(json.loads(path.read_text(encoding="utf-8")))
    return set()


def save_processed_comments(ids: set[str]) -> None:
    path = Path(__file__).resolve().parent / "processed_comments.json"
    path.write_text(json.dumps(list(ids), ensure_ascii=False), encoding="utf-8")


def run_once() -> int:
    processed = load_processed_comments()
    new_processed = set(processed)
    dm_count = 0

    media_list = get_recent_media()
    if not media_list:
        logger.warning("No media found for business ID: %s", INSTAGRAM_BUSINESS_ID)
        return 0

    for media in media_list:
        media_id = media.get("id", "")
        comments = get_media_comments(media_id)
        logger.info("Found %d comments on media %s", len(comments), media_id)

        for comment in comments:
            comment_id = comment.get("id", "")
            if comment_id in processed:
                continue

            text = comment.get("text", "")
            from_user = comment.get("from", {})
            user_id = from_user.get("id", "")
            username = from_user.get("username", "")

            if not matches_trigger(text):
                new_processed.add(comment_id)
                continue

            logger.info("Trigger match from @%s: '%s'", username, text[:60])

            if not user_id:
                new_processed.add(comment_id)
                continue

            if is_follower(user_id):
                logger.info("@%s is a follower. Sending DM...", username)
                if send_dm(user_id):
                    dm_count += 1
                    reply_to_comment(comment_id, "DMを送りました！確認してみてください 📩")
                else:
                    logger.warning("Failed to send DM to @%s", username)
            else:
                logger.info("@%s is not a follower. Sending follow prompt.", username)
                reply_to_comment(
                    comment_id,
                    "ありがとうございます！フォローしていただいてからDMでプレゼントをお送りします 🎁",
                )

            new_processed.add(comment_id)

    save_processed_comments(new_processed)
    return dm_count


def run_loop() -> None:
    logger.info("Instagram DM bot started (polling every %d seconds)", POLL_INTERVAL)
    while True:
        try:
            sent = run_once()
            logger.info("Cycle complete. DMs sent this run: %d", sent)
        except Exception as e:
            logger.error("Unhandled error in cycle: %s", e)
        logger.info("Sleeping for %d seconds...", POLL_INTERVAL)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ID:
        logger.error("INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ID must be set")
        sys.exit(1)

    if "--once" in sys.argv:
        sent = run_once()
        logger.info("Single run complete. DMs sent: %d", sent)
        sys.exit(0)
    else:
        run_loop()
