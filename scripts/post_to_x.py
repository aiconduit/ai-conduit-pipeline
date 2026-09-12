#!/usr/bin/env python3
"""
XにYouTube ShortsのURLを投稿する
"""
import os, sys, requests
from requests_oauthlib import OAuth1

API_KEY = os.environ["X_API_KEY"]
API_SECRET = os.environ["X_API_SECRET"]
ACCESS_TOKEN = os.environ["X_ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["X_ACCESS_SECRET"]

def post_tweet(text):
    auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    resp = requests.post(
        "https://api.twitter.com/2/tweets",
        auth=auth,
        json={"text": text}
    )
    print(f"Status: {resp.status_code}")
    print(resp.text[:300])
    return resp.status_code == 201

def main():
    youtube_url = os.environ.get("YOUTUBE_URL", "")
    sample_name = os.environ.get("SAMPLE_NAME", "")
    
    if not youtube_url:
        print("❌ YOUTUBE_URLが未設定")
        sys.exit(1)
    
    # ツイート文を生成
    hashtags = "#AI #AIツール #人工知能 #Shorts"
    text = f"🤖 新しいAIツールを紹介！\n\n{youtube_url}\n\n{hashtags}"
    
    print(f"投稿内容:\n{text}")
    
    success = post_tweet(text)
    if success:
        print("✅ X投稿成功！")
    else:
        print("❌ X投稿失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
