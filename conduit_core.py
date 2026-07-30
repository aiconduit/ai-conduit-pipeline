#!/usr/bin/env python3
"""
AI Conduit Core Framework v2.0
- DeepSeek API対応スクリプト生成
- Cinema Directorスタイルのシネマティックプロンプト
- BGM追加（Pexels Audio / 内蔵フォールバック）
- パターンインタラプト（5-10秒ごとに視覚変化）
- ループ構造（最後→最初）
- Hook-Value-CTAフレームワーク強制
"""
import os, requests, random, re, subprocess, json, urllib.parse
from pathlib import Path

# === API設定 ===
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "sk-71eab12699f047a5891e62268c66c241")
GROQ_KEY = os.environ.get("GROQ_API_KEY", "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")
GOOGLE_TTS_KEY = os.environ.get("GOOGLE_TTS_KEY", "AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY", "")

# === Cinema Director スタイル定義 ===
CINEMATIC_STYLES = {
    "heroic_reveal": {
        "shot": "Low Angle Wide Shot",
        "movement": "Crane Up with Orbit",
        "lighting": "Rim Lighting High Contrast Golden Hour",
        "suffix": "cinematic lighting, dramatic atmosphere, 4K, photorealistic, film grain",
    },
    "tense_uneasy": {
        "shot": "Dutch Angle Close-Up",
        "movement": "Handheld Shake Push In",
        "lighting": "Low Key Harsh Shadows Chiaroscuro",
        "suffix": "dark cinematic tone, high contrast, photorealistic, dramatic chiaroscuro",
    },
    "majestic_epic": {
        "shot": "Extreme Wide Shot Drone",
        "movement": "Drone Flyover Dolly Out",
        "lighting": "Golden Hour Volumetric God Rays",
        "suffix": "epic cinematic shot, hyper-realistic, dramatic shadows, professional photography",
    },
    "introspective": {
        "shot": "Medium Close-Up Profile",
        "movement": "Slow Push In Rack Focus",
        "lighting": "Soft Rembrandt Window Light",
        "suffix": "cinematic, moody lighting, ultra detailed, photorealistic, shallow depth of field",
    },
    "cyberpunk_neon": {
        "shot": "Wide Shot with Foreground",
        "movement": "Truck Left Pedestal Up",
        "lighting": "Neon Cyberpunk Rim Lighting Teal Orange Grade",
        "suffix": "neon-lit cinematic, cyberpunk atmosphere, ultra detailed, photorealistic",
    },
    "documentary": {
        "shot": "Medium Shot Shoulder Level",
        "movement": "Slow Dolly In Handheld",
        "lighting": "Natural Overcast Soft Box",
        "suffix": "documentary style, natural lighting, photorealistic, film grain",
    },
}

CINEMATIC_SUFFIXES = [
    "cinematic lighting, dramatic atmosphere, 4K, photorealistic, film grain",
    "cinematic, moody lighting, ultra detailed, photorealistic, shallow depth of field",
    "dramatic lighting, volumetric fog, photorealistic, cinematic composition, 4K",
    "epic cinematic shot, hyper-realistic, dramatic shadows, professional photography",
    "neon-lit cinematic, cyberpunk atmosphere, ultra detailed, photorealistic",
    "atmospheric fog, cinematic color grading, photorealistic, wide angle lens",
    "dark cinematic tone, high contrast, photorealistic, dramatic chiaroscuro",
]

# === Hook-Value-CTAフレームワーク ===
HOOK_TEMPLATES = [
    "「{topic}」を知らないエンジニアは損している",
    "え、{topic}って無料なの？",
    "深夜2時に見つけた{topic}がヤバすぎた",
    "100社落ちたタクが{topic}で逆転した話",
    "GitHubで今一番バズってる{topic}を解説する",
    "誰も教えてくれない{topic}の真実",
    "これを知った日、就活が変わった",
    "{topic}を3分で理解する",
    "AIエンジニアが全員使ってる{topic}とは",
    "信じられない、{topic}が無料だと？",
]

