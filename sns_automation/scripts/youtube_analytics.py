#!/usr/bin/env python3
"""
AI Conduit YouTube Analytics 自動分析システム
毎朝実行して動画パフォーマンスをDeepSeekで分析
"""
import os, json, requests
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-71eab12699f047a5891e62268c66c241")

def get_youtube_clients():
    """YouTube Data API + Analytics APIの両方を取得"""
    import tempfile
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON", "").strip()
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    
    if token_json:
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                f.write(token_json); f.flush()
                creds = Credentials.from_authorized_user_file(f.name,
                    scopes=[
                        "https://www.googleapis.com/auth/youtube.readonly",
                        "https://www.googleapis.com/auth/yt-analytics.readonly",
                    ])
        except: creds = None
    else:
        creds = None
    
    if creds is None:
        creds = Credentials(token=None, refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id, client_secret=client_secret,
            scopes=[
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/yt-analytics.readonly",
            ])
    
    if not creds.valid:
        creds.refresh(Request())
    
    yt = build("youtube", "v3", credentials=creds)
    yta = build("youtubeAnalytics", "v2", credentials=creds)
    return yt, yta

def get_recent_videos(yt, max_results=30):
    """最近の動画一覧を取得"""
    r = yt.search().list(
        part="snippet",
        forMine=True,
        type="video",
        order="date",
        maxResults=max_results
    ).execute()
    
    videos = []
    for item in r.get("items", []):
        videos.append({
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "published": item["snippet"]["publishedAt"][:10],
        })
    return videos

def get_video_analytics(yta, video_ids, days=7):
    """動画のアナリティクスデータを取得"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    video_filter = ",".join([f"video=={vid}" for vid in video_ids[:10]])
    
    try:
        r = yta.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,subscribersGained",
            dimensions="video",
            filters=f"video=={','.join(video_ids[:10])}",
            sort="-views",
            maxResults=20
        ).execute()
        return r
    except Exception as e:
        print(f"Analytics API error: {e}")
        return None

def analyze_with_deepseek(videos_data):
    """DeepSeekで動画パフォーマンスを分析"""
    prompt = f"""あなたはYouTube Shortsの専門アナリストです。
以下のAI Conduitチャンネルの動画パフォーマンスデータを分析してください。

{json.dumps(videos_data, ensure_ascii=False, indent=2)}

以下を日本語で分析してください：

1. **ベスト動画TOP3**: なぜ伸びたか（タイトル・フック・内容の観点から）
2. **最低動画**: なぜ伸びなかったか
3. **完了率分析**: 75%を超えている動画の共通点
4. **離脱パターン**: どのシーンタイプで離脱が多いか
5. **明日からの改善アクション**: 具体的に3つ
6. **次に作るべき動画**: タイトル案を3つ

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
        yt, yta = get_youtube_clients()
        print("✅ YouTube API接続成功")
    except Exception as e:
        print(f"❌ API接続失敗: {e}")
        return
    
    # 最近の動画を取得
    videos = get_recent_videos(yt, max_results=20)
    print(f"✅ 動画取得: {len(videos)}本")
    
    if not videos:
        print("動画が見つかりません")
        return
    
    video_ids = [v["id"] for v in videos]
    
    # アナリティクスデータ取得
    analytics = get_video_analytics(yta, video_ids, days=30)
    
    # データを統合
    videos_data = {
        "取得日": datetime.now().strftime("%Y-%m-%d"),
        "動画数": len(videos),
        "動画一覧": videos[:10],
        "アナリティクス": analytics,
    }
    
    # レポート保存
    report_path = f"analytics/report_{datetime.now().strftime('%Y%m%d')}.json"
    import os; os.makedirs("analytics", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(videos_data, f, ensure_ascii=False, indent=2)
    print(f"✅ データ保存: {report_path}")
    
    # DeepSeek分析
    print("\n=== DeepSeek AI分析 ===")
    analysis = analyze_with_deepseek(videos_data)
    print(analysis)
    
    # 分析レポート保存
    analysis_path = f"analytics/analysis_{datetime.now().strftime('%Y%m%d')}.md"
    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write(f"# AI Conduit アナリティクス分析\n")
        f.write(f"日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(analysis)
    print(f"\n✅ 分析レポート保存: {analysis_path}")

if __name__ == "__main__":
    main()
