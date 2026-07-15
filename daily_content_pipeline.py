#!/usr/bin/env python3
"""
Daily GitHub-trending content pipeline for AI Conduit (Phase 1).

Takes a small JSON config (hook / terminal steps / KPI numbers / narration text)
and produces a narrated 1080p vertical-ready MP4 using OpenMontage's zero-key
Remotion renderer + macOS `say` for narration.

Usage:
    python3 daily_content_pipeline.py configs/my_topic.json

Config schema (see configs/_example.json):
{
  "name": "codex-plugin-cc",
  "hook_text": "...",
  "hook_subtitle": "...",
  "terminal_title": "...",
  "prompt": "$",
  "steps": [
    {"kind": "cmd", "text": "npm install ..."},
    {"kind": "out", "text": "..."},
    {"kind": "pause", "seconds": 0.4},
    {"kind": "pill", "text": "...", "color": "#22D3EE", "durationSeconds": 2}
  ],
  "kpi_title": "本日のGitHubトレンド",
  "kpi_data": [
    {"label": "順位", "value": 1, "change": 0, "suffix": "位"}
  ],
  "narration_text": "..."
}
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
COMPOSER_DIR = ROOT_DIR / "remotion-composer"
PROPS_DIR = COMPOSER_DIR / "public" / "demo-props"
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
NARRATION_DIR = Path("/tmp/narration")

DEFAULT_BG = "#0B0F1A"
DEFAULT_ACCENT = "#22D3EE"


def build_props(cfg: dict) -> dict:
    hook_seconds = 3
    terminal_seconds = cfg.get("terminal_seconds", 13)
    kpi_seconds = cfg.get("kpi_seconds", 6)
    t1 = hook_seconds
    t2 = t1 + terminal_seconds
    t3 = t2 + kpi_seconds

    cuts = [
        {
            "id": "hook",
            "source": "",
            "type": "hero_title",
            "in_seconds": 0,
            "out_seconds": t1,
            "text": cfg["hook_text"],
            "subtitle": cfg.get("hook_subtitle", ""),
            "backgroundColor": DEFAULT_BG,
        },
        {
            "id": "terminal-demo",
            "source": "",
            "type": "terminal_scene",
            "in_seconds": t1,
            "out_seconds": t2,
            "terminalTitle": cfg.get("terminal_title", "Terminal"),
            "prompt": cfg.get("prompt", "$"),
            "accentColor": cfg.get("accentColor", DEFAULT_ACCENT),
            "backgroundColor": DEFAULT_BG,
            "steps": cfg["steps"],
        },
        {
            "id": "kpis",
            "source": "",
            "type": "kpi_grid",
            "in_seconds": t2,
            "out_seconds": t3,
            "title": cfg.get("kpi_title", ""),
            "chartData": cfg.get("kpi_data", []),
            "columns": len(cfg.get("kpi_data", [])) or 3,
            "chartColors": ["#22D3EE", "#34D399", "#F59E0B"],
            "chartAnimation": "cascade",
            "backgroundColor": DEFAULT_BG,
        },
    ]
    return {"theme": "flat-motion-graphics", "cuts": cuts, "overlays": []}


def render_video(name: str, props: dict) -> Path:
    PROPS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    props_path = PROPS_DIR / f"{name}.json"
    with props_path.open("w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    output_path = OUTPUT_DIR / f"{name}.mp4"
    print(f"[1/3] Rendering video -> {output_path}")
    subprocess.run(
        [
            "npx", "remotion", "render", "src/index.tsx", "Explainer",
            str(output_path), "--props", str(props_path), "--codec", "h264",
        ],
        cwd=COMPOSER_DIR,
        check=True,
    )
    return output_path


def make_narration(name: str, text: str, rate: int = 195, voice: str = "ja-JP-KeitaNeural") -> Path:
    NARRATION_DIR.mkdir(parents=True, exist_ok=True)
    mp3_path = NARRATION_DIR / f"{name}.mp3"
    print(f"[2/3] Generating narration (Edge-TTS: {voice}) -> {mp3_path}")
    subprocess.run(
        ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(mp3_path)],
        check=True,
    )
    return mp3_path


def mux(video_path: Path, audio_path: Path, name: str) -> Path:
    final_path = OUTPUT_DIR / f"{name}_narrated.mp4"
    print(f"[3/3] Muxing narration into video -> {final_path}")
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(video_path), "-i", str(audio_path),
            "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest",
            str(final_path),
        ],
        check=True,
    )
    return final_path


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 daily_content_pipeline.py <config.json>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    name = cfg["name"]

    props = build_props(cfg)
    video_path = render_video(name, props)

    if cfg.get("narration_text"):
        audio_path = make_narration(name, cfg["narration_text"], cfg.get("say_rate", 195), cfg.get("say_voice", "ja-JP-KeitaNeural"))
        final_path = mux(video_path, audio_path, name)
        print(f"\nDone: {final_path}")
    else:
        print(f"\nDone (no narration): {video_path}")


if __name__ == "__main__":
    main()