PATTERN_INTERRUPTS = [
    "zoom_punch",    # ズームイン + パンチ効果
    "color_flash",   # 色フラッシュ
    "text_pop",      # テキストポップアップ
    "speed_ramp",    # 速度変化
    "cut_zoom",      # カット + ズーム
]

def generate_script_deepseek(repo, stars, description, style="viral_hook", max_scenes=8):
    """DeepSeek APIでスクリプト生成（Claude品質・低コスト）"""
    print(f"[Script] DeepSeekでスクリプト生成中... (style={style})")
    
    hook = random.choice(HOOK_TEMPLATES).format(
        topic=repo.split("/")[-1] if "/" in repo else repo
    )
    
    cinematic = random.choice(list(CINEMATIC_STYLES.values()))
    
    system_prompt = """You are a viral short-form video script writer for Japanese AI/tech content.
You specialize in Hook-Value-CTA framework and Cinema Director techniques.
ALWAYS write in Japanese. ALWAYS output valid JSON only."""

    user_prompt = f"""Write a {max_scenes}-scene viral Japanese short video script about: {repo} ({stars}★) - {description}

VIRAL FRAMEWORK (MUST FOLLOW):
- Scene 1 (Hook, 0-3s): "{hook}" - STOP SCROLL IMMEDIATELY
- Scene 2-3 (Pattern Interrupt): Unexpected twist or surprising fact
- Scene 4-6 (Value): Core information, build curiosity
- Scene 7 (Secondary Hook): New info to keep watching
- Scene 8 (CTA): Follow + Share prompt

CINEMA DIRECTOR STYLE:
- Shot type: {cinematic['shot']}
- Camera: {cinematic['movement']}
- Lighting: {cinematic['lighting']}

RULES:
- "narration": 15-30 chars PUNCHY Japanese. Active voice. Short sentences.
- "caption": 4-8 chars keyword
- "visual_prompt": English cinematic Pexels search + "{cinematic['suffix']}"
- "interrupt": one of [zoom_punch, color_flash, text_pop, speed_ramp, cut_zoom, none]
- "mood": hook/interrupt/value/secondary_hook/cta
- FIRST SCENE must have large text visible in first frame

Output ONLY JSON array:
[
  {{"id":1,"narration":"聞いてくれ、これヤバい","caption":"衝撃","visual_prompt":"dark dramatic cinematic {cinematic['suffix']}","interrupt":"zoom_punch","mood":"hook"}},
  ...{max_scenes} scenes...
]"""

    try:
        r = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], "max_tokens": 1500, "temperature": 0.8},
            timeout=60)
        resp = r.json()
        if "choices" not in resp:
            raise Exception(f"DeepSeek: {resp}")
        text = resp["choices"][0]["message"]["content"].strip()
        s=text.find("["); e=text.rfind("]")+1
        if s>=0 and e>s: text=text[s:e]
        scenes = json.loads(re.sub(r"[\x00-\x1f]","",text))
        print(f"   ✅ {len(scenes)}シーン (DeepSeek)")
        return scenes
    except Exception as ex:
        print(f"   ⚠️ DeepSeek失敗、Groqにフォールバック: {ex}")
        return generate_script_groq(repo, stars, description, max_scenes)

