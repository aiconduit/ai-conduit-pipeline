#!/usr/bin/env python3
"""
auto_comment_reply.py
AIがコメントを読んで自動返信する
- 新規コメントを検知
- Cerebras/DeepSeekで返信文生成
- YouTube APIで自動投稿
"""
import os, json, requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

def refresh_token(refresh, client_id, client_secret):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    return r.json().get("access_token", "") if r.status_code == 200 else ""

def get_recent_comments(access_token, max_results=20):
    """最新コメントを取得"""
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get("https://www.googleapis.com/youtube/v3/commentThreads",
        headers=headers,
        params={
            "part": "snippet,replies",
            "allThreadsRelatedToChannelId": "UCiI9p233ZTKO7BiO2yESbbA",
            "maxResults": max_results,
            "order": "time",
        }, timeout=10)
    if r.status_code != 200:
        print(f"コメント取得失敗: {r.status_code}")
        return []
    return r.json().get("items", [])

def already_replied(item):
    """すでに返信済みか確認"""
    replies = item.get("replies", {}).get("comments", [])
    for reply in replies:
        author = reply["snippet"]["authorDisplayName"]
        if "AI Conduit" in author or "aiconduit" in author.lower():
            return True
    return False

def is_recent(published_at, hours=24):
    """24時間以内のコメントか"""
    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - dt) < timedelta(hours=hours)

def generate_reply(comment_text, video_title, cerebras_key, deepseek_key):
    """AIで返信文を生成"""
    prompt = (
        f"あなたはAI Conduit（Claude Code専門YouTubeチャンネル）の中の人です。\n"
        f"視聴者のコメントに返信してください。\n\n"
        f"動画タイトル: {video_title}\n"
        f"コメント: {comment_text}\n\n"
        f"返信ルール:\n"
        f"- 50文字以内で簡潔に\n"
        f"- フレンドリーで自然な日本語\n"
        f"- 絵文字を1つ使う\n"
        f"- コメントの内容に具体的に反応する\n"
        f"- 「AI」コメントには「プレゼントを概要欄から受け取ってください」を追加\n"
        f"- スパム・荒らしには返信しない（空文字を返す）\n\n"
        f"返信文のみ出力（他のテキスト不要）:"
    )

    for key, url, model in [
        (cerebras_key, "https://api.cerebras.ai/v1/chat/completions", "gpt-oss-120b"),
        (deepseek_key, "https://api.deepseek.com/chat/completions", "deepseek-chat"),
    ]:
        if not key:
            continue
        try:
            r = requests.post(url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 100},
                timeout=20)
            if r.status_code == 200:
                reply = r.json()["choices"][0]["message"]["content"].strip()
                if reply and len(reply) > 3:
                    return reply[:100]
        except:
            continue
    return ""

def post_reply(access_token, parent_id, text):
    """返信を投稿"""
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    r = requests.post(
        "https://www.googleapis.com/youtube/v3/comments",
        headers=headers,
        params={"part": "snippet"},
        json={"snippet": {"parentId": parent_id, "textOriginal": text}},
        timeout=10)
    return r.status_code == 200

def get_video_title(access_token, video_id):
    """動画タイトルを取得"""
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get("https://www.googleapis.com/youtube/v3/videos",
        headers=headers,
        params={"part": "snippet", "id": video_id},
        timeout=10)
    if r.status_code == 200:
        items = r.json().get("items", [])
        if items:
            return items[0]["snippet"]["title"]
    return "Claude Code Tips"

def main():
    refresh_tok = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    cerebras_key = os.environ.get("CEREBRAS_API_KEY", "")
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")

    access_token = refresh_token(refresh_tok, client_id, client_secret)
    if not access_token:
        print("認証失敗")
        return

    print("✅ 認証完了")
    comments = get_recent_comments(access_token)
    print(f"コメント数: {len(comments)}")

    replied = 0
    skipped = 0

    for item in comments:
        thread_id = item["id"]
        top = item["snippet"]["topLevelComment"]
        published_at = top["snippet"]["publishedAt"]
        comment_text = top["snippet"]["textDisplay"]
        video_id = top["snippet"]["videoId"]

        # 24時間以内のコメントのみ
        if not is_recent(published_at, hours=48):
            continue

        # すでに返信済みはスキップ
        if already_replied(item):
            skipped += 1
            continue

        # 自分自身のコメントはスキップ
        author = top["snippet"]["authorDisplayName"]
        if "AI Conduit" in author or "conduit" in author.lower():
            skipped += 1
            continue

        video_title = get_video_title(access_token, video_id)
        print(f"\nコメント: {comment_text[:50]}")

        reply_text = generate_reply(comment_text, video_title, cerebras_key, deepseek_key)

        if not reply_text:
            print(f"  → スキップ（スパム or 生成失敗）")
            skipped += 1
            continue

        success = post_reply(access_token, thread_id, reply_text)
        if success:
            print(f"  → 返信: {reply_text}")
            replied += 1
        else:
            print(f"  → 返信失敗")

        # レート制限対策
        import time
        time.sleep(2)

    print(f"\n完了: {replied}件返信 / {skipped}件スキップ")

    # ログ保存
    Path("logs").mkdir(exist_ok=True)
    log = {"timestamp": datetime.now().isoformat(), "replied": replied, "skipped": skipped}
    Path(f"logs/comment_reply_{datetime.now().strftime('%Y%m%d')}.json").write_text(
        json.dumps(log, ensure_ascii=False))

if __name__ == "__main__":
    main()
