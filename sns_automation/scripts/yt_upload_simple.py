#!/usr/bin/env python3
"""共通YouTube投稿ユーティリティ（P5-P10用）"""
import os, sys, glob, json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_youtube_client():
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON", "")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    
    if not all([token_json, client_id, client_secret, refresh_token]):
        print("YouTube credentials not found")
        return None
    
    try:
        token_data = json.loads(token_json)
    except:
        token_data = {}
    
    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def upload_video(video_path, title, description="", tags=None):
    yt = get_youtube_client()
    if not yt:
        return None
    
    tags = tags or ["AI", "ClaudeCode", "エンジニア", "プログラミング", "AIツール"]
    body = {
        "snippet": {
            "title": title[:100],
            "description": description or f"{title}\n\n#AI #ClaudeCode #エンジニア",
            "tags": tags,
            "categoryId": "28",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024*5)
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        _, response = request.next_chunk()
    
    video_id = response.get("id", "")
    url = f"https://youtube.com/shorts/{video_id}"
    print(f"タイトル: {title}")
    print(f"✅ {url}")
    return url

if __name__ == "__main__":
    # 最新のMP4ファイルを探す
    videos = sorted(glob.glob("projects/daily/renders/*.mp4"))
    if not videos:
        print("動画ファイルが見つかりません")
        sys.exit(0)
    
    video_file = videos[-1]
    title = Path(video_file).stem.replace("v2news_", "").replace("_", " ")[:80]
    upload_video(video_file, title)
