#!/usr/bin/env python3
"""
X(Twitter)にX_AUTH_TOKEN（Cookie）方式で動画を投稿する
"""
import os, sys, time, requests, json

AUTH_TOKEN = os.environ["X_AUTH_TOKEN"]

session = requests.Session()
session.headers.update({
    "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
    "cookie": f"auth_token={AUTH_TOKEN}",
    "x-twitter-auth-type": "OAuth2Session",
    "x-twitter-active-user": "yes",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
})

def get_csrf_token():
    resp = session.get("https://twitter.com/home")
    cookies = session.cookies.get_dict()
    ct0 = cookies.get("ct0", "")
    if ct0:
        session.headers["x-csrf-token"] = ct0
        session.headers["cookie"] = f"auth_token={AUTH_TOKEN}; ct0={ct0}"
    print(f"ct0: {ct0[:20] if ct0 else 'なし'}")
    return ct0

def upload_video_chunk(video_path):
    """v1.1 メディアアップロード"""
    file_size = os.path.getsize(video_path)
    print(f"動画サイズ: {file_size/1024/1024:.1f}MB")

    upload_session = requests.Session()
    upload_session.headers.update({
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "cookie": session.headers["cookie"],
        "x-csrf-token": session.headers.get("x-csrf-token", ""),
    })

    UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"

    # INIT
    resp = upload_session.post(UPLOAD_URL, data={
        "command": "INIT",
        "media_type": "video/mp4",
        "media_category": "tweet_video",
        "total_bytes": file_size,
    })
    print(f"INIT: {resp.status_code}")
    if resp.status_code != 202:
        print(resp.text[:300])
        return None
    media_id = resp.json()["media_id_string"]

    # APPEND
    chunk_size = 5 * 1024 * 1024
    segment = 0
    with open(video_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            resp = upload_session.post(UPLOAD_URL, data={
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": segment,
            }, files={"media": chunk})
            print(f"APPEND {segment}: {resp.status_code}")
            segment += 1

    # FINALIZE
    resp = upload_session.post(UPLOAD_URL, data={
        "command": "FINALIZE",
        "media_id": media_id,
    })
    print(f"FINALIZE: {resp.status_code}")
    data = resp.json()

    if "processing_info" in data:
        for _ in range(30):
            state = data["processing_info"]["state"]
            print(f"  状態: {state}")
            if state == "succeeded":
                break
            if state == "failed":
                return None
            time.sleep(5)
            resp = upload_session.get(UPLOAD_URL, params={"command": "STATUS", "media_id": media_id})
            data = resp.json()

    return media_id

def post_tweet(text, media_id=None):
    """GraphQL API でツイート投稿"""
    variables = {
        "tweet_text": text,
        "dark_request": False,
        "media": {"media_entities": [{"media_id": media_id, "tagged_users": []}], "possibly_sensitive": False} if media_id else None,
        "semantic_annotation_ids": [],
    }
    if not media_id:
        del variables["media"]

    resp = session.post(
        "https://twitter.com/i/api/graphql/SiM_cAu83R0wnrpmKDBnTg/CreateTweet",
        json={
            "variables": variables,
            "features": {
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
                "interactive_text_enabled": True,
                "responsive_web_text_conversations_enabled": False,
                "longform_notetweets_rich_text_read_enabled": True,
                "responsive_web_enhance_cards_enabled": False,
            },
            "queryId": "SiM_cAu83R0wnrpmKDBnTg",
        }
    )
    print(f"Tweet: {resp.status_code}")
    print(resp.text[:400])
    return resp.status_code == 200

def main():
    video_path = os.environ.get("VIDEO_PATH", "output.mp4")
    tweet_text = os.environ.get("TWEET_TEXT", "🤖 新しいAIツール紹介！ #AI #AIツール #人工知能 #Shorts")
    youtube_url = os.environ.get("YOUTUBE_URL", "")

    if youtube_url and youtube_url not in tweet_text:
        tweet_text += f"\n\n{youtube_url}"

    print("CSRF token取得中...")
    get_csrf_token()

    if os.path.exists(video_path):
        print(f"動画アップロード: {video_path}")
        media_id = upload_video_chunk(video_path)
    else:
        print("動画なし → テキストのみ投稿")
        media_id = None

    success = post_tweet(tweet_text, media_id)
    if success:
        print("✅ X投稿成功！")
    else:
        print("❌ X投稿失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
