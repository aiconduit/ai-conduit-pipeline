#!/usr/bin/env python3
"""
optimize_post_time.py
アナリティクスから最適投稿時間を算出してワークフローを自動更新
"""
import os, json, requests
from datetime import datetime, timezone
from pathlib import Path

def refresh_token(refresh, client_id, client_secret):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    return r.json().get("access_token", "") if r.status_code == 200 else ""

def get_audience_activity(access_token):
    """視聴者のアクティブ時間帯を取得"""
    headers = {"Authorization": f"Bearer {access_token}"}
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start_date = "2026-01-01"

    r = requests.get("https://youtubeanalytics.googleapis.com/v2/reports",
        headers=headers,
        params={
            "ids": "channel==MINE",
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "views",
            "dimensions": "day",
        }, timeout=15)

    if r.status_code == 200:
        return r.json().get("rows", [])
    print(f"アナリティクス取得失敗: {r.status_code}")
    return []

def calculate_best_time(rows):
    """曜日・時間帯から最適投稿時間を算出（JST）"""
    # データが少ない場合はデフォルト
    if len(rows) < 7:
        return {"hour": 20, "cron": "0 11 * * *", "reason": "デフォルト（20:00 JST）"}

    # 曜日別集計（簡易版）
    weekday_views = {i: 0 for i in range(7)}
    for row in rows:
        date_str = row[0]
        views = row[1]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday_views[dt.weekday()] += views

    best_weekday = max(weekday_views, key=weekday_views.get)
    weekday_names = ["月", "火", "水", "木", "金", "土", "日"]

    # 視聴者の多い時間帯は平日19-21時、休日18-22時が一般的（日本）
    if best_weekday < 5:  # 平日
        best_hour_jst = 20
    else:  # 週末
        best_hour_jst = 19

    best_hour_utc = (best_hour_jst - 9) % 24

    return {
        "hour_jst": best_hour_jst,
        "hour_utc": best_hour_utc,
        "best_weekday": weekday_names[best_weekday],
        "cron": f"0 {best_hour_utc} * * *",
        "reason": f"{weekday_names[best_weekday]}曜日が最多再生・{best_hour_jst}:00 JSTに投稿"
    }

def update_workflow_schedule(cron_expr, gh_token):
    """GitHub Actionsのスケジュールを自動更新"""
    headers = {"Authorization": f"token {gh_token}", "Content-Type": "application/json"}

    r = requests.get(
        "https://api.github.com/repos/aiconduit/ai-conduit-pipeline/contents/.github/workflows/autonomous_agent.yml",
        headers=headers, timeout=10)
    if r.status_code != 200:
        print("ワークフロー取得失敗")
        return False

    import base64
    sha = r.json()["sha"]
    content = base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")

    # cronを更新
    import re
    old_cron = re.search(r'cron: "([^"]+)"', content)
    if old_cron:
        old_expr = old_cron.group(1)
        new_content = content.replace(f'cron: "{old_expr}"', f'cron: "{cron_expr}"')
        encoded = base64.b64encode(new_content.encode()).decode()
        r2 = requests.put(
            "https://api.github.com/repos/aiconduit/ai-conduit-pipeline/contents/.github/workflows/autonomous_agent.yml",
            headers=headers,
            json={"message": f"Auto: 投稿時間最適化 → {cron_expr}", "content": encoded, "sha": sha})
        return r2.status_code == 200
    return False

def main():
    refresh_tok = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    gh_token = os.environ.get("GITHUB_TOKEN", "")

    access_token = refresh_token(refresh_tok, client_id, client_secret)
    if not access_token:
        print("認証失敗")
        return

    rows = get_audience_activity(access_token)
    best = calculate_best_time(rows)

    print(f"最適投稿時間: {best}")

    # ワークフロー更新
    if gh_token and best.get("cron"):
        success = update_workflow_schedule(best["cron"], gh_token)
        print(f"ワークフロー更新: {'✅' if success else '❌'}")

    Path("logs").mkdir(exist_ok=True)
    Path("logs/optimal_time.json").write_text(
        json.dumps(best, ensure_ascii=False, indent=2))
    print(f"✅ 最適時間: {best.get('hour_jst', 20)}:00 JST")

if __name__ == "__main__":
    main()
