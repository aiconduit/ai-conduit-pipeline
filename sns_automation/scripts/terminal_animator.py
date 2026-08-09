#!/usr/bin/env python3
"""
ターミナルアニメーション生成（高速FFmpeg版）
PillowフレームではなくFFmpegのdrawtextフィルターを使用
"""
import subprocess, os, re
from pathlib import Path

def extract_commands_from_narration(narration: str) -> list:
    """ナレーションからコマンド・コードを抽出"""
    lines = []
    patterns = [
        r'\$\s+[a-z][^。、\n]+',
        r'/[a-z][a-z0-9-]+[^。、\n]*',
        r'\.claude/[\w/.-]+',
        r'disallowedTools:[^。、\n]+',
        r'name:[^。、\n]+',
        r'description:[^。、\n]+',
        r'npx [^。、\n]+',
        r'git [^。、\n]+',
        r'cd [^。、\n]+',
    ]
    for pattern in patterns:
        for m in re.findall(pattern, narration):
            m = m.strip()
            if len(m) > 2 and m not in lines:
                lines.append(m)
    if not lines:
        # コマンドなし→ナレーションの要点を表示
        words = narration.replace('。','').replace('、','')[:40]
        lines = [words]
    return lines[:4]

def generate_typing_animation(command_lines: list, output_path: str, duration: float = 5.0, title: str = "") -> str:
    """FFmpeg drawtextでターミナルアニメーション生成（高速版）"""
    
    # 背景色：ダークターミナル
    bg_color = "0x0F0F14"
    text_color = "0x64FF64"  # 緑
    cmd_color = "0xFFFFFF"  # 白
    
    # 全コマンドを結合したテキスト
    display_text = "\n".join(command_lines)
    
    # 特殊文字をエスケープ
    def esc(s):
        return s.replace("'", "\'").replace(":", "\:").replace("[", "\[").replace("]", "\]")
    
    # FFmpegコマンド（drawtextフィルターで直接描画）
    drawtext_filters = []
    
    # ヘッダーバー
    drawtext_filters.append("drawbox=x=0:y=0:w=iw:h=80:color=0x232328:t=fill")
    
    # ドット装飾
    drawtext_filters.append("drawbox=x=20:y=25:w=30:h=30:color=0xFF5F56:t=fill")
    drawtext_filters.append("drawbox=x=65:y=25:w=30:h=30:color=0xFFBD2E:t=fill")
    drawtext_filters.append("drawbox=x=110:y=25:w=30:h=30:color=0x27C93F:t=fill")
    
    # タイトルテキスト
    drawtext_filters.append(f"drawtext=text='Claude Code Terminal':x=(w-tw)/2:y=25:fontcolor=0xB4B4B4:fontsize=28")
    
    # コマンドテキスト（各行）
    y_pos = 130
    for i, cmd in enumerate(command_lines):
        safe_cmd = esc(cmd[:45])  # 長さ制限
        if cmd.startswith("$") or cmd.startswith("git") or cmd.startswith("npx") or cmd.startswith("cd"):
            # コマンド行（$ プレフィックス付き）
            drawtext_filters.append(f"drawtext=text='\$ {safe_cmd}':x=40:y={y_pos}:fontcolor=0x64FF64:fontsize=36:enable='gte(t,{i*0.8})'")
        elif cmd.startswith("/"):
            # スラッシュコマンド
            drawtext_filters.append(f"drawtext=text='{safe_cmd}':x=40:y={y_pos}:fontcolor=0x64C8FF:fontsize=36:enable='gte(t,{i*0.8})'")
        elif ":" in cmd:
            # YAMLフィールド
            drawtext_filters.append(f"drawtext=text='{safe_cmd}':x=40:y={y_pos}:fontcolor=0x64C8FF:fontsize=36:enable='gte(t,{i*0.8})'")
        else:
            drawtext_filters.append(f"drawtext=text='{safe_cmd}':x=40:y={y_pos}:fontcolor=0xDCDCDC:fontsize=34:enable='gte(t,{i*0.8})'")
        y_pos += 70
    
    # ブランドバー
    drawtext_filters.append("drawbox=x=0:y=ih-80:w=iw:h=80:color=0x0078D7:t=fill")
    drawtext_filters.append("drawtext=text='AI Conduit | Claude Code Tips':x=30:y=ih-58:fontcolor=white:fontsize=28")
    
    vf = ",".join(drawtext_filters)
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={bg_color}:s=1080x1920:r=30:d={duration}",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr[-300:]}")
        return ""
    
    size = Path(output_path).stat().st_size // 1024
    print(f"✅ ターミナルアニメーション(高速): {output_path} ({size}KB, {duration:.1f}s)")
    return output_path

if __name__ == "__main__":
    test_cmds = ["$ git clone https://github.com/anthropics/anthropic-quickstarts", "$ cd financial-data-analyst", ".env にAPIキーを設定"]
    generate_typing_animation(test_cmds, "/tmp/test_fast_terminal.mp4", duration=5.0)
    print("テスト完了")
