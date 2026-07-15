#!/usr/bin/env python3
"""
Pexels動画ダウンローダー
GitHubトレンド紹介コンテンツ用のB-roll素材を自動取得

使い方:
    python3 pexels_downloader.py "programming code terminal" --orientation portrait
"""
import sys
import json
import os
import requests
import random
from pathlib import Path

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
CACHE_DIR = Path(__file__).parent / "assets" / "pexels_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# GitHubトレンド紹介でよく使うキーワードセット
TECH_KEYWORDS = {
    "coding": ["programmer coding laptop", "software developer terminal", "code screen dark"],
    "ai": ["artificial intelligence technology", "robot technology futuristic", "data visualization neon"],
    "github": ["open source collaboration", "developer team coding", "keyboard typing fast"],
    "startup": ["startup office modern", "entrepreneur working laptop", "team meeting tech"],
    "terminal": ["black screen terminal command", "hacker screen green", "computer screen dark night"],
    "data": ["data visualization charts", "big data processing", "server room technology"],
}

def search_video(query: str, orientation: str = "portrait", per_page: int = 5) -> list:
    if not PEXELS_API_KEY:
        print("ERROR: PEXELS_API_KEY not set")
        return []
    
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page, "orientation": orientation, "size": "medium"}
    
    try:
        r = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            # フォールバック: クエリを簡略化
            simple = query.split()[-1]
            if simple != query:
                print(f"  ⚠️ Retrying with '{simple}'...")
                return search_video(simple, orientation, per_page)
            return []
        data = r.json()
        return data.get("videos", [])
    except Exception as e:
        print(f"  ERROR: {e}")
        return []

def download_video(url: str, filename: str) -> Path:
    save_path = CACHE_DIR / filename
    if save_path.exists():
        print(f"  ✅ Cached: {filename}")
        return save_path
    
    print(f"  ⬇️  Downloading: {filename}...")
    r = requests.get(url, stream=True, timeout=30)
    with open(save_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  ✅ Saved: {save_path}")
    return save_path

def get_best_video_url(video: dict) -> str:
    files = sorted(video.get("video_files", []), key=lambda x: x["width"] * x["height"], reverse=True)
    return files[0]["link"] if files else ""

def fetch_broll(query: str, count: int = 2, orientation: str = "portrait") -> list[Path]:
    """クエリでPexels動画を検索してダウンロード、パスのリストを返す"""
    print(f"🔍 Searching Pexels: '{query}' ({orientation})...")
    videos = search_video(query, orientation)
    if not videos:
        print(f"  ⚠️ No results for '{query}'")
        return []
    
    valid = [v for v in videos if v.get("duration", 0) >= 4]
    selected = random.sample(valid, min(count, len(valid))) if valid else []
    
    paths = []
    for i, video in enumerate(selected):
        url = get_best_video_url(video)
        if url:
            safe_query = query.replace(" ", "_")[:30]
            filename = f"{safe_query}_{video['id']}.mp4"
            path = download_video(url, filename)
            paths.append(path)
    return paths

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "programmer coding laptop"
    orientation = "portrait"
    paths = fetch_broll(query, count=2, orientation=orientation)
    for p in paths:
        print(p)
