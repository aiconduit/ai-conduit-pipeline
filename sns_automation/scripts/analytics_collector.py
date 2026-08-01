#!/usr/bin/env python3
"""
YouTube Analytics自動収集スクリプト
投稿済み動画の再生数・CTR・視聴維持率を毎日収集してJSONに保存
"""
import os
import json
import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).parent.parent.parent
ANALYTICS_DIR = BASE_DIR / "analytics"
ANALYTICS_DIR.mkdir(exist_ok=True)
ANALYTICS_JSON = ANALYTICS_DIR / "analytics_history.json"
VIDEO_LOG_JSON = BASE_DIR / "output" / "auto_log.json"

def get_youtube_client():
    token_data = json.loads(os.environ["YOUTUBE_TOKEN_JSON"])
    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
    )
    return build("youtube", "v3", credentials=creds)

def get_analytics_client():
    token_data = json.loads(os.environ["YOUTUBE_TOKEN_JSON"])
    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
    )
    return build("youtubeAnalytics", "v2", credentials=creds)

def get_video_stats(youtube, video_ids):
    """動画の基本統計を取得"""
    if not video_ids:
        return {}
    response = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(video_ids)
    ).execute()
    stats = {}
    for item in response.get("items", []):
        vid = item["id"]
        s = item["statistics"]
        stats[vid] = {
            "title": item["snippet"]["title"],
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0)),
            "published_at": item["snippet"]["publishedAt"],
        }
    return stats

def get_analytics_stats(analytics, video_id, start_date, end_date):
    """CTR・視聴維持率・インプレッションを取得"""
    try:
        response = analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,impressions,impressionClickThroughRate",
            dimensions="video",
            filters=f"video=={video_id}",
        ).execute()
        rows = response.get("rows", [])
        if rows:
            row = rows[0]
            return {
                "views": int(row[1]),
                "watch_minutes": float(row[2]),
                "avg_view_duration_sec": float(row[3]),
                "avg_view_percentage": float(row[4]),
                "impressions": int(row[5]),
                "ctr": float(row[6]),
            }
    except Exception as e:
        print(f"   ⚠️ Analytics取得失敗 ({video_id}): {e}")
    return {}

def load_history():
    if ANALYTICS_JSON.exists():
        with open(ANALYTICS_JSON) as f:
            return json.load(f)
    return {}

def save_history(data):
    with open(ANALYTICS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_video_log():
    """投稿済み動画IDリストを取得"""
    video_ids = []
    if VIDEO_LOG_JSON.exists():
        with open(VIDEO_LOG_JSON) as f:
            log = json.load(f)
        if isinstance(log, list):
            for entry in log:
                vid = entry.get("video_id")
                if vid:
                    video_ids.append(vid)
        elif isinstance(log, dict):
            vid = log.get("video_id")
            if vid:
                video_ids.append(vid)
    return video_ids

def generate_improvement_report(history):
    """改善提案レポートを生成"""
    report = []
    report.append("# AI Conduit アナリティクスレポート")
    report.append(f"生成日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    if not history:
        report.append("データなし")
        return "\n".join(report)

    # 平均CTRと視聴維持率
    ctrs = [v.get("ctr", 0) for v in history.values() if "ctr" in v]
    retentions = [v.get("avg_view_percentage", 0) for v in history.values() if "avg_view_percentage" in v]
    views_list = [v.get("views", 0) for v in history.values()]

    if ctrs:
        avg_ctr = sum(ctrs) / len(ctrs)
        report.append(f"## 平均CTR: {avg_ctr:.1f}%")
        if avg_ctr < 3:
            report.append("⚠️ CTRが低い → サムネイル改善が必要")
        elif avg_ctr < 6:
            report.append("△ CTRは普通 → サムネイルの数字・テキストを強化")
        else:
            report.append("✅ CTRは良好")

    if retentions:
        avg_retention = sum(retentions) / len(retentions)
        report.append(f"## 平均視聴維持率: {avg_retention:.1f}%")
        if avg_retention < 30:
            report.append("⚠️ 視聴維持率が低い → フックを強化・動画を短くする")
        elif avg_retention < 50:
            report.append("△ 視聴維持率は普通 → 中盤のクリフハンガーを追加")
        else:
            report.append("✅ 視聴維持率は良好")

    # トップ動画
    if views_list:
        sorted_videos = sorted(history.items(), key=lambda x: x[1].get("views", 0), reverse=True)
        report.append("\n## トップ動画（再生数順）")
        for vid, data in sorted_videos[:5]:
            title = data.get("title", vid)[:30]
            views = data.get("views", 0)
            ctr = data.get("ctr", 0)
            retention = data.get("avg_view_percentage", 0)
            report.append(f"- {title}: {views}再生 / CTR {ctr:.1f}% / 維持率 {retention:.1f}%")

    return "\n".join(report)

def main():
    print("📊 YouTube Analytics収集開始...")
    today = datetime.date.today().strftime("%Y-%m-%d")
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    youtube = get_youtube_client()
    analytics = get_analytics_client()
    history = load_history()
    video_ids = load_video_log()

    if not video_ids:
        print("   ⚠️ 投稿済み動画IDが見つかりません")
        return

    print(f"   対象動画: {len(video_ids)}件")

    # 基本統計取得
    stats = get_video_stats(youtube, video_ids)
    for vid, data in stats.items():
        if vid not in history:
            history[vid] = {}
        history[vid].update(data)
        history[vid]["last_updated"] = today

        # Analytics取得
        analytics_data = get_analytics_stats(analytics, vid, week_ago, today)
        if analytics_data:
            history[vid].update(analytics_data)
        print(f"   ✅ {data['title'][:30]}: {data['views']}再生")

    save_history(history)

    # 改善レポート生成
    report = generate_improvement_report(history)
    report_path = ANALYTICS_DIR / f"report_{today}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n📝 レポート: {report_path}")
    print(report)

if __name__ == "__main__":
    main()
