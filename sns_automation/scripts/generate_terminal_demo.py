#!/usr/bin/env python3
"""
台本の内容に合わせてClaude Codeターミナルデモ動画を自動生成
asciinema + agg + ffmpeg を使用
"""
import os, sys, json, subprocess, tempfile, re
from pathlib import Path

def generate_terminal_demo(plan: dict, output_path: str, duration: int = 20):
    """台本からターミナルデモ動画を生成"""
    
    title = plan.get("selected_title", "Claude Code設定")
    scenes = plan.get("scenes", plan.get("script", {}).get("scenes", []))
    
    # シーンからコマンド・操作内容を抽出
    hook = scenes[0].get("narration", "") if scenes else ""
    step1 = scenes[3].get("caption", scenes[3].get("narration", "")) if len(scenes) > 3 else ""
    step2 = scenes[4].get("caption", scenes[4].get("narration", "")) if len(scenes) > 4 else ""
    result = scenes[5].get("narration", "") if len(scenes) > 5 else ""
    
    # ターミナルデモスクリプト生成
    demo_script = f"""#!/bin/bash
# Claude Code Demo
sleep 0.5
echo "╔══════════════════════════════════════════════╗"
echo "║  Claude Code  v2.1  │  claude-haiku-4-5     ║"
echo "╚══════════════════════════════════════════════╝"
sleep 0.5
echo ""
echo "\\$ claude"
sleep 1
echo ""
echo "  > {hook[:50]}"
sleep 1.5
echo ""
echo "  Claude Code 処理中..."
sleep 1
echo "  ✓ 設定ファイルを確認"
sleep 0.5
echo "  ✓ {step1[:45]}"
sleep 1
echo "  ✓ {step2[:45]}"
sleep 1
echo ""
echo "  ┌─────────────────────────────────────┐"
echo "  │  完了！                              │"
echo "  │  {result[:35]}   │"
echo "  └─────────────────────────────────────┘"
sleep 2
echo ""
echo "  \\$ _"
sleep 2
"""
    
    # 一時ファイルに書き出し
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(demo_script)
        script_path = f.name
    os.chmod(script_path, 0o755)
    
    cast_path = output_path.replace('.mp4', '.cast')
    gif_path = output_path.replace('.mp4', '.gif')
    
    try:
        # asciinema録画
        subprocess.run([
            "asciinema", "rec",
            "--command", f"bash {script_path}",
            "--cols", "70", "--rows", "20",
            "--overwrite", cast_path
        ], check=True, capture_output=True)
        
        # aggでGIF変換
        agg_path = "/usr/local/bin/agg"
        if not os.path.exists(agg_path):
            agg_path = "/tmp/agg"
        
        subprocess.run([
            agg_path,
            "--theme", "monokai",
            "--font-size", "20",
            "--cols", "70", "--rows", "20",
            cast_path, gif_path
        ], check=True, capture_output=True)
        
        # ffmpegで縦型MP4に変換
        subprocess.run([
            "ffmpeg", "-y", "-i", gif_path,
            "-vf", "scale=1080:-2:flags=lanczos,pad=1080:960:(ow-iw)/2:(oh-ih)/2:color=black",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-t", str(duration),
            output_path
        ], check=True, capture_output=True)
        
        print(f"✅ ターミナルデモ動画生成完了: {output_path}")
        return True
        
    except Exception as e:
        print(f"⚠️ ターミナルデモ生成失敗: {e}")
        return False
    finally:
        os.unlink(script_path)

if __name__ == "__main__":
    # テスト実行
    test_plan = {
        "selected_title": "Claude CodeのdisallowedToolsで安全自動化",
        "scenes": [
            {"narration": "disallowedToolsでエージェントの誤操作を防げます", "mood": "hook"},
            {"narration": "Why", "mood": "value"},
            {"narration": "Solution", "mood": "value"},
            {"narration": "設定完了", "caption": "reviewer.mdを作成します", "mood": "value"},
            {"narration": "手順2", "caption": "disallowedTools: Write, Edit を記述", "mood": "value"},
            {"narration": "手動確認が不要になります", "mood": "value"},
            {"narration": "CTA", "mood": "cta"},
        ]
    }
    generate_terminal_demo(test_plan, "/tmp/test_demo.mp4")
