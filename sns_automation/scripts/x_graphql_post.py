#!/usr/bin/env python3
"""
X(Twitter) GraphQL API方式で投稿
Cookieベース認証（auth_token + ct0）
"""
import os
import json
import glob
import requests
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "")
X_CT0 = os.environ.get("X_CT0", "")
X_TWID = os.environ.get("X_TWID", "")

GRAPHQL_URL = "https://x.com/i/api/graphql/SoVnbfCycZ7fERGCwpZkYA/CreateTweet"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

def post_tweet(text, media_id=None):
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {BEARER_TOKEN}",
        "x-csrf-token": X_CT0,
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "ja",
        "Cookie": f"auth_token={X_AUTH_TOKEN}; ct0={X_CT0}; twid={X_TWID}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://x.com/",
        "Origin": "https://x.com",
    }
    payload = {
        "variables": {
            "tweet_text": text,
            "dark_request": False,
            "media": {
                "media_entities": [{"media_id": media_id, "tagged_users": []}] if media_id else [],
                "possibly_sensitive": False
            },
            "semantic_annotation_ids": []
        },
        "features": {
            "interactive_text_enabled": True,
            "longform_notetweets_inline_media_enabled": False,
        },
        "queryId": "SoVnbfCycZ7fERGCwpZkYA"
    }
    r = requests.post(GRAPHQL_URL, headers=headers, json=payload, timeout=15)
    if r.status_code not in (200, 201):
        raise Exception(f"X投稿失敗: {r.status_code} {r.text[:300]}")
    data = r.json()
    if "errors" in data:
        raise Exception(f"X APIエラー: {data['errors']}")
    tweet_id = data["data"]["create_tweet"]["tweet_results"]["result"]["rest_id"]
    return f"https://x.com/i/web/status/{tweet_id}"

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
        hashtags = plan_data.get("hashtags", [])
        tag_str = " ".join(hashtags[:5])
        return f"🤖 {title}\n\n詳細は概要欄をチェック！\n\n{tag_str} #AI #AIニュース #エンジニア"
    except Exception as e:
        print(f"⚠️ テキスト生成失敗: {e}")
        return "🤖 AIニュース速報 | AI Conduit\n\n#AI #AIニュース #エンジニア #自動化"

def upload_video_to_x(video_path):
    """動画をX Media Upload APIでアップロード（チャンク方式）"""
    import time as _time
    UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
    file_size = os.path.getsize(video_path)
    _h = {
        "authorization": f"Bearer {BEARER_TOKEN}",
        "x-csrf-token": X_CT0,
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-active-user": "yes",
        "Cookie": f"auth_token={X_AUTH_TOKEN}; ct0={X_CT0}; twid={X_TWID}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://x.com/", "Origin": "https://x.com",
    }
    headers_no_ct = _h

    r = requests.post(UPLOAD_URL, headers=headers_no_ct, data={
        "command": "INIT", "total_bytes": file_size,
        "media_type": "video/mp4", "media_category": "tweet_video",
    })
    if r.status_code not in (200, 201, 202):
        raise Exception(f"INIT失敗: {r.status_code}")
    media_id = r.json()["media_id_string"]

    chunk_size = 5 * 1024 * 1024
    segment = 0
    with open(video_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            requests.post(UPLOAD_URL, headers=headers_no_ct, data={
                "command": "APPEND", "media_id": media_id, "segment_index": segment,
            }, files={"media": chunk})
            segment += 1

    r = requests.post(UPLOAD_URL, headers=headers_no_ct, data={"command": "FINALIZE", "media_id": media_id})
    processing_info = r.json().get("processing_info", {})
    while processing_info.get("state") in ("pending", "in_progress"):
        _time.sleep(processing_info.get("check_after_secs", 3))
        r2 = requests.get(UPLOAD_URL, headers=headers_no_ct, params={"command": "STATUS", "media_id": media_id})
        processing_info = r2.json().get("processing_info", {})
    print(f"   ✅ 動画アップロード完了: {media_id}")
    return media_id

def main():
    pipeline = os.environ.get("PIPELINE", "p2")

    if not all([X_AUTH_TOKEN, X_CT0]):
        print("❌ X Cookie情報が不足しています")
        return

    # 動画ファイル取得
    import glob
    prefix = "v3news" if pipeline == "p3" else "v2news"
    render_dir = BASE_DIR / "projects" / "daily" / "renders"
    files = sorted(glob.glob(str(render_dir / f"{prefix}_*.mp4")), key=os.path.getmtime, reverse=True)
    media_id = None
    if files:
        print(f"📹 動画アップロード中: {files[0].split('/')[-1]}")
        try:
            media_id = upload_video_to_x(files[0])
        except Exception as e:
            print(f"⚠️ 動画アップロード失敗 ({e}) → テキストのみ投稿")

    tweet_text = get_tweet_text(pipeline)
    print(f"📝 ツイート: {tweet_text[:60]}...")

    url = post_tweet(tweet_text, media_id=media_id)
    print(f"✅ X投稿完了: {url}")

    log_path = BASE_DIR / "output" / "x_log.json"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "pipeline": pipeline}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
