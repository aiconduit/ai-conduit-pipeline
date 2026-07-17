#!/usr/bin/env python3
"""
AI Conduit 純ffmpegパイプライン v2 (シーン単位B-roll方式)
有料ツール(OpusClip/SubMagic)の裏側アルゴリズムを参考に実装

核心改善:
- シーンごとに異なるB-roll 2本を割り当て
- 各シーンのナレーションに完全同期
- キネティックキャプション(pysubs2)
- ASS字幕 with Noto Sans CJK

使い方:
    python3 ffmpeg_pipeline_v2.py "MadsLorentzen/ai-job-search" "17500" "説明"
"""
import sys, json, os, subprocess, requests, random, re, asyncio, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from features.viral_scorer import score_script, optimize_hook
from features.brand_template import BRAND, get_scene_template, add_watermark
from features.bgm_selector import get_bgm, mix_bgm

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit_v2")
IS_CI = os.environ.get("CI", "") == "true"

for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]:
    d.mkdir(parents=True, exist_ok=True)

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF]")
def strip_emoji(s): return EMOJI_RE.sub("", s)

def _run(args, check=True, capture=True):
    r = subprocess.run([str(a) for a in args], 
                      capture_output=capture, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"Command failed: {args[0]}\n{r.stderr[-500:]}")
    return r

def _probe_dur(f):
    r = _run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f])
    return float(r.stdout.strip())

# === Step 1: シーン単位スクリプト生成 ===
def generate_scene_script(repo, stars, description):
    print(f"[1/5] 📝 シーン単位スクリプト生成中...")
    prompt = f"""You are a scriptwriter for a high-retention Japanese AI/GitHub trends channel.
Topic: {repo} ({stars} stars) - {description}

Create a 6-scene script in Japanese for a 25-second vertical video.

Rules:
- 3rd person perspective (「このツールは...」「開発者が...」)
- Hook -> What -> How -> Why -> CTA structure  
- CRITICAL: Each scene text must be VERY SHORT: maximum 20 Japanese characters per scene
- 6 scenes total, each 3-4 seconds when spoken aloud
- NO long sentences. Each scene = ONE short punchy sentence only
- For each scene provide TWO distinct Pexels video search terms (English, specific and literal)
- visual_1: matches start of narration, visual_2: matches end or reaction
- CTA scene: 「コメントにconduitでテンプレ無料」(keep it short)

Output ONLY valid JSON array:
[
  {{"id":1,"text":"短いナレーション文(最大20文字)","visual_1":"english term","visual_2":"english term"}},
  ...
]"""

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={"model": "llama-3.3-70b-versatile", 
              "messages": [{"role": "user", "content": prompt}], 
              "max_tokens": 1200}
    )
    text = r.json()["choices"][0]["message"]["content"].strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
    scenes = json.loads(text.strip())
    print(f"   ✅ {len(scenes)}シーン生成完了")
    return scenes

# === Step 2: シーン別ナレーション生成 ===
async def _tts_scene(text, path):
    import edge_tts
    await edge_tts.Communicate(text, "ja-JP-KeitaNeural").save(path)

def generate_scene_narrations(scenes):
    print(f"[2/5] 🎙️ シーン別ナレーション生成中...")
    audio_paths = []
    for scene in scenes:
        path = str(WORK_DIR / f"scene_{scene['id']}.mp3")
        asyncio.run(_tts_scene(scene['text'], path))
        dur = _probe_dur(path)
        scene['audio_path'] = path
        scene['actual_duration'] = dur
        print(f"   Scene {scene['id']}: {dur:.1f}s - {scene['text'][:30]}...")
        audio_paths.append(path)
    return audio_paths

