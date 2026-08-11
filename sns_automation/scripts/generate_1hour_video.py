#!/usr/bin/env python3
"""
generate_1hour_video.py
1時間動画完全版
- チャプター自動生成
- 視聴維持率対策（3分おきに新要素）
- サムネイル自動生成
- Lex Fridman/Nate Herkスタイル
"""
import os, json, subprocess, asyncio, textwrap
from pathlib import Path

PEXELS = os.environ.get("PEXELS_API_KEY","")
CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

SECTION_DURATION = 360  # 6分/セクション
INTRO_DURATION = 120    # 2分イントロ
OUTRO_DURATION = 120    # 2分アウトロ

def get_pexels_video(query, api_key):
    import requests as req
    if not api_key:
        return None
    try:
        r = req.get("https://api.pexels.com/videos/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 3, "min_duration": 10},
            timeout=10)
        if r.status_code == 200:
            videos = r.json().get("videos", [])
            if videos:
                files = sorted(videos[0]["video_files"],
                               key=lambda x: x.get("width",0), reverse=True)
                return files[0]["link"] if files else None
    except:
        pass
    return None

async def gen_audio(text, out_path, rate="+5%", pitch="+2Hz"):
    """Edge TTSで音声生成"""
    import edge_tts
    communicate = edge_tts.Communicate(text, "ja-JP-KeitaNeural",
                                        rate=rate, pitch=pitch)
    await communicate.save(out_path)

def build_section(script, idx, duration=360):
    """1セクション（6分）動画生成"""
    topic = script.get("topic", f"Claude Code Tips #{idx+1}")
    out = f"/tmp/section_{idx:02d}.mp4"

    # ナレーション構築（視聴維持率対策：中間でコメント誘導）
    parts = []
    for scene in ["hook", "why", "solution", "step1", "step2", "result", "cta"]:
        s = script.get(scene, {})
        n = s.get("narration", "")
        if n:
            parts.append(n)

    # 中間（3分）にコメント誘導を挿入（視聴維持率対策）
    mid = len(parts) // 2
    parts.insert(mid, f"この{topic}の機能は知っていましたか？コメントで教えてください。")

    full_narration = "。".join(parts)
    audio_path = f"/tmp/sec_{idx:02d}.mp3"
    asyncio.run(gen_audio(full_narration, audio_path))

    # B-roll取得
    broll = get_pexels_video(f"developer coding computer dark", PEXELS)
    broll_path = f"/tmp/broll_{idx:02d}.mp4"

    if broll:
        import requests as req
        r = req.get(broll, timeout=30)
        with open(broll_path, "wb") as f:
            f.write(r.content)
    else:
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c=0x0a0a14:s=1920x1080:r=30:d={duration}",
            "-c:v", "libx264", "-preset", "fast", broll_path
        ], capture_output=True)

    # セクションタイトルテキスト（安全なASCIIのみ）
    safe_num = str(idx + 1)

    # 動画合成
    vf = (
        f"scale=1920:1080:force_original_aspect_ratio=decrease,"
        f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:0x0a0a14,"
        # セクション番号バッジ
        f"drawbox=x=0:y=0:w=iw:h=80:color=0x1a1a2e:t=fill,"
        f"drawtext=text='Claude Code Tips {safe_num}/10':"
        f"x=30:y=20:fontsize=40:fontcolor=0xFFD700:borderw=2:bordercolor=black,"
        # 進捗バー
        f"drawbox=x=0:y=ih-8:w=iw*{(idx+1)/10}:h=8:color=0xFFD700:t=fill"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", broll_path,
        "-i", audio_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-t", str(duration),
        out
    ]
    r = subprocess.run(cmd, capture_output=True)
    return out if Path(out).exists() else None

def build_intro(scripts, duration=120):
    """2分イントロ：今日学べる10個を一覧で見せる"""
    out = "/tmp/intro.mp4"
    audio_path = "/tmp/intro_audio.mp3"

    topics = [s.get("topic", f"Tips #{i+1}")[:20] for i, s in enumerate(scripts[:10])]
    topic_list = "。".join([f"{i+1}つ目、{t}" for i, t in enumerate(topics)])
    narration = f"今日はClaude Codeの使い方、10個まとめて解説します。{topic_list}。最後まで見ると全部使えるようになります。"
    asyncio.run(gen_audio(narration, audio_path, rate="+8%", pitch="+3Hz"))

    # イントロ画面（黒背景＋タイトル）
    vf_parts = [
        "color=c=0x0a0a14:s=1920x1080:r=30",
    ]

    cmd_bg = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x0a0a14:s=1920x1080:r=30:d={duration}",
        "-i", audio_path,
        "-vf", (
            "drawbox=x=0:y=0:w=iw:h=iw:color=0x0a0a14:t=fill,"
            "drawtext=text='Claude Code':x=(w-tw)/2:y=80:fontsize=80:fontcolor=0xFFD700:borderw=3:bordercolor=black,"
            "drawtext=text='Today Tips 10':x=(w-tw)/2:y=180:fontsize=60:fontcolor=white:borderw=2:bordercolor=black"
        ),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-shortest", "-t", str(duration),
        out
    ]
    subprocess.run(cmd_bg, capture_output=True)
    return out if Path(out).exists() else None

