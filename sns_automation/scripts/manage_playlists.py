#!/usr/bin/env python3
"""
manage_playlists.py
再生リスト自動管理
"""
import os, requests

def refresh_token(refresh, client_id, client_secret):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    return r.json().get("access_token","") if r.status_code == 200 else ""

def get_or_create_playlist(headers, title, desc=""):
    r = requests.get("https://www.googleapis.com/youtube/v3/playlists",
        headers=headers,
        params={"part":"snippet","mine":True,"maxResults":50}, timeout=10)
    if r.status_code == 200:
        for pl in r.json().get("items",[]):
            if pl["snippet"]["title"] == title:
                return pl["id"]
    r2 = requests.post(
        "https://www.googleapis.com/youtube/v3/playlists",
        headers={**headers,"Content-Type":"application/json"},
        params={"part":"snippet,status"},
        json={"snippet":{"title":title,"description":desc},"status":{"privacyStatus":"public"}},
        timeout=10)
    if r2.status_code == 200:
        pid = r2.json()["id"]
        print(f"✅ 再生リスト作成: {title}")
        return pid
    return None

def add_to_playlist(headers, playlist_id, video_id):
    r = requests.post(
        "https://www.googleapis.com/youtube/v3/playlistItems",
        headers={**headers,"Content-Type":"application/json"},
        params={"part":"snippet"},
        json={"snippet":{"playlistId":playlist_id,"resourceId":{"kind":"youtube#video","videoId":video_id}}},
        timeout=10)
    return r.status_code == 200

def main(short_video_ids=None, longform_video_id=None):
    access_token = refresh_token(
        os.environ.get("YOUTUBE_REFRESH_TOKEN",""),
        os.environ.get("YOUTUBE_CLIENT_ID",""),
        os.environ.get("YOUTUBE_CLIENT_SECRET",""))
    if not access_token:
        print("認証失敗"); return
    headers = {"Authorization": f"Bearer {access_token}"}

    shorts_pl = get_or_create_playlist(headers,
        "Claude Code Tips【毎日更新】",
        "Claude Codeの使い方を毎日45秒で解説。すぐ使えるテンプレート付き。")
    longform_pl = get_or_create_playlist(headers,
        "Claude Code 完全解説【1時間シリーズ】",
        "Claude Codeの機能を毎日1時間でまとめて解説。")

    if short_video_ids and shorts_pl:
        for vid in short_video_ids:
            ok = add_to_playlist(headers, shorts_pl, vid)
            print(f"  {'✅' if ok else '❌'} Shorts追加: {vid}")
    if longform_video_id and longform_pl:
        ok = add_to_playlist(headers, longform_pl, longform_video_id)
        print(f"  {'✅' if ok else '❌'} 長尺追加: {longform_video_id}")

if __name__ == "__main__":
    main()
