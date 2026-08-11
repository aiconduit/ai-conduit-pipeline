#!/usr/bin/env python3
"""
analytics_collector.py
YouTubeアナリティクスを収集して自動改善パラメータを更新
"""
import os, json, requests
from datetime import datetime, timedelta
from pathlib import Path

def get_youtube_analytics(video_id: str, access_token: str) -> dict:
    """YouTubeアナリティクスAPI呼び出し"""
    headers = {"Authorization": f"Bearer {access_token}"}
    end_date = datetime.utcnow().strftime("%Y-%m-%d")
    start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    r = requests.get(
        "https://youtubeanalytics.googleapis.com/v2/reports",
        headers=headers,
        params={
            "ids": "channel==MINE",
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "views,estimatedMinutesWatched,averageViewPercentage,likes,comments,shares,subscribersGained",
            "filters": f"video=={video_id}",
            "dimensions": "video",
        }, timeout=15)
    
    if r.status_code == 200:
        data = r.json()
        rows = data.get("rows", [])
        if rows:
            cols = [c["name"] for c in data.get("columnHeaders", [])]
            return dict(zip(cols, rows[0]))
    return {}

def refresh_access_token(refresh_token: str, client_id: str, client_secret: str) -> str:
    """アクセストークン更新"""
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    if r.status_code == 200:
        return r.json().get("access_token", "")
    return ""

def auto_improve(metrics: dict, params_file: str = "auto_improvement_params.json") -> dict:
    """メトリクスに基づいて次回パラメータを自動改善"""
    
    # 現在のパラメータ読み込み
    params = {}
    if Path(params_file).exists():
        params = json.loads(Path(params_file).read_text())
    
    improvements = []
    views = metrics.get("views", 0)
    retention = metrics.get("averageViewPercentage", 0)
    ctr = metrics.get("clickThroughRate", 0)
    likes = metrics.get("likes", 0)
    
    print(f"\n📊 パフォーマンス:")
    print(f"  再生数: {views}")
    print(f"  視聴維持率: {retention:.1f}%")
    print(f"  いいね: {likes}")
    
    # 自動改善ロジック
    if retention < 75:
        params["target_duration_sec"] = max(30, params.get("target_duration_sec", 50) - 5)
        improvements.append(f"視聴維持率低({retention:.1f}%)→尺{params['target_duration_sec']}秒に短縮")
    elif retention >= 85:
        params["target_duration_sec"] = min(55, params.get("target_duration_sec", 50) + 3)
        improvements.append(f"視聴維持率高({retention:.1f}%)→尺を少し延長")
    
    if views < 200:
        params["hook_style"] = "number_shock"
        improvements.append("再生数低→数字フックに変更")
    elif views >= 1000:
        params["hook_style"] = "keep_current"
        improvements.append(f"再生数優秀({views})→現状維持")
    
    if likes > 0 and views > 0:
        like_rate = likes / views * 100
        if like_rate > 5:
            params["content_type"] = "tutorial"
            improvements.append(f"いいね率高({like_rate:.1f}%)→チュートリアル系を増やす")
    
    if improvements:
        Path(params_file).write_text(json.dumps(params, ensure_ascii=False, indent=2))
        print(f"\n🔧 自動改善 ({len(improvements)}件):")
        for imp in improvements:
            print(f"  ✓ {imp}")
    else:
        print("\n✅ 改善不要（パフォーマンス良好）")
    
    return params

def main():
    # 環境変数から認証情報取得
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    
    # 最新動画IDを取得
    video_log = Path("/tmp/latest_video.json")
    if not video_log.exists():
        video_log = Path("logs/latest_video.json")
    
    if not video_log.exists():
        print("⚠️ 動画IDログなし")
        return
    
    video_data = json.loads(video_log.read_text())
    video_id = video_data.get("video_id", "")
    
    if not video_id:
        print("⚠️ 動画IDなし")
        return
    
    print(f"分析対象: {video_id}")
    
    # アクセストークン更新
    access_token = refresh_access_token(refresh_token, client_id, client_secret)
    if not access_token:
        print("⚠️ トークン更新失敗")
        return
    
    # メトリクス取得
    metrics = get_youtube_analytics(video_id, access_token)
    if not metrics:
        print("⚠️ メトリクス取得失敗（まだ集計中の可能性）")
        return
    
    # 自動改善
    improved_params = auto_improve(metrics)
    
    # レポート保存
    Path("logs").mkdir(exist_ok=True)
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "video_id": video_id,
        "metrics": metrics,
        "improvements": improved_params,
    }
    date_str = datetime.utcnow().strftime("%Y%m%d")
    Path(f"logs/analytics_{date_str}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n✅ レポート保存: logs/analytics_{date_str}.json")

if __name__ == "__main__":
    main()