def generate_script_groq(repo, stars, description, max_scenes=8):
    """Groq APIフォールバック"""
    prompt = f"""Write {max_scenes} scenes for Japanese viral short video about {repo} ({stars}★) - {description}
Hook first, value middle, CTA last.
Output ONLY JSON: [{{"id":1,"narration":"日本語15-30文字","caption":"4-8文字","visual_prompt":"English cinematic search","interrupt":"zoom_punch","mood":"hook"}},...]"""
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens": 900})
    resp = r.json()
    if "choices" not in resp: raise Exception(f"Groq: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    s=text.find("["); e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    return json.loads(re.sub(r"[\x00-\x1f]","",text))

def tts_japanese(text, path, speed=1.05):
    """Edge TTS - ja-JP-NanamiNeural with word timestamps"""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sns_automation", "scripts"))
    try:
        from edge_tts_service import generate_speech_with_timestamps
        audio_path, timestamps = generate_speech_with_timestamps(text, path)
        return audio_path, timestamps
    except Exception as e:
        print(f"   ⚠️ Edge TTS失敗 ({e}), Google TTSにフォールバック")
        return _tts_google_fallback(text, path, speed)

def _tts_google_fallback(text, path, speed=1.05):
    """Google Cloud TTSフォールバック（タイムスタンプなし → 空リスト[]）"""
    import base64
    clean = re.sub(r"[\U0001F000-\U0001FAFF]","",text).strip()[:200]
    key = os.environ.get("GOOGLE_TTS_KEY","")
    if not key:
        raise Exception("GOOGLE_TTS_KEY not set")
    r = requests.post(
        f"https://texttospeech.googleapis.com/v1/text:synthesize?key={key}",
        headers={"Content-Type": "application/json"},
        json={"input":{"text":clean},
              "voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},
              "audioConfig":{"audioEncoding":"MP3","speakingRate":speed}})
    if r.status_code == 200:
        audio = base64.b64decode(r.json()["audioContent"])
        with open(path,"wb") as f: f.write(audio)
        return path, []
    raise Exception(f"Google TTS error: {r.status_code}")

def generate_word_subtitle_audio(text, path, speed=1.05, keywords=None):
    """Edge TTS based word-level subtitle audio generation. Returns (audio_path, list[WordTimestamp])"""
    audio_path, raw_timestamps = tts_japanese(text, path, speed)
    from word_sync_subtitle import WordTimestamp
    result = []
    for t in raw_timestamps:
        result.append(WordTimestamp(
            word=t.get("word", t.get("text", "")),
            start_sec=t.get("start", 0),
            end_sec=t.get("end", 0.3),
        ))
    return audio_path, result


def get_audio_duration(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=10,
        )
        return float(r.stdout.strip())
    except:
        return 3.0


def _pexels_download(query, cache_dir, orientation="portrait"):
    headers = {"Authorization": PEXELS_KEY}
    r = requests.get("https://api.pexels.com/videos/search", headers=headers,
        params={"query": f"{query} cinematic", "per_page": 10, "orientation": orientation}, timeout=15)
    if r.status_code != 200:
        r = requests.get("https://api.pexels.com/videos/search", headers=headers,
            params={"query": query, "per_page": 10, "orientation": orientation}, timeout=15)
    if r.status_code != 200:
        return None
    videos = [v for v in r.json().get("videos", []) if v.get("duration", 0) >= 4]
    if not videos:
        return None
    v = random.choice(videos[:5])
    files = sorted([f for f in v["video_files"] if 360 <= f.get("width", 0) <= 1080], key=lambda x: x["width"])
    url = files[-1]["link"] if files else v["video_files"][0]["link"]
    safe = re.sub(r"[^\w]", "_", query)[:25]
    fpath = Path(cache_dir) / f"{safe}_{v['id']}.mp4"
    if not fpath.exists():
        resp = requests.get(url, stream=True, timeout=30)
        with open(fpath, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
    return str(fpath)


def fetch_broll_cinematic(query, orientation="portrait", cache_dir=None):
    """単一B-roll取得: 指定クエリから1つのclipを返す
    検索は英語のままPexelsに送信。失敗時はフォールバッククエリで再試行。
    """
    if cache_dir is None:
        cache_dir = Path("/tmp/pexels_cache")
    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    fallback_queries = [
        "technology abstract",
        "computer code",
        "artificial intelligence",
        "futuristic technology dark",
        "tech workspace modern",
    ]

    result = _pexels_download(query, cache_dir, orientation)
    if result:
        return result

    for fq in fallback_queries:
        result = _pexels_download(fq, cache_dir, orientation)
        if result:
            print(f"   ⚠️ 本来のクエリ'{query}'が空 → フォールバック: '{fq}'")
            return result

    # 最終フォールバック: tech系別クエリで再試行
    for fq in fallback_queries:
        result = _pexels_download(fq + " cinematic", cache_dir, orientation)
        if result:
            print(f"   ⚠️ 全フォールバック失敗 → '{fq} cinematic' で再試行")
            return result

    # Pixabayフォールバック（高品質・APIキー必要）
    pixabay_result = _pixabay_download(query, cache_dir)
    if pixabay_result:
        return pixabay_result

    # Mixkitフォールバック（無料・高品質・APIキー不要）
    mixkit_result = _mixkit_fallback(query, cache_dir)
    if mixkit_result:
        return mixkit_result

    return None

def _pixabay_download(query, cache_dir):
    """Pixabay無料動画を取得（高品質・500件以上）"""
    if not PIXABAY_KEY:
        return None
    try:
        r = requests.get("https://pixabay.com/api/videos/", params={
            "key": PIXABAY_KEY,
            "q": query,
            "per_page": 10,
            "video_type": "film",
            "safesearch": "true",
        }, timeout=10)
        if r.status_code != 200:
            return None
        hits = r.json().get("hits", [])
        if not hits:
            return None
        import random
        v = random.choice(hits[:5])
        videos = v.get("videos", {})
        best = max(videos.values(), key=lambda x: x.get("width", 0), default=None)
        if not best:
            return None
        url = best.get("url", "")
        if not url:
            return None
        cache_dir = Path(cache_dir) if cache_dir else Path("/tmp/pexels_cache")
        cache_dir.mkdir(exist_ok=True)
        out = cache_dir / f"pixabay_{v['id']}.mp4"
        if out.exists():
            return str(out)
        resp = requests.get(url, timeout=30, stream=True)
        if resp.status_code == 200:
            with open(out, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"   Pixabay ✅ {v['id']}")
            return str(out)
    except Exception as e:
        print(f"   Pixabay error: {e}")
    return None

def _mixkit_fallback(query, cache_dir):
    """Mixkit無料動画をキーワードマッチングで取得"""
    import json, random
    mixkit_file = os.path.join(os.path.dirname(__file__), "assets", "mixkit_videos.json")
    if not os.path.exists(mixkit_file):
        return None
    with open(mixkit_file) as f:
        videos = json.load(f)
    cat_map = {
        "technology": ["technology","computer","future","ai","tech","digital","code"],
        "business": ["business","work","office","meeting","finance"],
        "city": ["city","urban","street","building","people"],
        "science": ["science","research","lab","data","analysis"],
        "abstract": ["abstract","background","pattern","light"],
    }
    q_lower = query.lower()
    selected_cat = "technology"
    for cat, keywords in cat_map.items():
        if any(kw in q_lower for kw in keywords):
            selected_cat = cat
            break
    ids = videos.get(selected_cat, videos.get("technology", []))
    if not ids:
        return None
    video_id = random.choice(ids)
    cache_dir = Path(cache_dir) if cache_dir else Path("/tmp/pexels_cache")
    cache_dir.mkdir(exist_ok=True)
    out = cache_dir / f"mixkit_{video_id}.mp4"
    if out.exists():
        return str(out)
    for res in ["1080", "720"]:
        url = f"https://assets.mixkit.co/videos/{video_id}/{video_id}-{res}.mp4"
        try:
            r = requests.get(url, timeout=30, stream=True)
            if r.status_code == 200:
                with open(out, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"   Mixkit ✅ {video_id} ({res}p)")
                return str(out)
        except:
            continue
    return None

def pixabay_search_music(query="upbeat background", min_dur=30):
    """Pixabayからフリーミュージックをスクレイピング（APIキー不要）"""
    try:
        import urllib.request
        slug = re.sub(r"\s+", "-", query.strip().lower())
        search_url = f"https://pixabay.com/music/search/{urllib.parse.quote(slug, safe='-')}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        match = re.search(r'window\.__BOOTSTRAP_URL__\s*=\s*["\']([^"\']+)["\']', html)
        if not match:
            return []
        bootstrap_url = f"https://pixabay.com{match.group(1)}"
        req2 = urllib.request.Request(bootstrap_url, headers={**headers, "Referer": search_url})
        with urllib.request.urlopen(req2, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        tracks = []
        for item in data.get("page", {}).get("results", []):
            src = item.get("sources", {}).get("src")
            dur = item.get("duration")
            if src and dur and dur >= min_dur:
                tracks.append({"url": src, "duration": dur, "title": item.get("name", "Unknown")})
        return tracks
    except Exception:
        return []

def freesound_search_music(query="upbeat", min_dur=30):
    """FreeSound APIフォールバック（APIキー必須だが安定）"""
    fs_key = os.environ.get("FREESOUND_API_KEY", "")
    if not fs_key:
        return []
    try:
        r = requests.get("https://freesound.org/apiv2/search/text/", params={
            "query": query, "filter": f"duration:[{min_dur} TO *]", "fields": "id,name,duration,previews",
            "token": fs_key
        }, timeout=15)
        if r.status_code != 200:
            return []
        results = r.json().get("results", [])
        return [{"url": t["previews"]["preview-hq-mp3"], "duration": t.get("duration", 60), "title": t.get("name", "Unknown")} for t in results if "previews" in t and "preview-hq-mp3" in t["previews"]]
    except Exception:
        return []

def download_bgm(work_dir):
    """BGMダウンロード（Pixabay→FreeSound→SoundHelixフォールバック連鎖）"""
    bgm_path = Path(work_dir) / "bgm.mp3"
    if bgm_path.exists():
        return str(bgm_path)
    bgm_url = None
    for source_name, search_fn, query in [
        ("Pixabay", pixabay_search_music, "upbeat corporate background"),
        ("Pixabay(lo-fi)", pixabay_search_music, "lofi study background"),
        ("Pixabay(ambient)", pixabay_search_music, "ambient cinematic background"),
        ("FreeSound", freesound_search_music, "upbeat corporate"),
    ]:
        tracks = search_fn(query)
        if tracks:
            chosen = random.choice(tracks[:5])
            bgm_url = chosen["url"]
            print(f"   BGM: {source_name} → {chosen['title']} ({chosen['duration']}s)")
            break
    if not bgm_url:
        bgm_url = random.choice([
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3",
        ])
        print(f"   BGM: SoundHelix（最終フォールバック）")
    try:
        r = requests.get(bgm_url, timeout=30, stream=True)
        if r.status_code == 200:
            with open(bgm_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return str(bgm_path)
    except Exception as e:
        print(f"   BGMダウンロード失敗: {e}")
    return None

def apply_pattern_interrupt(bg_path, interrupt_type, out_path, dur):
    """パターンインタラプトエフェクト適用 (zoompan不使用, -r 30固定)"""
    _run = lambda args: subprocess.run([str(a) for a in args], capture_output=True, text=True)
    
    if interrupt_type == "zoom_punch":
        _run(["ffmpeg", "-y", "-i", bg_path,
              "-r", "30",
               "-vf", "scale=iw*1.1:ih*1.1,crop=iw/1.1:ih/1.1,scale=960:960:force_original_aspect_ratio=increase,crop=960:960",
              "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-pix_fmt", "yuv420p", "-r", "30", out_path])
    elif interrupt_type == "color_flash":
        _run(["ffmpeg", "-y", "-i", bg_path,
              "-r", "30",
               "-vf", f"fade=t=in:st=0:d=0.1:color=white,fade=t=out:st={max(dur-0.3,0)}:d=0.3,scale=960:960:force_original_aspect_ratio=increase,crop=960:960",
              "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-pix_fmt", "yuv420p", "-r", "30", out_path])
    elif interrupt_type == "cut_zoom":
        _run(["ffmpeg", "-y", "-i", bg_path,
              "-r", "30",
               "-vf", "scale=1056:1056,crop=960:960:48:48,scale=960:960:force_original_aspect_ratio=increase,crop=960:960",
              "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-pix_fmt", "yuv420p", "-r", "30", out_path])
    elif interrupt_type == "speed_ramp":
        _run(["ffmpeg", "-y", "-i", bg_path,
              "-r", "30",
               "-vf", "setpts=0.85*PTS,scale=960:960:force_original_aspect_ratio=increase,crop=960:960",
              "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-pix_fmt", "yuv420p", "-r", "30", out_path])
    else:
        _run(["ffmpeg", "-y", "-i", bg_path,
              "-r", "30",
              "-vf", "scale=960:960:force_original_aspect_ratio=increase,crop=960:960",
              "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-pix_fmt", "yuv420p", "-r", "30", out_path])

def has_audio_stream(path):
    """ffprobeで音声ストリームの有無を確認"""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
         "-of", "csv=p=0", path],
        capture_output=True, text=True)
    return bool(r.stdout.strip())

def get_video_duration(path):
    r = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path],
        capture_output=True, text=True)
    return float(r.stdout.strip())

