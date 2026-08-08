#!/usr/bin/env python3
"""共通YouTube投稿ユーティリティ（P5-P10用）P2と同じ認証方式"""
import os, sys, glob, json, tempfile
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
    
    if not refresh_token or not client_id:
        print("YouTube credentials missing")
        return None
    
    if token_json:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(token_json)
            f.flush()
            creds = Credentials.from_authorized_user_file(f.name,
                scopes=["https://www.googleapis.com/auth/youtube.upload"])
    else:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
    
    if creds.expired or not creds.valid:
        creds.refresh(Request())
    
    return build("youtube", "v3", credentials=creds)

def upload_video(video_path, title, description=""):
    yt = get_youtube_client()
    if not yt:
        return None
    
    tags = ["AI", "ClaudeCode", "エンジニア", "プログラミング", "AIツール", "Shorts"]
    desc = description or f"""{title}

Claude Code / Gemini CLI / Codex など最新AIコーディングツールの実践テクを毎日解説。

#AI #ClaudeCode #エンジニア #プログラミング #Shorts"""
    
    body = {
        "snippet": {
            "title": title[:100],
            "description": desc,
            "tags": tags,
            "categoryId": "28",
            "defaultLanguage": "ja",
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
    videos = sorted(glob.glob("projects/daily/renders/*.mp4"))
    if not videos:
        print("動画ファイルが見つかりません")
        sys.exit(0)
    
    video_file = videos[-1]
    stem = Path(video_file).stem.replace("v2news_", "").replace("_", " ")
    title = stem[:80] + " #Shorts"
    print(f"アップロード: {video_file}")
    upload_video(video_file, title)
