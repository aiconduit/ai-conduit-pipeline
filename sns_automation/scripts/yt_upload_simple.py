#!/usr/bin/env python3
"""共通YouTube投稿ユーティリティ（P5-P10用）"""
import os, sys, glob, json, tempfile
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_youtube_client():
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON", "").strip()
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip()
    if not refresh_token or not client_id or not client_secret:
        print("YouTube credentials missing")
        return None
    # token_jsonが有効なJSONかチェック
    creds = None
    if token_json:
        try:
            json.loads(token_json)  # 有効なJSONか確認
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                f.write(token_json); f.flush()
                creds = Credentials.from_authorized_user_file(f.name,
                    scopes=["https://www.googleapis.com/auth/youtube.upload"])
        except (json.JSONDecodeError, Exception):
            creds = None
    if creds is None:
        creds = Credentials(token=None, refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id, client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.upload"])
    if not creds.valid:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def upload_video(video_path, title):
    yt = get_youtube_client()
    if not yt:
        return None
    body = {
        "snippet": {"title": title[:100], "description": title,
                    "tags": ["AI","ClaudeCode","Shorts"], "categoryId": "28"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024*5)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = req.next_chunk()
    vid = response.get("id", "")
    print(f"タイトル: {title}")
    print(f"OK https://youtube.com/shorts/{vid}")
    return vid

if __name__ == "__main__":
    videos = sorted(glob.glob("projects/daily/renders/*.mp4"))
    if not videos:
        print("No video found"); sys.exit(0)
    video_file = videos[-1]
    title = Path(video_file).stem.replace("v2news_","").replace("_"," ")[:80] + " #Shorts"
    print(f"Upload: {video_file}")
    upload_video(video_file, title)