def mix_bgm(video_path, bgm_path, out_path, voice_vol=0.85, music_vol=0.18):
    """BGMをミックス（voice 85% + music 18%）
    music_vol=0.18 (改定: 旧0.08から増強)
    音声がないvideoは音声なしのままコピー、BGM失敗時もフォールバック"""
    import shutil
    _run = lambda args: subprocess.run([str(a) for a in args], capture_output=True, text=True)
    dur = get_video_duration(video_path)

    if not has_audio_stream(video_path):
        print("   ⚠️ raw_output に音声ストリームなし → 音声なしのまま出力")
        _run(["ffmpeg", "-y", "-i", video_path,
              "-c", "copy",
              "-t", str(dur),
              out_path])
        return

    try:
        import random
        bgm_dur = get_video_duration(bgm_path)
        max_start = max(0, bgm_dur - dur - 2)
        rand_start = round(random.uniform(0, max_start), 2) if max_start > 0 else 0
        voice_end = dur
        music_fade_out = max(0, dur - 1.5)
        r = _run(["ffmpeg", "-y",
              "-i", video_path,
              "-ss", str(rand_start), "-stream_loop", "-1", "-i", bgm_path,
              "-filter_complex",
              f"[0:a]volume={voice_vol},afade=t=in:st=0:d=0.1,afade=t=out:st={voice_end-0.25}:d=0.25[voice];"
              f"[1:a]volume={music_vol},afade=t=in:st=0:d=1.0,afade=t=out:st={music_fade_out}:d=1.5[music];"
              f"[music][voice]amix=inputs=2:duration=first[out]",
              "-map", "0:v", "-map", "[out]",
              "-t", str(dur),
              "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac",
              out_path])
        if r.returncode != 0:
            raise RuntimeError(f"mix_bgm failed (stderr below):\n{r.stderr[-500:]}")
    except Exception as e:
        print(f"   ⚠️ BGMミックス失敗 ({e}) → 音声なしで出力")
        shutil.copy(video_path, out_path)

