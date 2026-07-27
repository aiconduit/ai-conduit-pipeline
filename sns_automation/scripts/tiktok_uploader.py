import json
import logging
import mimetypes
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import CONTENT_PLAN_JSON, VIDEOS_DIR, LOG_FORMAT, LOG_DATE_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("tiktok_uploader")

TIKTOK_ACCESS_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN", "")
TIKTOK_OPEN_ID = os.environ.get("TIKTOK_OPEN_ID", "")

API_BASE = "https://open.tiktokapis.com/v2"

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK", "")


def get_access_token() -> str | None:
    if TIKTOK_ACCESS_TOKEN:
        return TIKTOK_ACCESS_TOKEN
    logger.error("TIKTOK_ACCESS_TOKEN not set")
    return None


def init_upload(video_size: int) -> dict[str, Any] | None:
    token = get_access_token()
    if not token:
        return None

    url = f"{API_BASE}/video/init/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    payload = {
        "source_info": {
            "source": "FILE",
            "video_size": video_size,
            "chunk_size": video_size,
            "total_chunk_count": 1,
        },
        "open_id": TIKTOK_OPEN_ID,
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 401:
                logger.error("Token expired or invalid: %s", resp.text)
                return None
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("retry-after", 60))
                logger.warning("Rate limited. Waiting %d seconds...", retry_after)
                time.sleep(retry_after)
                continue
            resp.raise_for_status()
            data = resp.json()
            upload_url = data.get("data", {}).get("upload_url", "")
            publish_id = data.get("data", {}).get("publish_id", "")
            logger.info("Upload initialized: publish_id=%s", publish_id)
            return data.get("data", {})
        except requests.RequestException as e:
            logger.error("Attempt %d/3 to init upload failed: %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** attempt)
    return None


def upload_video_file(upload_url: str, video_path: Path) -> bool:
    mime_type, _ = mimetypes.guess_type(str(video_path))
    if not mime_type or not mime_type.startswith("video/"):
        mime_type = "video/mp4"

    headers = {
        "Content-Type": mime_type,
        "Content-Length": str(video_path.stat().st_size),
    }

    for attempt in range(3):
        try:
            with open(video_path, "rb") as f:
                resp = requests.put(upload_url, headers=headers, data=f, timeout=300)
            if resp.status_code == 429:
                time.sleep(60)
                continue
            if resp.status_code in (200, 201, 204):
                logger.info("Video file uploaded: %s", video_path.name)
                return True
            logger.warning("Upload attempt %d/3 returned %d", attempt + 1, resp.status_code)
        except requests.RequestException as e:
            logger.error("Upload attempt %d/3 failed: %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** attempt)
    return False


def check_upload_status(publish_id: str) -> str | None:
    token = get_access_token()
    if not token:
        return None

    url = f"{API_BASE}/video/status/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    payload = {
        "publish_id": publish_id,
        "open_id": TIKTOK_OPEN_ID,
    }

    for _ in range(30):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("data", {}).get("status", "")
            logger.info("Upload status: %s (publish_id=%s)", status, publish_id)
            if status == "PUBLISH_COMPLETE":
                return "complete"
            if status == "PUBLISH_FAILED":
                error_code = data.get("data", {}).get("error_code", "")
                logger.error("Publish failed: %s", error_code)
                return "failed"
            time.sleep(3)
        except requests.RequestException as e:
            logger.warning("Status check failed: %s", e)
            time.sleep(5)
    return "timeout"


def build_metadata(plan: dict[str, Any], index: int) -> tuple[str, list[str]]:
    topic = plan.get("topic", f"AI Conduit Topic #{index + 1}")
    hashtags = plan.get("hashtags", ["#AIConduit", "#自動化", "#AI"])
    tags = plan.get("tags", ["AIConduit", "automation"])

    all_hashtags = ["#fyp", "#programming", "#github", "#aitools", "#automation"] + hashtags
    all_hashtags = list(dict.fromkeys(all_hashtags))

    title = f"{topic} {' '.join(all_hashtags[:8])}"
    return title, all_hashtags


def post_video(token: str, video_id: str, title: str, hashtags: list[str]) -> bool:
    url = f"{API_BASE}/video/publish/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    payload = {
        "open_id": TIKTOK_OPEN_ID,
        "media_id": video_id,
        "title": title,
        "hashtags": hashtags,
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 429:
                time.sleep(60)
                continue
            resp.raise_for_status()
            logger.info("Video published: %s", title)
            return True
        except requests.RequestException as e:
            logger.error("Publish attempt %d/3 failed: %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** attempt)
    return False


def load_content_plan() -> list[dict[str, Any]] | None:
    if not CONTENT_PLAN_JSON.exists():
        logger.error("content_plan.json not found at %s", CONTENT_PLAN_JSON)
        return None
    data = json.loads(CONTENT_PLAN_JSON.read_text(encoding="utf-8"))
    plans = data.get("plans", [])
    logger.info("Loaded %d plans from content_plan.json", len(plans))
    return plans


def find_video_files() -> list[Path]:
    if not VIDEOS_DIR.exists():
        logger.warning("Videos directory does not exist: %s", VIDEOS_DIR)
        return []
    return sorted(VIDEOS_DIR.glob("*.mp4"))


def send_slack_notification(message: str) -> None:
    if not SLACK_WEBHOOK:
        return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": message}, timeout=10)
    except requests.RequestException as e:
        logger.warning("Slack notification failed: %s", e)


def upload_all() -> int:
    token = get_access_token()
    if not token:
        return 0

    plans = load_content_plan()
    if not plans:
        return 0

    video_files = find_video_files()
    if not video_files:
        logger.warning("No video files found in %s", VIDEOS_DIR)
        return 0

    success_count = 0
    for i, (plan, video_path) in enumerate(zip(plans, video_files)):
        if not video_path.exists():
            logger.warning("Video not found: %s. Skipping.", video_path)
            continue

        logger.info("Processing %d/%d: %s", i + 1, len(plans), video_path.name)

        init_data = init_upload(video_path.stat().st_size)
        if not init_data:
            logger.error("Failed to initialize upload for %s", video_path.name)
            continue

        upload_url = init_data.get("upload_url", "")
        publish_id = init_data.get("publish_id", "")

        if not upload_url:
            logger.error("No upload URL in init response")
            continue

        if not upload_video_file(upload_url, video_path):
            logger.error("Failed to upload file: %s", video_path.name)
            continue

        status = check_upload_status(publish_id)
        if status != "complete":
            logger.error("Upload did not complete: status=%s", status)
            continue

        title, hashtags = build_metadata(plan, i)
        if post_video(token, publish_id, title, hashtags):
            success_count += 1
            logger.info("Successfully posted to TikTok: %s", title)
        else:
            logger.error("Failed to publish video: %s", video_path.name)

        time.sleep(10)

    return success_count


if __name__ == "__main__":
    if not TIKTOK_ACCESS_TOKEN or not TIKTOK_OPEN_ID:
        logger.error("TIKTOK_ACCESS_TOKEN and TIKTOK_OPEN_ID must be set")
        sys.exit(1)

    posted = upload_all()
    logger.info("Total videos uploaded to TikTok: %d", posted)

    if posted == 0:
        send_slack_notification("TikTok upload: 0 videos posted (failure)")
