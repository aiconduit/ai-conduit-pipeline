#!/usr/bin/env python3
"""
AI Conduit YouTube Analytics 自動分析
YouTube Data API v3（既存トークンで動作）
"""
import os, json, requests, tempfile
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-71eab12699f047a5891e62268c66c241")

def get_youtube():
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON", "").strip()
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    
    if token_json:
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                f.write(token_json); f.flush()
                creds = Credentials.from_authorized_user_file(f.name,
                    scopes=["https://www.googleapis.com/auth/youtube.readonly"])
        except: creds = None
    else: creds = None
    
    if creds is None:
        creds = Credentials(token=None, refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id, client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.readonly"])
    
    if not creds.valid:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def get_recent_videos(yt, max_results=30):
    """最近の動画一覧と統計を取得"""
    # チャンネルID取得
    ch = yt.channels().list(part="id,statistics", mine=True).execute()
    channel_id = ch["items"][0]["id"]
    ch_stats = ch["items"][0]["statistics"]
    print(f"チャンネル統計: 動画{ch_stats.get('videoCount')}本 / 登録者{ch_stats.get('subscriberCount')}人")
    
    # 最近の動画検索
    search = yt.search().list(
        part="snippet", forMine=True, type="video",
        order="date", maxResults=max_results
    ).execute()
    
    video_ids = [item["id"]["videoId"] for item in search.get("items", [])]
    
    if not video_ids:
        return [], ch_stats
    
    # 動画の統計情報取得
    videos_resp = yt.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids[:20])
    ).execute()
    
    videos = []
    for item in videos_resp.get("items", []):
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})
        videos.append({
            "id": item["id"],
            "title": snippet.get("title", ""),
            "published": snippet.get("publishedAt", "")[:10],
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "duration": item.get("contentDetails", {}).get("duration", ""),
        })
    
    # 再生数でソート
    videos.sort(key=lambda x: x["views"], reverse=True)
    return videos, ch_stats

def analyze_with_deepseek(videos, ch_stats):
    """DeepSeekで分析"""
    top5 = videos[:5]
    bottom5 = videos[-5:] if len(videos) > 5 else []
    
    data_str = f"""
チャンネル統計:
- 総動画数: {ch_stats.get('videoCount')}
- 登録者数: {ch_stats.get('subscriberCount')}
- 総再生数: {ch_stats.get('viewCount')}

上位5動画:
{json.dumps(top5, ensure_ascii=False, indent=2)}

下位5動画:
{json.dumps(bottom5, ensure_ascii=False, indent=2)}

全{len(videos)}本の平均再生数: {sum(v['views'] for v in videos) // max(len(videos),1)}
"""
    
    prompt = f"""AI Conduit YouTubeチャンネルの動画パフォーマンスを分析してください。

{data_str}

以下を日本語で分析してください：

## 1. ベスト動画の共通点
（タイトルパターン・フック・数字の使い方）

## 2. 低パフォーマンス動画の問題点

## 3. タイトルパターン分析
（どのタイトル形式が最も再生される？）

## 4. 明日からの改善アクション（具体的に3つ）

## 5. 次に作るべき動画タイトル案（3つ）

数字を使って具体的に分析してください。"""

    r = requests.post("https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
        json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
              "max_tokens": 1500, "temperature": 0.3}, timeout=60)
    return r.json()["choices"][0]["message"]["content"]

def main():
    print("=== AI Conduit YouTube Analytics 分析 ===")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    try:
        yt = get_youtube()
        print("✅ YouTube API接続成功")
    except Exception as e:
        print(f"❌ API接続失敗: {e}")
        return
    
    videos, ch_stats = get_recent_videos(yt, max_results=30)
    print(f"✅ 動画取得: {len(videos)}本")
    
    if not videos:
        print("動画なし")
        return
    
    print("\nTop5動画:")
    for v in videos[:5]:
        print(f"  {v['views']:,}再生 | {v['title'][:40]}")
    
    # 保存
    import os
    os.makedirs("analytics", exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    
    data_path = f"analytics/data_{date_str}.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump({"date": date_str, "channel": ch_stats, "videos": videos}, f, ensure_ascii=False, indent=2)
    print(f"✅ データ保存: {data_path}")
    
    # DeepSeek分析
    print("\n=== DeepSeek AI分析中... ===")
    analysis = analyze_with_deepseek(videos, ch_stats)
    print(analysis)
    
    analysis_path = f"analytics/analysis_{date_str}.md"
    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write(f"# AI Conduit Analytics\n日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(analysis)
    print(f"\n✅ 分析レポート: {analysis_path}")

if __name__ == "__main__":
    main()