def add_loop_ending(concat_file, first_scene_path, output_path):
    """ループ構造: 最後に最初のシーンを0.5秒追加してループ感を出す"""
    _run = lambda args: subprocess.run([str(a) for a in args], capture_output=True, text=True)
    loop_clip = output_path.replace(".mp4", "_loop_clip.mp4")
    _run(["ffmpeg", "-y", "-i", first_scene_path, "-t", "0.8",
          "-vf", "fade=t=out:st=0.5:d=0.3",
          "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p", loop_clip])
    return loop_clip

def probe_dur(f):
    try:
        return get_video_duration(f)
    except:
        return 0.0

# === 設定をGitHubにプッシュ ===
if __name__ == "__main__":
    print("AI Conduit Core Framework v2.0")
    print(f"DeepSeek API: {'✅ 設定済み' if DEEPSEEK_KEY else '❌ 未設定'}")
    print(f"Google TTS: {'✅ 設定済み' if GOOGLE_TTS_KEY else '❌ 未設定'}")
    print(f"Pexels: {'✅ 設定済み' if PEXELS_KEY else '❌ 未設定'}")
    
    # DeepSeekテスト
    print("\nDeepSeekテスト中...")
    scenes = generate_script_deepseek("MadsLorentzen/ai-job-search", "17500", "Claude Codeで就活自動化", max_scenes=3)
    print(f"生成シーン数: {len(scenes)}")
    for s in scenes:
        print(f"  [{s['mood']}] {s['narration']}")
