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

Create a 12-scene script in Japanese for a 60-second vertical video.

CRITICAL RULE - TWO separate text fields per scene:
- "narration": Full natural Japanese sentence for voice (20-35 chars). This is SPOKEN.
- "caption": ONE ultra-short keyword shown on screen (MAX 8 chars). This is DISPLAYED.

Structure: Hook(2) -> Problem(2) -> Solution(3) -> How(3) -> Result(1) -> CTA(1)
- narration: 3rd person, natural spoken Japanese
- caption examples: "17,500⭐", "自動化", "3分で完了", "無料"
- CTA caption must be: "conduit"
- TWO Pexels search terms per scene (English, MUST be cinematic/3D/sci-fi style)
- visual examples: "cinematic dark technology", "3d hologram interface", "cyber neon city", "matrix code digital", "futuristic sci-fi space", "dark abstract motion", "holographic data stream", "artificial intelligence visualization"
- NEVER use plain office or coding footage - always cinematic and visually striking

Output ONLY valid JSON array:
[
  {{"id":1,"narration":"ナレーション文章(20-35文字)","caption":"表示文字(最大8文字)","visual_1":"english term","visual_2":"english term"}},
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
        # narrationフィールド優先、なければtextを使う
        narration_text = scene.get('narration', scene.get('text', ''))
        asyncio.run(_tts_scene(narration_text, path))
        dur = _probe_dur(path)
        scene['audio_path'] = path
        scene['actual_duration'] = dur
        print(f"   Scene {scene['id']}: {dur:.1f}s - {narration_text[:30]}...")
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

# === Step 5: 字幕生成(ナレーションテキストから直接生成) ===
def generate_captions_from_scenes(scenes: list, ass_path: Path) -> Path:
    """ナレーションテキストから直接Hormoziスタイルの字幕を生成
    Whisperの誤認識ゼロ・音声と100%一致"""
    print(f"[3/5] 📝 Hormozi字幕生成中...")
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "features"))
    from caption_generator import build_hormozi_ass
    
    IS_CI = os.environ.get("CI", "") == "true"
    font_name = "Noto Sans CJK JP" if IS_CI else "Hiragino Sans"
    
    build_hormozi_ass(scenes, str(ass_path), font_name=font_name, font_size=90)
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
    
    # 5. 口パクキャラクター動画生成
    print(f"[5/6] 🎭 口パクキャラクター動画生成中...")
    char_path = str(Path(__file__).parent / "assets" / "character_main.png")
    char_video = str(WORK_DIR / "character_lipsync.mp4")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from lipsync_generator import generate_lipsync_video
        generate_lipsync_video(char_path, combined, char_video,
                               mouth_x=540, mouth_y=503, fps=30)
        print(f"   ✅ 口パク動画生成完了")
    except Exception as e:
        print(f"   ⚠️ 口パク失敗: {e} → キャラ静止画で代替")
        # 失敗時はキャラ静止画をループ動画に
        dur = _probe_dur(combined)
        _run(["ffmpeg", "-y", "-loop", "1", "-i", char_path,
              "-t", str(dur),
              "-vf", "scale=1080:960:force_original_aspect_ratio=decrease,pad=1080:960:(ow-iw)/2:(oh-ih)/2",
              "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", char_video])

    # 6. 上下分割合成 + 字幕焼き込み
    print(f"[6/6] 🎬 上下分割合成中...")
    ass_path = WORK_DIR / f"{name}.ass"
    generate_captions_from_scenes(scenes, ass_path)

    output = str(OUTPUT_DIR / f"{name}_final.mp4")
    # 上: B-roll(1080x960) 下: キャラ口パク(1080x960) → 縦結合1080x1920
    # 字幕はキャラの下部(y=1800)に焼き込み
    filter_complex = (
        "[0:v]scale=1080:960:force_original_aspect_ratio=increase,"
        "crop=1080:960[top];"
        "[1:v]scale=1080:1936:force_original_aspect_ratio=increase,"
        "crop=1080:960:0:0[bottom];"
        "[top][bottom]vstack=inputs=2[stacked];"
        f"[stacked]ass={ass_path}:fontsdir=/usr/share/fonts[out]"
    )
    _run(["ffmpeg", "-y",
          "-i", combined,
          "-i", char_video,
          "-filter_complex", filter_complex,
          "-map", "[out]",
          "-map", "0:a",
          "-c:v", "libx264", "-preset", "fast", "-crf", "22",
          "-c:a", "aac", "-pix_fmt", "yuv420p", output])
    
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
    narration = " ".join(s.get('narration', s.get('text', '')) for s in scenes)
    print(f"\n📋 ナレーション:\n{narration}")
    print(f"\n#AI #GitHub #GitHubTrending #AIツール #エンジニア")

if __name__ == "__main__":
    main()
