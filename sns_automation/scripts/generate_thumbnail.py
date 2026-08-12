#!/usr/bin/env python3
"""
generate_thumbnail.py
サムネイル自動生成 - 数字必須・A/Bテスト対応
"""
import subprocess, re, sys
from pathlib import Path
from datetime import datetime

def extract_number(title):
    nums = re.findall(r'\d+', title)
    return nums[0] if nums else "10"

def generate_thumbnail(title, output_path, style="auto"):
    num = extract_number(title)
    day = datetime.now().day
    if style == "auto":
        style = "dark" if day % 2 == 0 else "accent"
    if style == "dark":
        bg, accent, text_c, sub_c = "0x0a0a14", "0xFFD700", "white", "0xaaaaaa"
    else:
        bg, accent, text_c, sub_c = "0x1a1a2e", "0xFF6B35", "white", "0xdddddd"

    safe_title = title[:18].replace("'","").replace(":","").replace("#","").replace("!","")
    vf = (
        f"drawbox=x=0:y=0:w=iw:h=ih:color={bg}:t=fill,"
        f"drawbox=x=0:y=0:w=12:h=ih:color={accent}:t=fill,"
        f"drawtext=text='{num}':x=60:y=50:fontsize=280:fontcolor={accent}:borderw=8:bordercolor=black:alpha=0.12,"
        f"drawtext=text='Claude Code':x=60:y=80:fontsize=80:fontcolor={accent}:borderw=4:bordercolor=black,"
        f"drawtext=text='Tips':x=60:y=180:fontsize=130:fontcolor={text_c}:borderw=5:bordercolor=black,"
        f"drawtext=text='{safe_title}':x=60:y=340:fontsize=46:fontcolor={sub_c}:borderw=2:bordercolor=black,"
        f"drawbox=x=60:y=430:w=380:h=68:color={accent}:t=fill,"
        f"drawtext=text='FREE TEMPLATE':x=78:y=448:fontsize=38:fontcolor=black,"
        f"drawbox=x=1050:y=28:w=200:h=58:color=0xFF4444:t=fill,"
        f"drawtext=text='2026':x=1078:y=44:fontsize=40:fontcolor=white:borderw=2:bordercolor=black"
    )
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c={bg}:s=1280x720:r=1:d=1",
        "-vf", vf, "-frames:v", "1", output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return Path(output_path).exists()

def upload_thumbnail(youtube, video_id, path):
    from googleapiclient.http import MediaFileUpload
    try:
        youtube.thumbnails().set(videoId=video_id,
            media_body=MediaFileUpload(path, mimetype="image/jpeg")).execute()
        return True
    except Exception as e:
        print(f"サムネイルUpload失敗: {e}")
        return False

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "Claude Code Tips 10選"
    out = sys.argv[2] if len(sys.argv) > 2 else "thumbnail.jpg"
    print("✅" if generate_thumbnail(title, out) else "❌")
