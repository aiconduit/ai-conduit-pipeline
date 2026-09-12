#!/usr/bin/env python3
"""
X(Twitter)に動画を直接アップロードして投稿する
Twitter API v1.1 chunked media upload + v2 tweet
"""
import os, sys, time, requests
from requests_oauthlib import OAuth1

API_KEY = os.environ["X_API_KEY"]
API_SECRET = os.environ["X_API_SECRET"]
ACCESS_TOKEN = os.environ["X_ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["X_ACCESS_SECRET"]

auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
TWEET_URL = "https://api.twitter.com/2/tweets"

def upload_video(video_path):
    """チャンク分割で動画をアップロード"""
    file_size = os.path.getsize(video_path)
    print(f"動画サイズ: {file_size/1024/1024:.1f}MB")

    # INIT
    resp = requests.post(UPLOAD_URL, auth=auth, data={
        "command": "INIT",
        "media_type": "video/mp4",
        "media_category": "tweet_video",
        "total_bytes": file_size,
    })
    print(f"INIT: {resp.status_code}")
    if resp.status_code != 202:
        print(resp.text)
        return None
    media_id = resp.json()["media_id_string"]
    print(f"media_id: {media_id}")

    # APPEND（5MB単位）
    chunk_size = 5 * 1024 * 1024
    segment = 0
    with open(video_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            resp = requests.post(UPLOAD_URL, auth=auth, data={
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": segment,
            }, files={"media": chunk})
            print(f"APPEND segment {segment}: {resp.status_code}")
            segment += 1

    # FINALIZE
    resp = requests.post(UPLOAD_URL, auth=auth, data={
        "command": "FINALIZE",
        "media_id": media_id,
    })
    print(f"FINALIZE: {resp.status_code}")
    data = resp.json()

    # 処理待ち
    if "processing_info" in data:
        for _ in range(30):
            state = data["processing_info"]["state"]
            print(f"  状態: {state}")
            if state == "succeeded":
                break
            if state == "failed":
                print("❌ 動画処理失敗")
                return None
            time.sleep(5)
            resp = requests.get(UPLOAD_URL, auth=auth, params={"command": "STATUS", "media_id": media_id})
            data = resp.json()

    return media_id

def post_tweet_with_video(media_id, text):
    resp = requests.post(TWEET_URL, auth=auth, json={
        "text": text,
        "media": {"media_ids": [media_id]}
    })
    print(f"Tweet: {resp.status_code}")
    print(resp.text[:300])
    return resp.status_code == 201

def main():
    video_path = os.environ.get("VIDEO_PATH", "output.mp4")
    sample_name = os.environ.get("SAMPLE_NAME", "")
    youtube_url = os.environ.get("YOUTUBE_URL", "")

    if not os.path.exists(video_path):
        print(f"❌ 動画ファイルが見つかりません: {video_path}")
        sys.exit(1)

    print(f"動画アップロード開始: {video_path}")
    media_id = upload_video(video_path)
    if not media_id:
        sys.exit(1)

    hashtags = "#AI #AIツール #人工知能 #Shorts"
    if youtube_url:
        text = f"🤖 新しいAIツール紹介！\n\n{youtube_url}\n\n{hashtags}"
    else:
        text = f"🤖 新しいAIツール紹介！\n\n{hashtags}"

    print(f"投稿内容: {text}")
    success = post_tweet_with_video(media_id, text)
    if success:
        print("✅ X動画投稿成功！")
    else:
        print("❌ X投稿失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
