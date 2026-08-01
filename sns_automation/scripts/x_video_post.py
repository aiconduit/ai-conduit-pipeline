#!/usr/bin/env python3
"""
X(Twitter) 動画自動投稿スクリプト
OAuth 1.0a + Media Upload API でReels動画をツイート
"""
import os
import json
import time
import glob
import requests
from pathlib import Path
from requests_oauthlib import OAuth1

BASE_DIR = Path(__file__).parent.parent.parent

X_API_KEY = os.environ.get("X_API_KEY", "")
X_API_SECRET = os.environ.get("X_API_SECRET", "")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET", "")
UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
API_BASE = "https://api.twitter.com/2"

def get_oauth():
    return OAuth1(
        client_key=X_API_KEY,
        client_secret=X_API_SECRET,
        resource_owner_key=X_ACCESS_TOKEN,
        resource_owner_secret=X_ACCESS_SECRET,
    )

def upload_video(video_path):
    """動画をX Media Upload APIでアップロード（チャンク方式）"""
    oauth = get_oauth()
    file_size = os.path.getsize(video_path)

    # INIT
    resp = requests.post(UPLOAD_URL, auth=oauth, data={
        "command": "INIT",
        "total_bytes": file_size,
        "media_type": "video/mp4",
        "media_category": "tweet_video",
    })
    if resp.status_code not in (200, 201, 202):
        raise Exception(f"INIT失敗: {resp.status_code} {resp.text[:200]}")
    media_id = resp.json()["media_id_string"]
    print(f"   INIT OK: media_id={media_id}")

    # APPEND（5MB chunks）
    chunk_size = 5 * 1024 * 1024
    segment = 0
    with open(video_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            resp = requests.post(UPLOAD_URL, auth=oauth, data={
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": segment,
            }, files={"media": chunk})
            if resp.status_code not in (200, 204):
                raise Exception(f"APPEND失敗 segment={segment}: {resp.status_code}")
            segment += 1
            print(f"   APPEND segment={segment} OK")

    # FINALIZE
    resp = requests.post(UPLOAD_URL, auth=oauth, data={
        "command": "FINALIZE",
        "media_id": media_id,
    })
    if resp.status_code not in (200, 201):
        raise Exception(f"FINALIZE失敗: {resp.status_code} {resp.text[:200]}")

    # 処理完了待機
    processing_info = resp.json().get("processing_info", {})
    while processing_info.get("state") in ("pending", "in_progress"):
        wait = processing_info.get("check_after_secs", 3)
        print(f"   処理中... {wait}秒待機")
        time.sleep(wait)
        resp = requests.get(UPLOAD_URL, auth=oauth, params={
            "command": "STATUS", "media_id": media_id
        })
        processing_info = resp.json().get("processing_info", {})

    if processing_info.get("state") == "failed":
        raise Exception(f"動画処理失敗: {processing_info}")

    print(f"   ✅ 動画アップロード完了: {media_id}")
    return media_id

def post_tweet_with_video(text, media_id):
    """動画付きツイートを投稿"""
    oauth = get_oauth()
    payload = {
        "text": text,
        "media": {"media_ids": [media_id]},
    }
    resp = requests.post(f"{API_BASE}/tweets", json=payload, auth=oauth, timeout=15)
    if resp.status_code not in (200, 201):
        raise Exception(f"ツイート失敗: {resp.status_code} {resp.text[:200]}")
    tweet_id = resp.json()["data"]["id"]
    url = f"https://x.com/i/web/status/{tweet_id}"
    print(f"✅ X投稿完了: {url}")
    return url

def get_latest_video(pipeline="p2"):
    prefix = "v3news" if pipeline == "p3" else "v2news"
    render_dir = BASE_DIR / "projects" / "daily" / "renders"
    files = sorted(glob.glob(str(render_dir / f"{prefix}_*.mp4")), key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def get_tweet_text(pipeline="p2"):
    plan_file = "news_content_plan_p3.json" if pipeline == "p3" else "news_content_plan.json"
    plan_path = BASE_DIR / "sns_automation" / plan_file
    try:
        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)
        plan_data = plan.get("plan", plan)
        if isinstance(plan_data, dict) and "plan" in plan_data:
            plan_data = plan_data["plan"]
        title = plan_data.get("selected_title", "AIニュース速報")[:50]
        return f"🤖 {title}\n\n詳細は概要欄をチェック！\n\n#AI #AIニュース #エンジニア #自動化 #Shorts"
    except:
        return "🤖 AIニュース速報 | AI Conduit\n\n#AI #AIニュース #エンジニア #自動化"

def main():
    pipeline = os.environ.get("PIPELINE", "p2")

    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET]):
        print("❌ X API認証情報が不足しています")
        return

    video_path = get_latest_video(pipeline)
    if not video_path:
        print(f"❌ 動画ファイルが見つかりません")
        return

    print(f"🎬 動画: {video_path}")
    tweet_text = get_tweet_text(pipeline)
    print(f"📝 ツイート: {tweet_text[:50]}...")

    media_id = upload_video(video_path)
    url = post_tweet_with_video(tweet_text, media_id)

    log_path = BASE_DIR / "output" / "x_log.json"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "video": video_path, "pipeline": pipeline}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
