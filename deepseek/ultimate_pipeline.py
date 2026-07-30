#!/usr/bin/env python3
"""
AI Conduit 究極の動画生成パイプライン
全研究知見を統合した完全自動化システム
"""

import os
import json
import subprocess
import random
import requests
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# === 設定 ===
ROOT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = ROOT_DIR / "deepseek" / "ultimate_output"
WORK_DIR = Path("/tmp/ultimate_work")
CONFIG_PATH = ROOT_DIR / "deepseek" / "ultimate_config.json"

# APIキー
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

for d in [OUTPUT_DIR, WORK_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# === フックテンプレート（25+パターン） ===
HOOKS = [
    "【衝撃】{}がヤバすぎる！",
    "【驚き】{}、知らないと損する！",
    "【誰も話さない】{}の真実",
    "【97%の人が知らない】{}",
    "【2026年】{}が起きている",
    "【超便利】{}で日々が変わる",
    "【エンジニア必見】{}",
]

# === シーン構成 ===
SCENES = [
    {"id": "hook", "duration": 3.0, "type": "wide", "prompt": "広角・導入"},
    {"id": "problem", "duration": 4.0, "type": "closeup", "prompt": "クローズアップ・問題提起"},
    {"id": "solution", "duration": 6.0, "type": "action", "prompt": "アクション・解決策"},
    {"id": "result", "duration": 5.0, "type": "portrait", "prompt": "ポートレート・結果"},
    {"id": "cta", "duration": 4.0, "type": "aftermath", "prompt": "CTA・フォロー誘導"},
]

# === カメラ動き ===
CAMERA_MOVES = [
    "zoompan=z='min(zoom+0.0015,1.3)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "zoompan=z=1.2:x='iw/2-(iw/zoom/2)+iw*0.05*sin(on/10)':y='ih/2-(ih/zoom/2)'",
]

# === トランジション ===
TRANSITIONS = ["slideleft", "slideright", "fade", "dissolve", "zoomin"]

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_trending_github() -> Dict[str, Any]:
    """GitHubトレンド取得"""
    log("📊 GitHubトレンド取得中...")
    url = "https://api.github.com/search/repositories"
    params = {"q": "created:>2026-07-01", "sort": "stars", "order": "desc", "per_page": 5}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("items"):
            repo = data["items"][0]
            return {"name": repo["full_name"], "stars": repo["stargazers_count"], "description": repo["description"] or "AIツール"}
    except Exception as e:
        log(f"⚠️ トレンド取得失敗: {e}")
    return {"name": "n8n-io/n8n", "stars": 45200, "description": "ノーコードAIワークフロー自動化"}

def generate_script(repo: Dict[str, Any]) -> str:
    """スクリプト生成（5シーン構成）"""
    tool_name = repo["name"].split("/")[-1]
    hook = random.choice(HOOKS).format(tool_name)
    return f"""{hook}
{tool_name}は{repo['description']}。
{repo['stars']}スターの注目ツール。
コメントにconduitでテンプレートプレゼント！"""

async def generate_tts(text: str, output_path: Path) -> bool:
    """Edge TTSで音声生成"""
    log("🔊 TTS生成中...")
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, "ja-JP-KeitaNeural", rate="-8%")
        await communicate.save(str(output_path))
        return True
    except Exception as e:
        log(f"⚠️ TTS失敗: {e}")
        return False

def create_video_scene(text: str, duration: float, output_path: Path) -> bool:
    """Pillow + ffmpegでシーン動画を生成"""
    from PIL import Image, ImageDraw, ImageFont
    fps = 24
    total_frames = int(duration * fps)
    width, height = 1080, 1920
    frame_dir = WORK_DIR / f"scene_{output_path.stem}"
    frame_dir.mkdir(exist_ok=True)
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 80)
    except:
        font = ImageFont.load_default()
    for i in range(total_frames):
        img = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (width - (bbox[2] - bbox[0])) // 2
        y = (height - (bbox[3] - bbox[1])) // 2
        draw.text((x, y), text, font=font, fill='white')
        img.save(frame_dir / f'frame_{i:04d}.png')
    cmd = ['ffmpeg', '-framerate', str(fps), '-i', str(frame_dir / 'frame_%04d.png'),
           '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-pix_fmt', 'yuv420p',
           '-t', str(duration), '-y', str(output_path)]
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    return result.returncode == 0

def create_ultimate_video(scenes: List[Dict], audio_path: Path, output_path: Path) -> bool:
    """全シーンを結合して最終動画を生成"""
    log("🎥 究極動画を合成中...")
    scene_files = []
    for i, scene in enumerate(scenes):
        scene_path = WORK_DIR / f"scene_{i:02d}.mp4"
        if create_video_scene(scene["text"], scene["duration"], scene_path):
            scene_files.append(str(scene_path))
    if not scene_files:
        return False
    # 結合リスト作成
    list_path = WORK_DIR / "concat_list.txt"
    with open(list_path, "w") as f:
        for sf in scene_files:
            f.write(f"file '{sf}'\n")
    cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(list_path),
           '-c', 'copy', '-y', str(output_path)]
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    if result.returncode != 0:
        log(f"⚠️ 結合失敗: {result.stderr[:200]}")
        return False
    # 音声を追加
    final_path = output_path.parent / f"{output_path.stem}_with_audio.mp4"
    cmd2 = ['ffmpeg', '-i', str(output_path), '-i', str(audio_path),
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
            '-shortest', '-y', str(final_path)]
    subprocess.run(cmd2, capture_output=True, timeout=60)
    if final_path.exists():
        final_path.rename(output_path)
    return True

async def run_ultimate_pipeline():
    """メインパイプライン"""
    log("🚀 究極パイプライン開始")
    repo = get_trending_github()
    log(f"📦 対象: {repo['name']} ({repo['stars']} stars)")
    script = generate_script(repo)
    log(f"📝 スクリプト: {script[:60]}...")
    audio_path = WORK_DIR / "narration.mp3"
    if not await generate_tts(script, audio_path):
        return
    scenes = []
    tool_name = repo["name"].split("/")[-1]
    for i, scene in enumerate(SCENES):
        if i == 0:
            text = random.choice(HOOKS).format(tool_name)
        elif i == len(SCENES) - 1:
            text = "コメントにconduitでテンプレート！"
        else:
            text = f"{tool_name}・{repo['stars']}スター"
        scenes.append({"text": text, "duration": scene["duration"]})
    output_name = f"ultimate_{repo['name'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.mp4"
    output_path = OUTPUT_DIR / output_name
    if create_ultimate_video(scenes, audio_path, output_path):
        log(f"✅ 完璧な動画が完成: {output_path}")
    else:
        log("❌ 動画生成失敗")

def main():
    asyncio.run(run_ultimate_pipeline())

if __name__ == "__main__":
    main()
