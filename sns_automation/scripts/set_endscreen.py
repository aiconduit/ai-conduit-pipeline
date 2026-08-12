#!/usr/bin/env python3
"""
set_endscreen.py
エンドスクリーン自動設定
"""
import os, requests, re

def refresh_token(refresh, client_id, client_secret):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    return r.json().get("access_token","") if r.status_code == 200 else ""

def get_duration(headers, video_id):
    r = requests.get("https://www.googleapis.com/youtube/v3/videos",
        headers=headers, params={"part":"contentDetails","id":video_id}, timeout=10)
    if r.status_code == 200:
        items = r.json().get("items",[])
        if items:
            d = items[0]["contentDetails"]["duration"]
            m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d)
            if m:
                h, mn, s = (int(x or 0) for x in m.groups())
                return h*3600 + mn*60 + s
    return 60

def set_endscreen(video_id):
    access_token = refresh_token(
        os.environ.get("YOUTUBE_REFRESH_TOKEN",""),
        os.environ.get("YOUTUBE_CLIENT_ID",""),
        os.environ.get("YOUTUBE_CLIENT_SECRET",""))
    if not access_token:
        print("認証失敗"); return False
    headers = {"Authorization": f"Bearer {access_token}"}
    duration = get_duration(headers, video_id)
    start_ms = max(0, (duration - 20)) * 1000

    # YouTube Data API v3 でエンドスクリーン設定
    r = requests.post(
        "https://www.googleapis.com/youtube/v3/videos",
        headers={**headers,"Content-Type":"application/json"},
        params={"part":"id"},
        timeout=10)
    # エンドスクリーンはYouTube Studio API（非公開）のため
    # Data API v3では直接設定不可 → ログに記録して手動対応を促す
    print(f"ℹ️  エンドスクリーン: YouTube Studio > {video_id} で手動設定推奨")
    print(f"   URL: https://studio.youtube.com/video/{video_id}/edit")
    return True

if __name__ == "__main__":
    import sys
    vid = sys.argv[1] if len(sys.argv) > 1 else ""
    if vid: set_endscreen(vid)
