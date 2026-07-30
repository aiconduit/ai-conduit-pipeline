#!/usr/bin/env python3
"""
DeepSeek Video Pipeline for AI Conduit
GitHub Actions で動作する軽量動画生成パイプライン
"""

import os
import sys
import json
import subprocess
import argparse
import requests
import random
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "ds_output"
WORK_DIR = Path("/tmp/ds_work")
CONFIG_PATH = ROOT_DIR / "ds_config.json"

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

for d in [OUTPUT_DIR, WORK_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def log(msg: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    sys.stdout.flush()

def get_trending_github() -> Optional[Dict[str, Any]]:
    log("📊 GitHubトレンドを取得中...")
    url = "https://api.github.com/search/repositories"
    params = {
        "q": "created:>2026-07-01",
        "sort": "stars",
        "order": "desc",
        "per_page": 5
    }
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("items"):
            repo = data["items"][0]
            return {
                "name": repo["full_name"],
                "stars": repo["stargazers_count"],
                "description": repo["description"] or "AIツール",
                "url": repo["html_url"]
            }
    except Exception as e:
        log(f"⚠️ トレンド取得失敗: {e}")
    return {
        "name": "n8n-io/n8n",
        "stars": 45200,
        "description": "ノーコードAIワークフロー自動化ツール",
        "url": "https://github.com/n8n-io/n8n"
    }

def generate_script_with_deepseek(topic: str, repo_info: Dict[str, Any]) -> str:
    log(f"🤖 DeepSeekでスクリプト生成中... (トピック: {topic})")
    if not DEEPSEEK_API_KEY:
        log("⚠️ DEEPSEEK_API_KEYが設定されていません。テンプレートを使用します。")
        return generate_fallback_script(repo_info)
    prompt = f"""
あなたはAIツール紹介のショート動画スクリプトライターです。
以下のリポジトリを紹介する15〜20秒の日本語ナレーションスクリプトを作成してください。

リポジトリ: {repo_info['name']}
スター数: {repo_info['stars']}
説明: {repo_info['description']}

【フォーマット】
- フック（3秒）: 視聴者の興味を引く一言
- 内容（10秒）: ツールの特徴・メリット
- CTA（2秒）: 「conduit」コメントでテンプレートプレゼント
"""
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "あなたはプロの動画スクリプトライターです。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            },
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            script = data["choices"][0]["message"]["content"].strip()
            return script
        else:
            log(f"⚠️ APIエラー: {resp.status_code}")
    except Exception as e:
        log(f"⚠️ DeepSeek API失敗: {e}")
    return generate_fallback_script(repo_info)

def generate_fallback_script(repo_info: Dict[str, Any]) -> str:
    name = repo_info["name"].split("/")[-1]
    return f"""
{name}、AIで作業を自動化できるツールです。
{repo_info['stars']}スターを獲得している注目のオープンソース。
今すぐGitHubでチェックして、あなたの作業効率を上げましょう。
コメントに「conduit」でテンプレートプレゼント！
"""

def generate_tts(text: str, output_path: Path) -> bool:
    log("🔊 音声生成中...")
    try:
        cmd = [
            "edge-tts",
            "--text", text[:500],
            "--voice", "ja-JP-KeitaNeural",
            "--rate", "-8%",
            "--write-media", str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and output_path.exists():
            log(f"✅ 音声生成完了: {output_path}")
            return True
        else:
            log(f"⚠️ Edge-TTS失敗: {result.stderr[:200]}")
    except Exception as e:
        log(f"⚠️ TTS例外: {e}")
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=16000",
        "-t", "15", "-c:a", "aac", str(output_path)
    ], capture_output=True)
    return True

def download_pexels_video(query: str, output_path: Path) -> bool:
    log(f"🎬 Pexels B-roll取得中: {query}")
    if not PEXELS_API_KEY:
        log("⚠️ PEXELS_API_KEYが設定されていません。スキップします。")
        return False
    keywords = [
        "coding computer", "developer typing", "laptop screen code",
        "technology futuristic", "ai robot interface", "digital network"
    ]
    query = random.choice(keywords) if query == "auto" else query
    try:
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 5, "orientation": "portrait"}
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("videos"):
            video = data["videos"][0]
            for quality in ["hd", "sd", "small"]:
                for file in video.get("video_files", []):
                    if file.get("quality") == quality:
                        video_url = file["link"]
                        break
                else:
                    continue
                break
            else:
                video_url = video["video_files"][0]["link"]
            resp = requests.get(video_url, stream=True, timeout=30)
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            log(f"✅ B-roll取得完了: {output_path}")
            return True
    except Exception as e:
        log(f"⚠️ Pexels取得失敗: {e}")
    return False

def create_vertical_video(audio_path: Path, broll_path: Path, output_path: Path, duration: int = 15) -> bool:
    log("🎥 動画合成中...")
    if not broll_path.exists():
        log("⚠️ B-rollなし → テキスト動画を生成")
        cmd = [
            "ffmpeg", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:d={duration}",
            "-i", str(audio_path),
            "-vf", f"drawtext=text='AI Conduit':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-50",
            "-c:v", "libx264", "-c:a", "aac", "-shortest",
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        return result.returncode == 0
    cmd = [
        "ffmpeg", "-i", str(broll_path),
        "-i", str(audio_path),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-y", str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    if result.returncode != 0:
        log(f"⚠️ 動画合成失敗: {result.stderr[:300]}")
        return False
    log(f"✅ 動画生成完了: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="auto", help="生成トピック")
    args = parser.parse_args()
    log("🚀 DeepSeek Video Pipeline 開始")
    log(f"📁 出力先: {OUTPUT_DIR}")
    repo_info = get_trending_github()
    log(f"📦 対象リポジトリ: {repo_info['name']} ({repo_info['stars']} stars)")
    script = generate_script_with_deepseek(args.topic, repo_info)
    log(f"📝 スクリプト: {script[:100]}...")
    audio_path = WORK_DIR / "narration.mp3"
    generate_tts(script, audio_path)
    broll_path = WORK_DIR / "broll.mp4"
    if not download_pexels_video(args.topic, broll_path):
        broll_path = Path("/dev/null")
    output_name = f"ds_{repo_info['name'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.mp4"
    output_path = OUTPUT_DIR / output_name
    create_vertical_video(audio_path, broll_path, output_path, duration=18)
    info_path = OUTPUT_DIR / f"{output_path.stem}_info.json"
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump({
            "repo": repo_info,
            "script": script,
            "generated": datetime.now().isoformat(),
            "topic": args.topic
        }, f, ensure_ascii=False, indent=2)
    log(f"✅ パイプライン完了！出力: {output_path}")

if __name__ == "__main__":
    main()