def build_outro(duration=120):
    """2分アウトロ：まとめ＋CTA"""
    out = "/tmp/outro.mp4"
    audio_path = "/tmp/outro_audio.mp3"
    narration = (
        "以上、Claude Codeの使い方10個を解説しました。"
        "今日紹介したテンプレートファイルは全て概要欄から無料で受け取れます。"
        "ショート動画では各機能を45秒で解説しています。チャンネル登録してお待ちください。"
        "次回どの機能を詳しく解説してほしいか、コメントで教えてください。"
    )
    asyncio.run(gen_audio(narration, audio_path, rate="+5%", pitch="+3Hz"))

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x0a0a14:s=1920x1080:r=30:d={duration}",
        "-i", audio_path,
        "-vf", (
            "drawbox=x=0:y=0:w=iw:h=iw:color=0x0a0a14:t=fill,"
            "drawtext=text='Subscribe':x=(w-tw)/2:y=(h-th)/2:fontsize=100:fontcolor=0xFFD700:borderw=4:bordercolor=black,"
            "drawtext=text='Free Templates in Description':x=(w-tw)/2:y=(h-th)/2+120:fontsize=50:fontcolor=white:borderw=2:bordercolor=black"
        ),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-shortest", "-t", str(duration),
        out
    ]
    subprocess.run(cmd, capture_output=True)
    return out if Path(out).exists() else None

def generate_chapters(scripts):
    """チャプター情報を生成（概要欄に自動挿入）"""
    chapters = []
    current_sec = 0

    # イントロ
    chapters.append({"time": "00:00", "title": "イントロ"})
    current_sec += INTRO_DURATION

    # 各セクション
    for i, script in enumerate(scripts[:10]):
        topic = script.get("topic", f"Tips #{i+1}")[:30]
        m = current_sec // 60
        s = current_sec % 60
        chapters.append({"time": f"{m:02d}:{s:02d}", "title": f"#{i+1} {topic}"})
        current_sec += SECTION_DURATION

    # アウトロ
    m = current_sec // 60
    s = current_sec % 60
    chapters.append({"time": f"{m:02d}:{s:02d}", "title": "まとめ・テンプレート配布"})

    return chapters

def generate_thumbnail(title, output_path="thumbnail.jpg"):
    """サムネイル生成（FFmpeg drawtext）"""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x0a0a14:s=1280x720:r=1:d=1",
        "-vf", (
            # 背景グラデーション
            "drawbox=x=0:y=0:w=iw:h=ih:color=0x0a0a14:t=fill,"
            "drawbox=x=0:y=0:w=8:h=ih:color=0xFFD700:t=fill,"
            # メインタイトル
            "drawtext=text='Claude Code':x=50:y=80:fontsize=90:fontcolor=0xFFD700:borderw=4:bordercolor=black,"
            "drawtext=text='Tips 10':x=50:y=200:fontsize=120:fontcolor=white:borderw=4:bordercolor=black,"
            # サブタイトル
            "drawtext=text='Complete Guide 2026':x=50:y=360:fontsize=55:fontcolor=0xaaaaaa:borderw=2:bordercolor=black,"
            # バッジ
            "drawbox=x=50:y=440:w=300:h=70:color=0xFF4444:t=fill,"
            "drawtext=text='FREE TEMPLATES':x=70:y=458:fontsize=38:fontcolor=white:borderw=2:bordercolor=black"
        ),
        "-frames:v", "1",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return Path(output_path).exists()

def main():
    data = json.loads(Path("all_scripts.json").read_text())
    shorts = data.get("shorts", [])
    longform = data.get("longform", {})

    title = longform.get("title", "Claude Code Tips 10選 完全解説")
    print(f"1時間動画生成: {title}")
    print(f"構成: イントロ2分 + Tips×10（各6分） + アウトロ2分 = 62分")

    # チャプター生成
    chapters = generate_chapters(shorts)
    print("\nチャプター:")
    for ch in chapters:
        print(f"  {ch['time']} {ch['title']}")

    # 各パート生成
    section_files = []

    # イントロ
    print("\nイントロ生成中...")
    intro = build_intro(shorts, INTRO_DURATION)
    if intro:
        section_files.append(intro)
        print("✅ イントロ")

    # 各セクション
    for i, script in enumerate(shorts[:10]):
        print(f"\nセクション {i+1}/10: {script.get('topic','')[:30]}")
        sec = build_section(script, i, SECTION_DURATION)
        if sec:
            section_files.append(sec)
            print(f"✅ セクション{i+1}")
        else:
            print(f"❌ 失敗")

    # アウトロ
    print("\nアウトロ生成中...")
    outro = build_outro(OUTRO_DURATION)
    if outro:
        section_files.append(outro)
        print("✅ アウトロ")

    if not section_files:
        print("❌ セクションなし")
        return

    # 全セクション結合
    concat_file = "/tmp/longform_concat.txt"
    with open(concat_file, "w") as f:
        for sf in section_files:
            f.write(f"file '{sf}'\n")

    print(f"\n結合中... ({len(section_files)}パート)")
    result = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "longform_output.mp4"
    ], capture_output=True)

    if Path("longform_output.mp4").exists():
        size = Path("longform_output.mp4").stat().st_size // 1024 // 1024
        print(f"✅ 1時間動画完成: {size}MB")
    else:
        print(f"❌ 結合失敗: {result.stderr[-200:]}")
        return

    # サムネイル生成
    print("\nサムネイル生成中...")
    if generate_thumbnail(title):
        print("✅ thumbnail.jpg")

    # チャプター情報をJSONで保存（upload時に概要欄に追加）
    chapter_text = "\n".join([f"{ch['time']} {ch['title']}" for ch in chapters])
    Path("longform_chapters.txt").write_text(chapter_text)
    print(f"\nチャプター:\n{chapter_text}")

    Path("longform_plan.json").write_text(
        json.dumps({"title": title, "chapters": chapters}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
