import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials(
    token=None,
    refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
    client_id=os.environ["YOUTUBE_CLIENT_ID"],
    client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
    token_uri="https://oauth2.googleapis.com/token",
    scopes=["https://www.googleapis.com/auth/youtube"]
)
youtube = build("youtube", "v3", credentials=creds)

resp = youtube.channels().list(part="brandingSettings", mine=True).execute()
channel = resp["items"][0]
channel_id = channel["id"]
branding = channel.get("brandingSettings", {})
channel_info = branding.get("channel", {})

channel_info["description"] = """AIツール・GitHubトレンドを毎日紹介！

毎日投稿 | Daily AI news
GitHubトレンド解説
エンジニア向けAIツール紹介
就活・副業・自動化のヒント

━━━━━━━━━━━━━━━
無料プレゼントあり！
動画を見てコメントに「AIconduit」と書くと
この動画に関連した限定資料を無料でお渡しします！

Instagram（DM受付中）
https://www.instagram.com/aiconduit/
━━━━━━━━━━━━━━━

チャンネル登録で最新AI情報をキャッチ！"""

branding["channel"] = channel_info
youtube.channels().update(
    part="brandingSettings",
    body={"id": channel_id, "brandingSettings": branding}
).execute()
print("チャンネル説明更新完了:", channel_id)
