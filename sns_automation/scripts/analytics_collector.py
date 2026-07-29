#!/usr/bin/env python3
"""毎日のYouTubeアナリティクス自動収集"""
import os, json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

def collect_analytics():
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON", "")
    if token_json:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(token_json)
            f.flush()
            creds = Credentials.from_authorized_user_file(f.name,
                ["https://www.googleapis.com/auth/youtube.readonly"])
    else:
        return

    if creds.expired: creds.refresh(Request())
    youtube = build("youtube", "v3", credentials=creds)

    ch = youtube.channels().list(part="statistics", mine=True).execute()
    stats = ch["items"][0]["statistics"]

    search = youtube.search().list(part="snippet", forMine=True, type="video", maxResults=50).execute()
    video_ids = [item["id"]["videoId"] for item in search["items"]]
    videos = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids)).execute()

    total_views = sum(int(v["statistics"].get("viewCount", 0)) for v in videos["items"])
    top_videos = sorted(videos["items"], key=lambda x: int(x["statistics"].get("viewCount", 0)), reverse=True)[:5]

    report = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "subscribers": int(stats.get("subscriberCount", 0)),
        "total_views": total_views,
        "video_count": int(stats.get("videoCount", 0)),
        "top_videos": [
            {
                "title": v["snippet"]["title"][:40],
                "views": int(v["statistics"].get("viewCount", 0)),
                "likes": int(v["statistics"].get("likeCount", 0))
            } for v in top_videos
        ]
    }

    os.makedirs("output", exist_ok=True)
    
    # 今日のレポート
    log_file = f"output/analytics_{datetime.now().strftime('%Y%m%d')}.json"
    with open(log_file, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 累積ログ
    history_file = "output/analytics_history.json"
    history = []
    if os.path.exists(history_file):
        with open(history_file) as f:
            history = json.load(f)
    history.append(report)
    history = history[-90:]  # 90日分保持
    with open(history_file, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"=== {report['date']} ===")
    print(f"登録者: {report['subscribers']}人")
    print(f"総再生数: {report['total_views']:,}回")
    print(f"動画数: {report['video_count']}本")
    for v in report["top_videos"][:3]:
        print(f"  {v['views']:,}回 | {v['title']}")

if __name__ == "__main__":
    collect_analytics()
