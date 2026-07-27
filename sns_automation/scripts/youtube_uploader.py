import json
import logging
import sys
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    CONTENT_PLAN_JSON,
    YOUTUBE_CLIENT_ID,
    YOUTUBE_CLIENT_SECRET,
    YOUTUBE_REFRESH_TOKEN,
    VIDEOS_DIR,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("youtube_uploader")

UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def refresh_access_token() -> str | None:
    if not YOUTUBE_REFRESH_TOKEN:
        logger.error("YOUTUBE_REFRESH_TOKEN not set")
        return None

    data = {
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "refresh_token": YOUTUBE_REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }
    try:
        resp = requests.post(TOKEN_URL, data=data, timeout=15)
        resp.raise_for_status()
        token = resp.json()["access_token"]
        logger.info("Access token refreshed successfully")
        return token
    except requests.RequestException as e:
        logger.error("Failed to refresh token: %s", e)
        return None


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


def initiate_resumable_upload(access_token: str, metadata: dict[str, Any]) -> str | None:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Upload-Content-Type": "video/*",
    }
    try:
        resp = requests.post(UPLOAD_URL, headers=headers, json=metadata, timeout=30)
        resp.raise_for_status()
        upload_url = resp.headers.get("Location")
        if upload_url:
            logger.info("Resumable upload URL obtained")
            return upload_url
        logger.error("No Location header in response")
        return None
    except requests.RequestException as e:
        logger.error("Failed to initiate upload: %s", e)
        return None


def upload_video_chunks(upload_url: str, video_path: Path) -> dict[str, Any] | None:
    file_size = video_path.stat().st_size
    chunk_size = 4 * 1024 * 1024  # 4MB
    headers = {
        "Content-Length": str(file_size),
        "Content-Type": "video/*",
    }

    try:
        with open(video_path, "rb") as f:
            if file_size <= chunk_size:
                headers["Content-Range"] = f"bytes 0-{file_size - 1}/{file_size}"
                resp = requests.put(upload_url, headers=headers, data=f, timeout=300)
            else:
                resp = upload_chunked(upload_url, f, file_size, chunk_size)

            resp.raise_for_status()
            result = resp.json()
            video_id = result.get("id", "unknown")
            logger.info("Upload complete! Video ID: %s", video_id)
            return result
    except requests.RequestException as e:
        logger.error("Upload failed: %s", e)
        return None


def upload_chunked(upload_url: str, file_obj, file_size: int, chunk_size: int) -> requests.Response:
    uploaded = 0
    last_resp = None
    while uploaded < file_size:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        end = min(uploaded + len(chunk), file_size) - 1
        content_range = f"bytes {uploaded}-{end}/{file_size}"
        headers = {
            "Content-Length": str(len(chunk)),
            "Content-Range": content_range,
        }
        resp = requests.put(upload_url, headers=headers, data=chunk, timeout=120)
        if resp.status_code not in (200, 201, 308):
            resp.raise_for_status()
        uploaded += len(chunk)
        last_resp = resp
        logger.debug("Uploaded %d/%d bytes", uploaded, file_size)
    return last_resp


def build_metadata(plan: dict[str, Any], video_index: int) -> dict[str, Any]:
    topic = plan.get("topic", f"AI Conduit Topic #{video_index + 1}")
    description = plan.get("reason", "")
    hashtags = " ".join(plan.get("hashtags", ["#AIConduit", "#自動化"]))
    tags = plan.get("tags", ["AIConduit", "automation", "AI"])

    return {
        "snippet": {
            "title": f"【AI Conduit】{topic} | GitHubトレンド解説",
            "description": f"{description}\n\n{hashtags}\n\n▶ AI Conduitで自動化：https://github.com/jimmylee/AI_Conduit",
            "tags": tags + ["AIConduit", "GitHub", "自動化", "AI", "プログラミング"],
            "categoryId": "28",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }


def upload_all() -> None:
    access_token = refresh_access_token()
    if not access_token:
        return

    plans = load_content_plan()
    if not plans:
        return

    video_files = find_video_files()
    if not video_files:
        logger.warning("No video files found in %s. Skipping upload.", VIDEOS_DIR)
        return

    for i, (plan, video_path) in enumerate(zip(plans, video_files)):
        if not video_path.exists():
            logger.warning("Video file not found: %s. Skipping.", video_path)
            continue

        metadata = build_metadata(plan, i)
        logger.info("Uploading video %d/%d: %s", i + 1, len(plans), video_path.name)

        upload_url = initiate_resumable_upload(access_token, metadata)
        if not upload_url:
            continue

        result = upload_video_chunks(upload_url, video_path)
        if result:
            logger.info("Successfully uploaded: %s -> https://youtu.be/%s",
                        video_path.name, result.get("id"))
        else:
            logger.error("Failed to upload: %s", video_path.name)


if __name__ == "__main__":
    upload_all()
