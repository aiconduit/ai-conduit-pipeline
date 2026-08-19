"""YouTubeチャンネル設定最適化スクリプト"""
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_youtube():
    creds = Credentials(
        token=None,
        refresh_token=os.environ.get("YOUTUBE_REFRESH_TOKEN",""),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("YOUTUBE_CLIENT_ID",""),
        client_secret=os.environ.get("YOUTUBE_CLIENT_SECRET",""),
    )
    return build("youtube", "v3", credentials=creds)

def update_channel():
    yt = get_youtube()
    ch = yt.channels().list(part="snippet,brandingSettings", mine=True).execute()
    channel_id = ch["items"][0]["id"]
    print(f"channel_id: {channel_id}")

    new_desc = """HyperFrames x Claude Code で作る自動動画チャンネルです。

毎日ソースコードをプレゼントしています。
コメントに「AI Conduit」と書いてください。

- HyperFramesサンプルのソースを毎日配布
- Claude Code x AI自動化の最新情報
- 毎日20時自動投稿

HTML を書けば動画になる時代が来ました。

GitHub: https://github.com/aiconduit
"""

    yt.channels().update(
        part="snippet",
        body={
            "id": channel_id,
            "snippet": {
                "description": new_desc,
                "defaultLanguage": "ja"
            }
        }
    ).execute()
    print("channel description updated")
    print(new_desc)

if __name__ == "__main__":
    update_channel()