# === Step 3: Pexels B-roll取得 ===
def fetch_pexels_video(query, exclude_paths=[]):
    headers = {"Authorization": PEXELS_API_KEY}
    # tech系キーワードに変換
    tech_prefix = "programmer developer coding " if not any(kw in query.lower() for kw in ['code','program','develop','laptop','computer','screen','keyboard','terminal']) else ""
    search_q = tech_prefix + query
    
    params = {"query": search_q, "per_page": 10, "orientation": "portrait", "size": "small"}
    r = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=10)
    if r.status_code != 200:
        return None
    
    videos = [v for v in r.json().get("videos", []) if v.get("duration", 0) >= 3]
    if not videos:
        # フォールバック: シンプルなコーディング映像
        params["query"] = "programmer typing keyboard dark"
        r = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=10)
        videos = [v for v in r.json().get("videos", []) if v.get("duration", 0) >= 3]
    
    if not videos:
        return None
    
    # HD以下のファイルを選択
    for v in random.sample(videos, min(5, len(videos))):
        files = [f for f in v["video_files"] if 360 <= f.get("width", 0) <= 1920]
        if not files:
            files = v["video_files"]
        files.sort(key=lambda x: x["width"] * x["height"])
        url = files[-1]["link"] if files else None
        if not url:
            continue
        
        safe = re.sub(r'[^\w]', '_', query)[:20]
        fpath = PEXELS_CACHE / f"{safe}_{v['id']}.mp4"
        if str(fpath) not in exclude_paths:
            if not fpath.exists():
                resp = requests.get(url, stream=True, timeout=30)
                with open(fpath, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
            return str(fpath)
    return None

def fetch_scene_brolls(scenes):
    print(f"[3/5] 🎬 シーン別B-roll取得中...")
    for scene in scenes:
        v1 = fetch_pexels_video(scene['visual_1'])
        exclude = [v1] if v1 else []
        v2 = fetch_pexels_video(scene['visual_2'], exclude)
        scene['broll_a'] = v1
        scene['broll_b'] = v2 or v1  # B-rollがない場合はAを使用
        print(f"   Scene {scene['id']}: {Path(v1).name if v1 else 'none'} + {Path(scene['broll_b']).name if scene['broll_b'] else 'none'}")

# === Step 4: シーン別動画合成 ===
def compose_scene(scene, idx):
    """1シーンをA/Bスプリットで合成"""
    dur = scene['actual_duration']
    audio = scene['audio_path']
    broll_a = scene['broll_a']
    broll_b = scene['broll_b']
    output = str(WORK_DIR / f"composed_{idx:02d}.mp4")
    
    if not broll_a:
        # B-rollなし: 黒背景
        _run(["ffmpeg", "-y",
              "-f", "lavfi", "-i", f"color=black:s=1080x1920:r=30:d={dur}",
              "-i", audio,
              "-c:v", "libx264", "-preset", "fast", "-crf", "23",
              "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", output])
        return output
    
    dur_a = dur / 2
    dur_b = dur / 2 + 0.3
    
    temp_a = str(WORK_DIR / f"broll_a_{idx}.mp4")
    temp_b = str(WORK_DIR / f"broll_b_{idx}.mp4")
    
    loop_a = int(dur_a / max(_probe_dur(broll_a), 1)) + 2
    _run(["ffmpeg", "-y", "-stream_loop", str(loop_a), "-i", broll_a,
          "-t", str(dur_a), "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
          "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-an", "-pix_fmt", "yuv420p", temp_a])
    
    loop_b = int(dur_b / max(_probe_dur(broll_b), 1)) + 2
    _run(["ffmpeg", "-y", "-stream_loop", str(loop_b), "-i", broll_b,
          "-t", str(dur_b), "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
          "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-an", "-pix_fmt", "yuv420p", temp_b])
    
    # xfadeで結合
    temp_video = str(WORK_DIR / f"video_{idx}.mp4")
    offset = dur_a - 0.3
    trans = random.choice(['fade', 'slideleft', 'slideup', 'wipeleft'])
    _run(["ffmpeg", "-y", "-i", temp_a, "-i", temp_b,
          "-filter_complex", f"[0:v][1:v]xfade=transition={trans}:duration=0.3:offset={offset}[out]",
          "-map", "[out]", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
          temp_video])
    
    # ナレーション追加
    _run(["ffmpeg", "-y", "-i", temp_video, "-i", audio,
          "-c:v", "copy", "-c:a", "aac", "-map", "0:v", "-map", "1:a",
          "-shortest", "-pix_fmt", "yuv420p", output])
    
    return output

# === Step 5: キネティックキャプション生成 ===
def generate_kinetic_ass(all_audio_path, ass_path, scenes):
    print(f"[5/5] 📝 キネティックキャプション生成中...")
    import whisper, pysubs2
    
    model = whisper.load_model("small")
    result = model.transcribe(all_audio_path, word_timestamps=True, language="ja")
    
    all_words = []
    for segment in result.get("segments", []):
        all_words.extend(segment.get("words", []))
    
    font_name = "Noto Sans CJK JP"
    if not IS_CI:
        font_name = "Arial"
    
    subs = pysubs2.SSAFile()
    subs.info["PlayResX"] = "1080"
    subs.info["PlayResY"] = "1920"
    
    style = pysubs2.SSAStyle(
        fontname=font_name,
        fontsize=68,
        primarycolor=pysubs2.Color(255, 255, 255, 0),
        outlinecolor=pysubs2.Color(0, 0, 0, 0),
        backcolor=pysubs2.Color(0, 0, 0, 150),
        bold=True,
        outline=4,
        shadow=2,
        alignment=2,
        marginv=130,
        marginl=40,
        marginr=40,
    )
    subs.styles["Default"] = style
    
    # 日本語: セグメント単位で表示(単語ではなく文節単位)
    # Whisperのセグメント(文章の切れ目)をそのまま使う
    for segment in result.get("segments", []):
        seg_text = strip_emoji(segment["text"].strip())
        if not seg_text:
            continue
        start_ms = int(segment["start"] * 1000)
        end_ms = int(segment["end"] * 1000)
        duration_ms = end_ms - start_ms
        
        # 長いセグメントは2分割
        if len(seg_text) > 15 and duration_ms > 2000:
            mid = len(seg_text) // 2
            # 句読点で分割を試みる
            split_pos = seg_text.rfind("、", 0, mid+5) or seg_text.rfind("。", 0, mid+5) or mid
            if split_pos <= 0:
                split_pos = mid
            mid_ms = start_ms + duration_ms // 2
            
            subs.append(pysubs2.SSAEvent(
                start=pysubs2.make_time(ms=start_ms),
                end=pysubs2.make_time(ms=mid_ms),
                text=seg_text[:split_pos],
            ))
            subs.append(pysubs2.SSAEvent(
                start=pysubs2.make_time(ms=mid_ms),
                end=pysubs2.make_time(ms=end_ms),
                text=seg_text[split_pos:],
            ))
        else:
            subs.append(pysubs2.SSAEvent(
                start=pysubs2.make_time(ms=start_ms),
                end=pysubs2.make_time(ms=end_ms),
                text=seg_text,
            ))
    
    subs.save(str(ass_path))
    print(f"   ✅ {len(subs)}ブロックの字幕生成完了")
    return ass_path

# === メイン ===
def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "MadsLorentzen/ai-job-search"
    stars = sys.argv[2] if len(sys.argv) > 2 else "17500"
    description = sys.argv[3] if len(sys.argv) > 3 else "GitHubトレンドリポジトリ"
    name = repo.split("/")[-1]
    
    print(f"\n🚀 AI Conduit Pipeline v2 (シーン単位B-roll)")
    print(f"   {repo} ({stars}⭐)\n")
    
    # 1. シーン単位スクリプト生成
    scenes = generate_scene_script(repo, stars, description)
    
    # バイラルスコアリング
    print("   🎯 バイラルスコアリング中...")
    scenes = score_script(scenes)
    scenes = optimize_hook(scenes)

    # 2. シーン別ナレーション生成
    generate_scene_narrations(scenes)
    
    # 3. B-roll取得
    fetch_scene_brolls(scenes)
    
    # 4. シーン別動画合成
    print(f"[4/5] 🎬 シーン別動画合成中...")
    scene_videos = []
    for i, scene in enumerate(scenes):
        vid = compose_scene(scene, i)
        scene_videos.append(vid)
        print(f"   Scene {scene['id']} ✅")
    
    # 全シーンを結合
    concat_list = str(WORK_DIR / "concat.txt")
    with open(concat_list, "w") as f:
        for v in scene_videos:
            f.write(f"file '{v}'\n")
    
    combined = str(WORK_DIR / "combined.mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
          "-c:v", "libx264", "-preset", "fast", "-crf", "22",
          "-c:a", "aac", "-pix_fmt", "yuv420p", combined])
    
    # 5. キネティックキャプション生成・焼き込み
    ass_path = WORK_DIR / f"{name}.ass"
    generate_kinetic_ass(combined, ass_path, scenes)
    
    output = str(OUTPUT_DIR / f"{name}_final.mp4")
    _run(["ffmpeg", "-y", "-i", combined,
          "-vf", f"ass={ass_path}:fontsdir=/usr/share/fonts",
          "-c:v", "libx264", "-preset", "fast", "-crf", "22",
          "-c:a", "copy", "-pix_fmt", "yuv420p", output])
    
    # バイラルスコアリング結果表示
    scored = [s for s in scenes if "viral_score" in s]
    if scored:
        avg_score = sum(s["viral_score"] for s in scored) / len(scored)
        print(f"\n📊 バイラルスコア平均: {avg_score:.1f}/10")

    # ウォーターマーク追加
    output_wm = output.replace("_final.mp4", "_branded.mp4")
    try:
        add_watermark(output, output_wm)
        print(f"   ✅ ウォーターマーク追加完了")
        output = output_wm
    except Exception as e:
        print(f"   ⚠️ ウォーターマーク失敗: {e}")

    # BGM追加
    bgm = get_bgm(mood="upbeat")
    if bgm:
        output_bgm = output.replace(".mp4", "_bgm.mp4")
        try:
            mix_bgm(output, bgm, output_bgm, bgm_volume=0.12)
            output = output_bgm
            print(f"   ✅ BGM追加完了")
        except Exception as e:
            print(f"   ⚠️ BGM追加失敗: {e}")

    total_dur = _probe_dur(output)
    print(f"\n✅ 完成: {output} ({total_dur:.1f}s)")
    narration = " ".join(s['text'] for s in scenes)
    print(f"\n📋 ナレーション:\n{narration}")
    print(f"\n#AI #GitHub #GitHubTrending #AIツール #エンジニア")

if __name__ == "__main__":
    main()
