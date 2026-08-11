#!/usr/bin/env python3
"""
auto_private.py
パフォーマンス不足の動画を自動で非公開にする
基準:
  - 投稿24時間後: 視聴維持率 < 60% → 非公開
  - 投稿72時間後: 再生数 < 100 → 非公開
  - 投稿7日後: 累計再生数 < 300 → 非公開
"""
import os, json, requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

def refresh_token(refresh_token, client_id, client_secret):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    if r.status_code == 200:
        return r.json().get("access_token", "")
    print(f"トークン更新失敗: {r.status_code} {r.text[:100]}")
    return ""

def get_channel_videos(access_token, max_results=50):
    """チャンネルの動画一覧を取得"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # チャンネルID取得
    r = requests.get("https://www.googleapis.com/youtube/v3/channels",
        headers=headers,
        params={"part": "id,statistics", "mine": True},
        timeout=10)
    if r.status_code != 200:
        print(f"チャンネル取得失敗: {r.status_code}")
        return []
    
    channel_id = r.json().get("items", [{}])[0].get("id", "")
    if not channel_id:
        return []
    
    # 動画一覧取得
    r2 = requests.get("https://www.googleapis.com/youtube/v3/search",
        headers=headers,
        params={
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "maxResults": max_results,
        }, timeout=10)
    
    if r2.status_code != 200:
        print(f"動画一覧取得失敗: {r2.status_code}")
        return []
    
    videos = []
    for item in r2.json().get("items", []):
        video_id = item["id"]["videoId"]
        published_at = item["snippet"]["publishedAt"]
        title = item["snippet"]["title"]
        videos.append({
            "id": video_id,
            "title": title,
            "published_at": published_at,
        })
    return videos

def get_video_stats(access_token, video_ids):
    """動画の統計情報を取得"""
    headers = {"Authorization": f"Bearer {access_token}"}
    ids_str = ",".join(video_ids)
    r = requests.get("https://www.googleapis.com/youtube/v3/videos",
        headers=headers,
        params={"part": "statistics,status", "id": ids_str},
        timeout=10)
    if r.status_code != 200:
        return {}
    stats = {}
    for item in r.json().get("items", []):
        vid_id = item["id"]
        stats[vid_id] = {
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "status": item["status"]["privacyStatus"],
        }
    return stats

def get_video_retention(access_token, video_id):
    """視聴維持率を取得"""
    headers = {"Authorization": f"Bearer {access_token}"}
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    
    r = requests.get("https://youtubeanalytics.googleapis.com/v2/reports",
        headers=headers,
        params={
            "ids": "channel==MINE",
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "averageViewPercentage,views",
            "filters": f"video=={video_id}",
            "dimensions": "video",
        }, timeout=10)
    
    if r.status_code == 200:
        rows = r.json().get("rows", [])
        if rows:
            return {"retention": rows[0][1], "views": rows[0][2]}
    return {"retention": None, "views": 0}

def set_video_private(access_token, video_id, reason):
    """動画を非公開に変更"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    r = requests.put(
        "https://www.googleapis.com/youtube/v3/videos",
        headers=headers,
        params={"part": "status"},
        json={"id": video_id, "status": {"privacyStatus": "private"}},
        timeout=10)
    
    if r.status_code == 200:
        print(f"  ✅ 非公開: {video_id} ({reason})")
        return True
    else:
        print(f"  ❌ 非公開失敗: {r.status_code} {r.text[:100]}")
        return False

def main():
    # 認証
    refresh_tok = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    
    if not all([refresh_tok, client_id, client_secret]):
        print("認証情報不足")
        return
    
    access_token = refresh_token(refresh_tok, client_id, client_secret)
    if not access_token:
        return
    
    print("✅ 認証完了")
    
    # 動画一覧取得
    videos = get_channel_videos(access_token, max_results=30)
    print(f"動画数: {len(videos)}本")
    
    # 統計取得
    video_ids = [v["id"] for v in videos]
    if not video_ids:
        return
    
    stats = get_video_stats(access_token, video_ids[:50])
    
    now = datetime.now(timezone.utc)
    results = []
    private_count = 0
    
    for video in videos:
        vid_id = video["id"]
        title = video["title"][:40]
        published = datetime.fromisoformat(video["published_at"].replace("Z", "+00:00"))
        age_hours = (now - published).total_seconds() / 3600
        
        stat = stats.get(vid_id, {})
        views = stat.get("views", 0)
        status = stat.get("status", "")
        
        # すでに非公開はスキップ
        if status == "private":
            continue
        
        print(f"\n[{age_hours:.0f}h] {title}")
        print(f"  再生数: {views} ステータス: {status}")
        
        reason = None
        
        # 24時間後チェック: 維持率
        if 24 <= age_hours < 96:
            retention_data = get_video_retention(access_token, vid_id)
            retention = retention_data.get("retention")
            if retention is not None:
                print(f"  維持率: {retention:.1f}%")
                if retention < 60:
                    reason = f"維持率{retention:.1f}%<60%"
        
        # 72時間後チェック: 再生数
        if age_hours >= 72 and views < 100:
            reason = f"72h後再生数{views}<100"
        
        # 7日後チェック: 累計
        if age_hours >= 168 and views < 300:
            reason = f"7日後累計{views}<300"
        
        if reason:
            set_video_private(access_token, vid_id, reason)
            private_count += 1
            results.append({
                "video_id": vid_id,
                "title": title,
                "views": views,
                "age_hours": age_hours,
                "reason": reason,
                "action": "private",
            })
        else:
            print(f"  → 公開維持")
    
    print(f"\n📊 結果: {private_count}本を非公開に変更")
    
    # ログ保存
    Path("logs").mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    log_path = f"logs/auto_private_{date_str}.json"
    Path(log_path).write_text(
        json.dumps({"timestamp": now.isoformat(), "results": results},
                   ensure_ascii=False, indent=2))
    print(f"✅ ログ: {log_path}")

if __name__ == "__main__":
    main()
