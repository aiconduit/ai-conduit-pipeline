#!/usr/bin/env python3
"""
generate_all_shorts.py
all_scripts.jsonから10本のShorts動画を生成
"""
import os, json, subprocess, sys
from pathlib import Path

def run_pipeline(script_data, output_path):
    """1本のShorts動画を生成"""
    Path("news_content_plan.json").write_text(
        json.dumps(script_data, ensure_ascii=False, indent=2))
    result = subprocess.run(
        ["python3", "run_from_news_plan.py"],
        capture_output=True, text=True, timeout=300,
        env={**os.environ}
    )
    # 出力ファイルを探してコピー
    import glob, shutil
    videos = sorted(glob.glob("projects/daily/renders/*.mp4"))
    if videos:
        shutil.copy(videos[-1], output_path)
        return True
    return False

def main():
    data = json.loads(Path("all_scripts.json").read_text())
    shorts = data.get("shorts", [])

    out_dir = Path("shorts_output")
    out_dir.mkdir(exist_ok=True)

    for i, script in enumerate(shorts[:10]):
        print(f"\nShorts {i+1}/10: {script.get('title','')[:40]}")
        out_path = out_dir / f"short_{i:02d}.mp4"
        try:
            success = run_pipeline(script, str(out_path))
            print(f"  {'✅' if success else '❌'} {out_path}")
        except Exception as e:
            print(f"  ❌ {e}")

    generated = len(list(out_dir.glob("*.mp4")))
    print(f"\n生成完了: {generated}/10本")

if __name__ == "__main__":
    main()
