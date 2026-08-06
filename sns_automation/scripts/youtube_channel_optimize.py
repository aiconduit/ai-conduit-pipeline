#!/usr/bin/env python3
"""YouTubeチャンネル設定最適化スクリプト"""
import os, json
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
    
    # チャンネル情報取得
    ch = yt.channels().list(part="snippet,brandingSettings", mine=True).execute()
    channel_id = ch["items"][0]["id"]
    print(f"チャンネルID: {channel_id}")
    print(f"現在の説明: {ch['items'][0]['snippet'].get('description','')[:100]}")
    
    # 説明文・キーワード更新
    new_desc = """🤖 毎日15秒でAI最新情報をお届け！

エンジニア・IT学生・AI初学者必見のチャンネルです。

✅ 毎日自動投稿（20時・21時）
✅ 最新AIツール・ニュース・テクニック
✅ コメントに「AI」→無料プレゼント🎁

【チャンネル登録して毎日チェック！】

#AI #AIニュース #エンジニア #ChatGPT #プログラミング"""

    keywords = "AI,人工知能,ChatGPT,Claude,エンジニア,プログラミング,自動化,AIニュース,テクノロジー,副業,生産性,Shorts,AIツール"
    
    yt.channels().update(
        part="snippet,brandingSettings",
        body={
            "id": channel_id,
            "snippet": {"description": new_desc, "defaultLanguage": "ja"},
            "brandingSettings": {
                "channel": {"keywords": keywords}
            }
        }
    ).execute()
    print("✅ チャンネル説明・キーワード更新完了")

if __name__ == "__main__":
    update_channel()
