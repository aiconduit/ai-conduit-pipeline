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

def post_tweet(text):
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
            "media": {"media_entities": [], "possibly_sensitive": False},
            "semantic_annotation_ids": []
        },
        "features": {
            "interactive_text_enabled": True,
            "longform_notetweets_inline_media_enabled": False,
        }
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

def main():
    pipeline = os.environ.get("PIPELINE", "p2")

    if not all([X_AUTH_TOKEN, X_CT0]):
        print("❌ X Cookie情報が不足しています")
        return

    tweet_text = get_tweet_text(pipeline)
    print(f"📝 ツイート: {tweet_text[:60]}...")

    url = post_tweet(tweet_text)
    print(f"✅ X投稿完了: {url}")

    log_path = BASE_DIR / "output" / "x_log.json"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "pipeline": pipeline}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
