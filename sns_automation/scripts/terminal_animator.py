#!/usr/bin/env python3
"""
ターミナルアニメーション生成システム
Claude Codeのコマンド・コードをタイピングアニメーションで表示するMP4を生成
"""
import subprocess, os, sys, json, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1080, 1920
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

def get_mono_font(size=38):
    for p in FONT_PATHS:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def make_terminal_frame(lines_so_far: list, cursor_visible: bool = True, title: str = "") -> Image.Image:
    """ターミナル風フレームを生成"""
    img = Image.new("RGB", (WIDTH, HEIGHT), (15, 15, 20))  # ダーク背景
    draw = ImageDraw.Draw(img)
    
    # ターミナルヘッダーバー
    draw.rectangle([(0, 0), (WIDTH, 80)], fill=(35, 35, 40))
    draw.ellipse([(20, 25), (50, 55)], fill=(255, 95, 86))   # 赤ボタン
    draw.ellipse([(65, 25), (95, 55)], fill=(255, 189, 46))  # 黄ボタン
    draw.ellipse([(110, 25), (140, 55)], fill=(39, 201, 63)) # 緑ボタン
    
    # ターミナルタイトル
    title_font = get_mono_font(28)
    draw.text((WIDTH//2 - 100, 22), "Claude Code Terminal", font=title_font, fill=(180, 180, 180))
    
    # プロンプト行とコード
    code_font = get_mono_font(36)
    small_font = get_mono_font(28)
    
    y = 120
    for line in lines_so_far:
        if line.startswith("$ "):
            # コマンド行
            draw.text((40, y), "$ ", font=code_font, fill=(100, 255, 100))
            draw.text((100, y), line[2:], font=code_font, fill=(255, 255, 255))
        elif line.startswith("# "):
            # コメント行
            draw.text((40, y), line, font=small_font, fill=(120, 180, 120))
        elif line.startswith("---") or line.startswith("name:") or line.startswith("description:") or line.startswith("disallowed"):
            # YAMLフロントマター
            draw.text((40, y), line, font=code_font, fill=(100, 200, 255))
        else:
            # 出力・通常テキスト
            draw.text((40, y), line, font=code_font, fill=(220, 220, 220))
        y += 55
        if y > HEIGHT - 200:
            break
    
    # カーソル
    if cursor_visible:
        draw.rectangle([(40, y), (60, y + 40)], fill=(100, 255, 100))
    
    # AI Conduitブランドバー（下部）
    draw.rectangle([(0, HEIGHT - 80), (WIDTH, HEIGHT)], fill=(0, 120, 215))
    brand_font = get_mono_font(30)
    draw.text((30, HEIGHT - 60), "AI Conduit | Claude Code Tips", font=brand_font, fill=(255, 255, 255))
    
    return img

def generate_typing_animation(command_lines: list, output_path: str, duration: float = 5.0, title: str = "") -> str:
    """タイピングアニメーションMP4を生成"""
    import tempfile, os
    
    fps = 30
    total_frames = int(duration * fps)
    
    # 全テキストを結合
    full_text = "\n".join(command_lines)
    total_chars = sum(len(l) for l in command_lines)
    
    # フレームを一時ディレクトリに保存
    with tempfile.TemporaryDirectory() as tmpdir:
        frame_paths = []
        
        # タイピングアニメーション
        chars_per_frame = max(1, total_chars // (total_frames * 0.7))
        current_chars = 0
        
        for frame_idx in range(total_frames):
            # タイピング進捗
            progress = frame_idx / (total_frames * 0.7)
            current_chars = min(total_chars, int(progress * total_chars))
            
            # 現在表示する行を計算
            display_lines = []
            remaining = current_chars
            for line in command_lines:
                if remaining <= 0:
                    break
                display_lines.append(line[:remaining])
                remaining -= len(line)
            
            # カーソル点滅（0.5秒ごと）
            cursor = (frame_idx // 15) % 2 == 0
            
            frame = make_terminal_frame(display_lines, cursor_visible=cursor, title=title)
            
            frame_path = os.path.join(tmpdir, f"frame_{frame_idx:05d}.png")
            frame.save(frame_path)
            frame_paths.append(frame_path)
        
        # FFmpegでMP4生成
        result = subprocess.run([
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(tmpdir, "frame_%05d.png"),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1920",
            output_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr[-200:]}")
            return ""
    
    size = Path(output_path).stat().st_size // 1024
    print(f"✅ ターミナルアニメーション: {output_path} ({size}KB, {duration:.1f}s)")
    return output_path

def extract_commands_from_narration(narration: str) -> list:
    """ナレーションからコマンド・コードを抽出"""
    import re
    lines = []
    
    # よく使うClaude Codeコマンドパターン
    patterns = [
        r'\$\s+claude[^\n,。]+',           # $ claude ...
        r'/[a-z][a-z-]+[^\n,。]*',           # /command
        r'\.claude/[\w/.-]+',               # .claude/path
        r'disallowedTools:[^\n,。]+',         # YAML fields
        r'name:[^\n,。]+',
        r'description:[^\n,。]+',
        r'npx [^\n,。]+',
        r'---',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, narration)
        for m in matches:
            m = m.strip()
            if len(m) > 2 and m not in lines:
                if not m.startswith('$'):
                    m = '$ ' + m if m.startswith('claude') or m.startswith('npx') else m
                lines.append(m)
    
    if not lines:
        # コマンドが見つからない場合はナレーションをそのまま表示
        lines = ["# " + narration[:50]]
    
    return lines[:6]

if __name__ == "__main__":
    # テスト
    test_commands = [
        "$ claude",
        "/loop 5m /babysit",
        "# 5分ごとに自動でコードを修正",
        "$ /loop 30m /slack-feedback",
    ]
    generate_typing_animation(test_commands, "/tmp/test_terminal.mp4", duration=5.0)
    print("テスト完了")
