#!/usr/bin/env python3
"""
パイプライン3 HyperFramesビデオエンジン
パイプライン2の台本・TTSを受け取り、HyperFramesでHTML→MP4生成
"""
import os, json, subprocess, tempfile, shutil
from pathlib import Path

WORK_DIR = Path("/tmp/pipeline3_work")
W, H = 1080, 1920

def _run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)

def probe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 4.0

def generate_scene_html(scene: dict, idx: int, total: int, audio_dur: float) -> str:
    """シーン情報からHyperFrames用HTMLを生成"""
    title = scene.get("title", "value")
    narration = scene.get("narration", "")
    caption = scene.get("caption", "")
    mood = scene.get("mood", "value")
    
    # ムード別カラースキーム
    colors = {
        "hook":  {"bg": "#0a0a0f", "accent": "#FF4500", "text": "#ffffff"},
        "value": {"bg": "#080818", "accent": "#3b82f6", "text": "#ffffff"},
        "cta":   {"bg": "#0a0f0a", "accent": "#22c55e", "text": "#ffffff"},
    }
    c = colors.get(mood, colors["value"])
    
    # 進捗バー
    progress_pct = int((idx / total) * 100)
    
    # アニメーション時間（音声長さに合わせる）
    dur = max(audio_dur, 2.0)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  width: {W}px; height: {H}px;
  background: {c['bg']};
  overflow: hidden; font-family: 'Noto Sans JP', sans-serif;
}}
.progress-bar {{
  position: absolute; top: 0; left: 0;
  height: 8px; width: {progress_pct}%;
  background: {c['accent']};
}}
.scene-label {{
  position: absolute; top: 30px; right: 40px;
  color: {c['accent']}; font-size: 40px; font-weight: bold;
  opacity: 0.7;
}}
.main-content {{
  position: absolute; top: 200px; left: 60px; right: 60px;
  display: flex; flex-direction: column; gap: 40px;
}}
.scene-title {{
  font-size: 55px; color: {c['accent']}; font-weight: 900;
  opacity: 0; transform: translateY(30px);
}}
.narration {{
  font-size: 75px; color: {c['text']}; font-weight: bold;
  line-height: 1.3; opacity: 0; transform: translateY(30px);
}}
.caption-box {{
  background: rgba(255,255,255,0.05);
  border: 2px solid {c['accent']};
  border-radius: 20px; padding: 30px;
  font-size: 55px; color: {c['accent']};
  opacity: 0; transform: translateY(30px);
}}
.bottom-accent {{
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 8px; background: {c['accent']};
}}
.channel-name {{
  position: absolute; bottom: 30px; left: 0; right: 0;
  text-align: center; color: rgba(255,255,255,0.4);
  font-size: 38px;
}}
</style>
</head>
<body>
<div data-composition-id="scene_{idx:02d}" data-width="{W}" data-height="{H}" data-duration="{dur:.1f}">
  <div class="progress-bar"></div>
  <div class="scene-label">{idx+1}/{total}</div>
  <div class="main-content">
    <div class="scene-title">{caption or title}</div>
    <div class="narration">{narration}</div>
    {"<div class='caption-box'>" + caption + "</div>" if caption and caption != title else ""}
  </div>
  <div class="bottom-accent"></div>
  <div class="channel-name">AI Conduit</div>
</div>
<script>
const tl = gsap.timeline();
tl.to('.scene-title', {{ opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }}, 0.2)
  .to('.narration', {{ opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }}, 0.5)
  .to('.caption-box', {{ opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }}, 0.9);
window.__timelines = window.__timelines || {{}};
window.__timelines['scene_{idx:02d}'] = tl;
</script>
</body>
</html>"""
    return html

def render_scene_html(html_content: str, scene_id: str, audio_path: str) -> str:
    """HTMLをHyperFramesでMP4にレンダリングして音声と合成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    # HTMLファイル保存
    proj_dir = WORK_DIR / f"proj_{scene_id}"
    proj_dir.mkdir(exist_ok=True)
    html_path = proj_dir / "index.html"
    html_path.write_text(html_content, encoding="utf-8")
    
    # HyperFramesでレンダリング
    video_path = str(WORK_DIR / f"scene_{scene_id}_silent.mp4")
    r = subprocess.run(
        ["hyperframes", "render", str(proj_dir), "-o", video_path],
        capture_output=True, text=True, timeout=180
    )
    
    if not os.path.exists(video_path):
        print(f"  ⚠️ HyperFrames失敗: {r.stderr[:100]}")
        return None
    
    # 音声と合成
    final_path = str(WORK_DIR / f"scene_{scene_id}.mp4")
    _run(["ffmpeg", "-y", "-i", video_path, "-i", audio_path,
          "-c:v", "libx264", "-c:a", "aac", "-shortest",
          "-pix_fmt", "yuv420p", final_path])
    
    return final_path if os.path.exists(final_path) else None

def generate_video(plan: dict, audio_files: list, ass_files: list = None) -> str:
    """パイプライン3メイン動画生成"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    scenes = plan.get("scenes", [])
    total = len(scenes)
    scene_videos = []
    
    for i, (scene, audio_path) in enumerate(zip(scenes, audio_files)):
        if not os.path.exists(audio_path):
            continue
        
        dur = probe_dur(audio_path)
        html = generate_scene_html(scene, i, total, dur)
        
        print(f"  Scene {i+1}/{total}: {scene.get('title','?')} ({dur:.1f}秒)")
        video = render_scene_html(html, f"{i:02d}", audio_path)
        
        if video:
            scene_videos.append(video)
            print(f"    ✅ 生成完了")
        else:
            print(f"    ❌ 失敗")
    
    if not scene_videos:
        raise Exception("シーン動画が生成されませんでした")
    
    # 全シーン結合
    concat_file = str(WORK_DIR / "concat.txt")
    with open(concat_file, "w") as f:
        for sv in scene_videos:
            f.write(f"file '{sv}'\n")
    
    output = str(WORK_DIR / "pipeline3_final.mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
          "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
          "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-c:a", "aac", "-pix_fmt", "yuv420p", output])
    
    return output

if __name__ == "__main__":
    print("✅ hyperframes_engine.py loaded")
