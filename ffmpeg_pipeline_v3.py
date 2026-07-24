#!/usr/bin/env python3
"""
AI Conduit パイプライン v3 - ニュースキャスター風ダイナミックエディット
- キャラクターがメイン（画面中央・大きく）
- punch-in zoom / screen shake / white flash
- B-rollはPIP（ピクチャーインピクチャー）で右上に小さく表示
- vignette（映画的暗縁）
- beat-sync風の動的カット

使い方:
    python3 ffmpeg_pipeline_v3.py "repo/name" "stars" "description"
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_bb78b0e1caafa33f46892b4395b362d047ad8d406cc0fc55")
GOOGLE_TTS_KEY = os.environ.get("GOOGLE_TTS_KEY", "AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit_v3")
CHAR_PATH = ROOT_DIR / "assets" / "character_main.png"

for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]:
    d.mkdir(parents=True, exist_ok=True)

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF]")
def strip_emoji(s): return EMOJI_RE.sub("", s)

def _run(args, check=True):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr[-800:]}")
    return r

def _probe_dur(f):
    r = _run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f])
    return float(r.stdout.strip())

# === Step 1: スクリプト生成 ===
def generate_script(repo, stars, description):
    print("[1/6] 📝 スクリプト生成中...")
    prompt = f"""You are a master storyteller for a Japanese AI news channel.
Topic: {repo} ({stars} stars) - {description}

Create a 10-scene STORY script. Character: タク (young Japanese engineer).

STRUCTURE:
- Scene 1-2 (hook): タク is in crisis. Shocking, casual, punchy.
- Scene 3-4 (problem): His daily pain. Relatable.
- Scene 5-6 (solution): タク discovers this tool. Excitement.
- Scene 7-8 (mechanism): HOW it works. Specific actions.
- Scene 9 (result): transformation. Numbers.
- Scene 10 (cta): Direct to viewer. "あなたも" + "AI Conduit"

STYLE: Ultra-casual Japanese. Like texting. Short punchy sentences.
Good: "タク、マジで100社落ちてた", "え、これ無料？やば"
Bad: "タクは困難な状況に置かれていた"

RULES:
- "narration": 15-30 chars, casual Japanese
- "caption": MAX 8 chars keyword
- "mood": hook/problem/solution/mechanism/result/cta
- "visual": ONE cinematic English Pexels search term
- "effect": ONE of [none, zoom_in, zoom_out, shake, flash, slow_zoom]

Output ONLY JSON array:
[
  {{"id":1,"narration":"タク、マジで100社落ちてた","caption":"100社落ち","mood":"hook","visual":"dark city rain cinematic","effect":"zoom_in"}},
  ...10 scenes...
]"""

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
    )
    resp = r.json()
    if "choices" not in resp:
        raise Exception(f"Groq error: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        text = text[start:end]
    text = re.sub(r"[\x00-\x1f]", "", text)
    scenes = json.loads(text)
    print(f"   ✅ {len(scenes)}シーン生成完了")
    return scenes

# === Step 2: TTS ===
def tts_scene(text, path):
    """ElevenLabs George → Google TTS fallback"""
    r = requests.post(
        "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json={"text": text, "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": 0.45, "similarity_boost": 0.75, "style": 0.3}}
    )
    if r.status_code == 200:
        with open(path, "wb") as f: f.write(r.content)
    else:
        import base64
        r2 = requests.post(
            f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
            json={"input": {"text": text}, "voice": {"languageCode": "ja-JP", "name": "ja-JP-Chirp3-HD-Charon"}, "audioConfig": {"audioEncoding": "MP3"}}
        )
        with open(path, "wb") as f: f.write(base64.b64decode(r2.json()["audioContent"]))

def generate_narrations(scenes):
    print("[2/6] 🎙️ ナレーション生成中...")
    for scene in scenes:
        path = str(WORK_DIR / f"narr_{scene['id']:02d}.mp3")
        text = strip_emoji(scene.get("narration", ""))
        tts_scene(text, path)
        dur = _probe_dur(path)
        scene["audio_path"] = path
        scene["duration"] = dur
        print(f"   Scene {scene['id']}: {dur:.1f}s")
    return scenes

# === Step 3: Pexels B-roll ===
def fetch_broll(query):
    headers = {"Authorization": PEXELS_API_KEY}
    r = requests.get("https://api.pexels.com/videos/search",
                     headers=headers, params={"query": query, "per_page": 8, "orientation": "portrait"}, timeout=10)
    if r.status_code != 200: return None
    videos = [v for v in r.json().get("videos", []) if v.get("duration", 0) >= 3]
    if not videos: return None
    v = random.choice(videos[:5])
    files = sorted([f for f in v["video_files"] if 360 <= f.get("width", 0) <= 1080], key=lambda x: x["width"])
    url = files[-1]["link"] if files else v["video_files"][0]["link"]
    safe = re.sub(r"[^\w]", "_", query)[:20]
    fpath = PEXELS_CACHE / f"{safe}_{v['id']}.mp4"
    if not fpath.exists():
        resp = requests.get(url, stream=True, timeout=30)
        with open(fpath, "wb") as f:
            for chunk in resp.iter_content(8192): f.write(chunk)
    return str(fpath)

def fetch_brolls(scenes):
    print("[3/6] 🎬 B-roll取得中...")
    for scene in scenes:
        broll = fetch_broll(scene.get("visual", "cinematic technology dark"))
        scene["broll"] = broll
        print(f"   Scene {scene['id']}: {Path(broll).name if broll else 'none'}")
    return scenes

# === Step 4: エフェクト付きシーン合成 ===
def apply_effect_to_char(char_img, dur, effect, idx):
    """キャラクター画像にエフェクトを適用"""
    out = str(WORK_DIR / f"char_{idx:02d}.mp4")
    frames = max(int(dur * 30), 1)
    
    base_vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
    
    if effect == "zoom_in":
        # punch-in zoom: 1.0→1.08 over first 0.15s then back
        vf = (f"{base_vf},"
              f"zoompan=z='if(lte(on,{int(0.15*30)}),1+0.08*(on/{int(0.15*30)}),if(lte(on,{int(0.3*30)}),1.08-0.08*((on-{int(0.15*30)})/{int(0.15*30)}),1))'"
              f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30")
    elif effect == "zoom_out":
        vf = (f"{base_vf},"
              f"zoompan=z='if(lte(on,{frames}),1.08-0.08*(on/{frames}),1)'"
              f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30")
    elif effect == "shake":
        vf = (f"scale=1120:1960:force_original_aspect_ratio=decrease,pad=1120:1960:(ow-iw)/2:(oh-ih)/2,"
              f"crop=1080:1920:x='10*sin(t*30)':y='8*sin(t*25)'")
    elif effect == "slow_zoom":
        vf = (f"{base_vf},"
              f"zoompan=z='min(zoom+0.0008,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30")
    else:
        vf = base_vf

    _run(["ffmpeg", "-y", "-loop", "1", "-i", char_img,
          "-t", str(dur), "-vf", vf,
          "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", out])
    return out

def compose_scene(scene, idx):
    """シーンを合成: キャラメイン + B-roll PIP + white flash + vignette"""
    dur = scene["duration"]
    audio = scene["audio_path"]
    broll = scene["broll"]
    effect = scene.get("effect", "none")
    out = str(WORK_DIR / f"scene_{idx:02d}.mp4")

    # キャラクターにエフェクト適用
    char_video = apply_effect_to_char(str(CHAR_PATH), dur, effect, idx)

    if broll and os.path.exists(broll):
        # B-roll PIP: 右上に320x180で表示
        broll_dur = _probe_dur(broll)
        loop = int(dur / max(broll_dur, 1)) + 2
        broll_pip = str(WORK_DIR / f"pip_{idx:02d}.mp4")
        _run(["ffmpeg", "-y", "-stream_loop", str(loop), "-i", broll,
              "-t", str(dur),
              "-vf", "scale=320:180:force_original_aspect_ratio=increase,crop=320:180",
              "-c:v", "libx264", "-preset", "fast", "-an", "-pix_fmt", "yuv420p", broll_pip])

        # PIP overlay + audio（シンプル版）
        _run(["ffmpeg", "-y",
              "-i", char_video, "-i", audio, "-i", broll_pip,
              "-filter_complex",
              "[0:v][2:v]overlay=x=W-w-20:y=20[out]",
              "-map", "[out]", "-map", "1:a",
              "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", out])
    else:
        _run(["ffmpeg", "-y", "-i", char_video, "-i", audio,
              "-c:v", "copy", "-c:a", "aac", "-shortest", out])

    # white flash on zoom_in/flash effect
    if effect in ["zoom_in", "flash"]:
        flash_out = str(WORK_DIR / f"flash_{idx:02d}.mp4")
        _run(["ffmpeg", "-y", "-i", out,
              "-vf", f"fade=t=in:st=0:d=0.08:color=white",
              "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-c:a", "copy", "-pix_fmt", "yuv420p", flash_out])
        os.replace(flash_out, out)

    return out

def compose_all_scenes(scenes):
    print("[4/6] 🎬 シーン合成中...")
    scene_files = []
    for i, scene in enumerate(scenes):
        f = compose_scene(scene, i)
        scene_files.append(f)
        print(f"   Scene {scene['id']} [{scene.get('effect','none')}]: {scene['duration']:.1f}s")
    return scene_files

# === Step 5: 連結 ===
def concat_scenes(scene_files):
    print("[5/6] 🔗 シーン連結中...")
    concat_list = str(WORK_DIR / "concat_v3.txt")
    with open(concat_list, "w") as f:
        for sf in scene_files:
            f.write(f"file '{sf}'\n")
    combined = str(WORK_DIR / "combined_v3.mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
          "-c:v", "libx264", "-preset", "fast", "-crf", "22",
          "-c:a", "aac", "-pix_fmt", "yuv420p", combined])
    return combined

# === Step 6: 字幕オーバーレイ ===
def add_subtitles(video, scenes):
    print("[6/6] 📝 字幕追加中...")
    from features.caption_generator import build_caption_pngs, overlay_captions_on_video, generate_hook_png, generate_cta_png
    
    caption_dir = str(WORK_DIR / "captions_v3")
    build_caption_pngs(scenes, caption_dir)

    # Hook PNG
    stars_val = scenes[0].get("narration", "")
    hook_png = str(WORK_DIR / "hook_v3.png")
    try:
        generate_hook_png("AI Conduit News", hook_png)
        total_dur = _probe_dur(video)
        video_hook = str(WORK_DIR / "video_hook_v3.mp4")
        _run(["ffmpeg", "-y", "-i", video, "-i", hook_png,
              "-filter_complex",
              "[1:v]fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st=2.5:d=0.2:alpha=1[hook];"
              "[0:v][hook]overlay=x=(W-w)/2:y=60:enable='between(t,0,2.8)'[out]",
              "-map", "[out]", "-map", "0:a",
              "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-c:a", "aac", "-pix_fmt", "yuv420p", video_hook])
        video = video_hook
    except Exception as e:
        print(f"   ⚠️ Hook失敗: {e}")

    # CTA PNG
    try:
        cta_png = str(WORK_DIR / "cta_v3.png")
        generate_cta_png("👇 AI Conduit をフォロー", cta_png)
        total_dur = _probe_dur(video)
        cta_start = max(0, total_dur - 2.5)
        video_cta = str(WORK_DIR / "video_cta_v3.mp4")
        _run(["ffmpeg", "-y", "-i", video, "-i", cta_png,
              "-filter_complex",
              f"[1:v]fade=t=in:st=0:d=0.3:alpha=1[cta];"
              f"[0:v][cta]overlay=x=(W-w)/2:y=900:enable='between(t,{cta_start},{total_dur})'[out]",
              "-map", "[out]", "-map", "0:a",
              "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-c:a", "aac", "-pix_fmt", "yuv420p", video_cta])
        video = video_cta
    except Exception as e:
        print(f"   ⚠️ CTA失敗: {e}")

    name = OUTPUT_DIR / "pipeline_v3_output.mp4"
    overlay_captions_on_video(video, scenes, caption_dir, str(name))
    return str(name)

# === メイン ===
def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "MadsLorentzen/ai-job-search"
    stars = sys.argv[2] if len(sys.argv) > 2 else "17500"
    description = sys.argv[3] if len(sys.argv) > 3 else "Claude Codeで就活を自動化"

    print(f"\n🚀 AI Conduit Pipeline v3 起動")
    print(f"   Topic: {repo} ({stars}★)\n")

    scenes = generate_script(repo, stars, description)
    scenes = generate_narrations(scenes)
    scenes = fetch_brolls(scenes)
    scene_files = compose_all_scenes(scenes)
    combined = concat_scenes(scene_files)
    output = add_subtitles(combined, scenes)

    dur = _probe_dur(output)
    print(f"\n✅ 完成: {output} ({dur:.1f}s)")

if __name__ == "__main__":
    main()
