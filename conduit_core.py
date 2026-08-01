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
    "zoom_punch",       # ズームイン + パンチ効果
    "color_flash",      # 色フラッシュ
    "text_pop",         # テキストポップアップ
    "speed_ramp",       # 速度変化
    "cut_zoom",         # カット + ズーム
    "zoom_punch_hook",  # 激しいズームパンチ（hook専用）
    "pan_left",         # 左パン
    "pan_right",        # 右パン
]

def _scenes_pass_quality(scenes):
    """自己レビュー: 生成されたscenes配列の品質チェック。
    以下いずれかに該当すればNG（False）を返す。
    - narrationが20文字未満のsceneが2つ以上ある
    - 全sceneのnarrationが同じ内容を繰り返している（先頭20文字が3つ以上一致）
    - CTAシーン（最後のscene）にAIconduitが含まれていない
    """
    if not scenes or len(scenes) < 2:
        return False
    narrations = [(s.get("narration") or "") for s in scenes]
    if sum(1 for n in narrations if len(n) < 20) >= 2:
        return False
    prefixes = [n[:20] for n in narrations]
    from collections import Counter
    if max(Counter(prefixes).values(), default=0) >= 3:
        return False
    cta = narrations[-1]
    if "AIconduit" not in cta:
        return False
    return True


def _generate_with_review(gen_fn, label, max_attempts=3):
    """自己レビューループ: 品質チェックNGならprint警告して再生成（最大2回再試行）。
    2回再試行してもNGの場合は現在の結果をそのまま返す。
    """
    scenes = None
    for attempt in range(1, max_attempts + 1):
        scenes = gen_fn()
        if scenes is not None and _scenes_pass_quality(scenes):
            return scenes
        if attempt < max_attempts:
            print(f"   ⚠️ [{label}] 自己レビュー: 品質チェックNG（{attempt}回目）→ 再生成します")
    print(f"   ⚠️ [{label}] 自己レビュー: 2回再試行しても品質NGのため現在の結果を返します")
    return scenes


def generate_script_deepseek(repo, stars, description, style="viral_hook", max_scenes=8):
    """DeepSeek APIでスクリプト生成 + 自己レビューループ（Claude品質・低コスト）"""
    print(f"[Script] DeepSeekでスクリプト生成中... (style={style})")

    def _gen_once():
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
- Scene 8 (CTA): Follow AIconduit + Share prompt

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
- FINAL SCENE (CTA) MUST mention "AIconduit" in its narration

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

    return _generate_with_review(_gen_once, "DeepSeek")

def generate_script_groq(repo, stars, description, max_scenes=8):
    """Groq APIフォールバック + 自己レビューループ"""
    def _gen_once():
        prompt = f"""Write {max_scenes} scenes for Japanese viral short video about {repo} ({stars}★) - {description}
Hook first, value middle, CTA last.
FINAL SCENE (CTA) MUST mention "AIconduit" in its narration.
Output ONLY JSON: [{{"id":1,"narration":"日本語15-30文字","caption":"4-8文字","visual_prompt":"English cinematic search","interrupt":"zoom_punch","mood":"hook"}},...]"""
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens": 900})
        resp = r.json()
        if "choices" not in resp: raise Exception(f"Groq: {resp}")
        text = resp["choices"][0]["message"]["content"].strip()
        s=text.find("["); e=text.rfind("]")+1
        if s>=0 and e>s: text=text[s:e]
        scenes = json.loads(re.sub(r"[\x00-\x1f]","",text))
        print(f"   ✅ {len(scenes)}シーン (Groq)")
        return scenes

    return _generate_with_review(_gen_once, "Groq")

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
    """Edge TTS生成。戻り値: (audio_path, list[dict{word,start_ms,duration_ms}])"""
    return tts_japanese(text, path, speed)

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
        print(f"   [Pexels] query='{query} cinematic' → HTTP {r.status_code}, try bare query")
        r = requests.get("https://api.pexels.com/videos/search", headers=headers,
            params={"query": query, "per_page": 10, "orientation": orientation}, timeout=15)
    if r.status_code != 200:
        print(f"   [Pexels] bare query='{query}' → HTTP {r.status_code}, giving up")
        return None
    videos = [v for v in r.json().get("videos", []) if v.get("duration", 0) >= 4]
    if not videos:
        print(f"   [Pexels] query='{query}' → 0 videos returned (or all <4s)")
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

    print(f"   [fetch_broll] クエリ '{query}' でPexels検索...")
    result = _pexels_download(query, cache_dir, orientation)
    if result:
        print(f"   [fetch_broll] ✅ Pexels hit: {result}")
        return result

    print(f"   [fetch_broll] ⚠️ Pexels空 → fallback_queriesで再試行")
    for fq in fallback_queries:
        result = _pexels_download(fq, cache_dir, orientation)
        if result:
            print(f"   [fetch_broll] ✅ fallback '{fq}' → {result}")
            return result

    print(f"   [fetch_broll] ⚠️ 全fallback_queries失敗 → '{fq} cinematic' で再試行")
    for fq in fallback_queries:
        result = _pexels_download(fq + " cinematic", cache_dir, orientation)
        if result:
            print(f"   [fetch_broll] ✅ fallback+cinematic '{fq}' → {result}")
            return result

    print(f"   [fetch_broll] ⚠️ Pexels全滅 → Pixabayにフォールバック")
    pixabay_result = _pixabay_download(query, cache_dir)
    if pixabay_result:
        print(f"   [fetch_broll] ✅ Pixabay hit: {pixabay_result}")
        return pixabay_result

    print(f"   [fetch_broll] ⚠️ Pixabayも空 → Mixkitにフォールバック")
    mixkit_result = _mixkit_fallback(query, cache_dir)
    if mixkit_result:
        print(f"   [fetch_broll] ✅ Mixkit hit: {mixkit_result}")
        return mixkit_result

    print(f"   [fetch_broll] ❌ 全ソース空 → Noneを返す")
    return None

# === B-roll: トピック連動スライドショー ===

def _make_slideshow(images, output_path, dur_per=3.0, size=960):
    """画像リストをスライドショー動画化（960x960, 3秒/枚）"""
    cache_dir = Path(os.path.dirname(output_path))
    cache_dir.mkdir(parents=True, exist_ok=True)
    clips = []
    for i, img in enumerate(images):
        clip = cache_dir / f"slide_{i}.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", str(img), "-t", str(dur_per),
             "-vf", f"scale={size}:{size}:force_original_aspect_ratio=increase,crop={size}:{size}",
             "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
             "-pix_fmt", "yuv420p", str(clip)],
            capture_output=True, text=True)
        if clip.exists():
            clips.append(str(clip))
    if len(clips) < 2:
        return None
    list_file = cache_dir / "slideshow_list.txt"
    with open(list_file, "w") as f:
        for p in clips:
            f.write(f"file '{p}'\n")
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c", "copy", str(output_path)],
        capture_output=True, text=True)
    if r.returncode == 0 and os.path.exists(str(output_path)):
        return str(output_path)
    return None


def images_to_slideshow(images, output_path, dur_per=3.0, size=960):
    """公開API: 画像リストをスライドショー動画化する。
    images: 画像ファイルパスのリスト
    output_path: 出力mp4パス
    dur_per: 1枚あたりの表示秒数
    size: 正方形キャンバスサイズ（px）
    Returns: 成功時 output_path（str）、失敗時 None
    """
    return _make_slideshow(images, output_path, dur_per=dur_per, size=size)


def _github_readme_images(repo, cache_dir, max_images=4):
    """GitHub公開リポジトリのREADMEから画像URLを収集しダウンロードする（認証不要）"""
    try:
        r = requests.get(
            f"https://api.github.com/repos/{repo}/readme",
            headers={"Accept": "application/vnd.github.raw+json"}, timeout=15)
        if r.status_code != 200:
            return []
        readme = r.text
        img_urls = []
        for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', readme):
            img_urls.append(m.group(1))
        for m in re.finditer(r'(?:src|srcset)="([^"]+)"', readme):
            if "srcset" in m.group(0).lower():
                first = m.group(1).split(",")[0].strip().split(" ")[0]
                img_urls.append(first)
            else:
                img_urls.append(m.group(1))
        seen = set()
        downloads = []
        for u in img_urls:
            u = u.strip().strip('"').strip()
            if (not u) or u.startswith("data:") or "{" in u:
                continue
            if u.startswith("http://") or u.startswith("https://"):
                full = u
            else:
                full = f"https://raw.githubusercontent.com/{repo}/HEAD/{u.lstrip('/')}"
            if full in seen:
                continue
            seen.add(full)
            try:
                resp = requests.get(full, timeout=20, stream=True, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code != 200:
                    continue
                probe = full.split("?")[0]
                ext = probe.split(".")[-1].lower() if "." in probe.split("/")[-1] else "png"
                if ext not in ("png", "jpg", "jpeg", "gif", "webp"):
                    ext = "png"
                out = Path(cache_dir) / f"github_{repo.split('/')[-1]}_{len(downloads)}.{ext}"
                if not out.exists():
                    with open(out, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                if out.stat().st_size > 0:
                    downloads.append(str(out))
                if len(downloads) >= max_images:
                    break
            except Exception:
                continue
        return downloads
    except Exception:
        return []


GITHUB_REPO_MAP = {
    "n8n": "n8n-io/n8n",
    "langchain": "langchain-ai/langchain",
    "claude": "anthropics/claude-code",
    "claude code": "anthropics/claude-code",
    "claude code 日本語": "anthropics/claude-code",
    "claude desktop": "anthropics/claude-desktop",
    "llamaindex": "run-llama/llama_index",
    "llama": "run-llama/llama_index",
    "autogpt": "Significant-Gravitas/AutoGPT",
    "auto gpt": "Significant-Gravitas/AutoGPT",
    "agentops": "AgentOps-AI/agentops",
    "openinterpreter": "OpenInterpreter/open-interpreter",
    "open interpreter": "OpenInterpreter/open-interpreter",
    "dify": "langgenius/dify",
    "flowise": "FlowiseAI/Flowise",
    "supabase": "supabase/supabase",
    "openhands": "All-Hands-AI/OpenHands",
    "open hands": "All-Hands-AI/OpenHands",
    "browser use": "browser-use/browser-use",
    "browser-use": "browser-use/browser-use",
    "comfyui": "comfyanonymous/ComfyUI",
    "stable diffusion": "AUTOMATIC1111/stable-diffusion-webui",
    "ai job": "MadsLorentzen/ai-job-search",
    "ai-job": "MadsLorentzen/ai-job-search",
    "ai job search": "MadsLorentzen/ai-job-search",
    "ui": "shadcn-ui/ui",
    "shadcn": "shadcn-ui/ui",
    "bazel": "bazelbuild/bazel",
    "opencv": "opencv/opencv",
    "tensorflow": "tensorflow/tensorflow",
    "pytorch": "pytorch/pytorch",
    "kubernetes": "kubernetes/kubernetes",
    "k8s": "kubernetes/kubernetes",
    "docker": "moby/moby",
    "vscode": "microsoft/vscode",
    "asdf": "asdf-vm/asdf",
    "nodejs": "nodejs/node",
    "node.js": "nodejs/node",
    "next.js": "vercel/next.js",
    "nextjs": "vercel/next.js",
    "react": "facebook/react",
    "vue": "vuejs/core",
    "svelte": "sveltejs/svelte",
    "fastapi": "fastapi/fastapi",
    "flask": "pallets/flask",
    "django": "django/django",
    "rust": "rust-lang/rust",
    "golang": "golang/go",
    "android": "android/architecture-samples",
    "flutter": "flutter/flutter",
    "remotion": "remotion-dev/remotion",
    "opencode": "anomalyco/opencode",
    "ruff": "astral-sh/ruff",
    "pyenv": "pyenv/pyenv",
    "uv": "astral-sh/uv",
    "deepse": "deepseek-ai/DeepSeek-V3",
    "deepseek": "deepseek-ai/DeepSeek-V3",
    "llama.cpp": "ggml-org/llama.cpp",
    "ollama": "ollama/ollama",
    "openai": "openai/openai-python",
    "whisper": "openai/whisper",
    "huggingface": "huggingface/transformers",
    "transformers": "huggingface/transformers",
    "gitlens": "gitkraken/vscode-gitlens",
    "brew": "Homebrew/brew",
    "homebrew": "Homebrew/brew",
}

def _match_github_repo(topic):
    """topicから紹介対象のGitHubリポジトリを特定する（GITHUB_REPO_MAP参照・大文字小文字無視）"""
    t = (topic or "").lower()
    for key, repo in GITHUB_REPO_MAP.items():
        if key in t:
            return repo
    if t.count("/") == 1 and "/" in t:
        return t.strip()
    return None


# === ツール名 → Official URL マッピング（fetch_broll_playwright用） ===
TOOL_URL_MAP = {
    "n8n": "https://n8n.io",
    "langchain": "https://www.langchain.com",
    "claude": "https://claude.ai",
    "claude code": "https://docs.anthropic.com/en/docs/claude-code",
    "claude desktop": "https://claude.ai/download",
    "llamaindex": "https://www.llamaindex.ai",
    "llama": "https://www.llama.com",
    "autogpt": "https://agpt.co",
    "auto gpt": "https://agpt.co",
    "agentops": "https://agentops.ai",
    "openinterpreter": "https://openinterpreter.com",
    "open interpreter": "https://openinterpreter.com",
    "dify": "https://dify.ai",
    "flowise": "https://flowiseai.com",
    "supabase": "https://supabase.com",
    "openhands": "https://www.all-hands.dev",
    "open hands": "https://www.all-hands.dev",
    "browser use": "https://www.browser-use.com",
    "browser-use": "https://www.browser-use.com",
    "comfyui": "https://www.comfy.org",
    "stable diffusion": "https://stability.ai",
    "ui": "https://ui.shadcn.com",
    "shadcn": "https://ui.shadcn.com",
    "bazel": "https://bazel.build",
    "opencv": "https://opencv.org",
    "tensorflow": "https://www.tensorflow.org",
    "pytorch": "https://pytorch.org",
    "kubernetes": "https://kubernetes.io",
    "k8s": "https://kubernetes.io",
    "docker": "https://www.docker.com",
    "vscode": "https://code.visualstudio.com",
    "asdf": "https://asdf-vm.com",
    "nodejs": "https://nodejs.org",
    "node.js": "https://nodejs.org",
    "next.js": "https://nextjs.org",
    "nextjs": "https://nextjs.org",
    "react": "https://react.dev",
    "vue": "https://vuejs.org",
    "svelte": "https://svelte.dev",
    "fastapi": "https://fastapi.tiangolo.com",
    "flask": "https://flask.palletsprojects.com",
    "django": "https://www.djangoproject.com",
    "rust": "https://www.rust-lang.org",
    "golang": "https://go.dev",
    "android": "https://www.android.com",
    "flutter": "https://flutter.dev",
    "remotion": "https://www.remotion.dev",
    "opencode": "https://opencode.ai",
    "ruff": "https://docs.astral.sh/ruff",
    "pyenv": "https://github.com/pyenv/pyenv",
    "uv": "https://docs.astral.sh/uv",
    "deepseek": "https://www.deepseek.com",
    "llama.cpp": "https://github.com/ggml-org/llama.cpp",
    "ollama": "https://ollama.com",
    "openai": "https://openai.com",
    "whisper": "https://openai.com/index/whisper",
    "huggingface": "https://huggingface.co",
    "transformers": "https://huggingface.co/docs/transformers",
    "gitlens": "https://gitkraken.com/gitlens",
    "brew": "https://brew.sh",
    "homebrew": "https://brew.sh",
}


def fetch_broll_playwright(tool_name, cache_dir, direct_url=None):
    """ツールの公式HPをヘッドレスChromiumでスクリーンショット → Ken Burns動画化。

    direct_urlが指定された場合はそのURLを直接使用。
    それ以外はTOOL_URL_MAPからtool_nameで検索。
    失敗時は None を返す。
    """
    try:
        if not tool_name and not direct_url:
            return None
        url = direct_url
        if not url:
            t = tool_name.lower()
            for key, u in TOOL_URL_MAP.items():
                if key in t:
                    url = u
                    break
        if not url:
            return None

        try:
            import playwright
        except ImportError:
            print(f"   ⚠️ [fetch_broll_playwright] Playwrightが未インストール → None")
            return None

        if cache_dir is None:
            cache_dir = Path("/tmp/broll_topic_cache")
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        async def _capture():
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 900},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="ja-JP",
                )
                page = await context.new_page()
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(3000)
                except Exception:
                    pass
                safe_name = re.sub(r"[^\w]", "_", (tool_name or "direct"))[:20]
                shot = Path(cache_dir) / f"playwright_{safe_name}.png"
                await page.screenshot(path=str(shot), full_page=False)
                await browser.close()
                size = shot.stat().st_size if shot.exists() else 0
                print(f"   [DEBUG] Playwright screenshot size={size} url={url}")
                return str(shot) if shot.exists() and size > 50000 else None

        import asyncio
        shot = asyncio.run(_capture())
        if not shot:
            return None
        shot_size = os.path.getsize(shot) if os.path.exists(shot) else 0
        print(f"   [DEBUG] Playwright PNG: {shot} size={shot_size}")
        safe = re.sub(r"[^\w]", "_", tool_name or "direct")[:20]
        out = str(Path(cache_dir) / f"playwright_kenburns_{safe}.mp4")
        result = _make_kenburns(shot, out, dur=8.0)
        print(f"   [DEBUG] kenburns result: {result} size={os.path.getsize(result) if result and os.path.exists(result) else 0}")
        if result and os.path.exists(result):
            print(f"   [fetch_broll_playwright] OK: {result}")
            return result
        return None
        return None
        return None
    except Exception as e:
        print(f"   ⚠️ [fetch_broll_playwright] 例外: {e} → None")
        return None


def _fetch_github_readme_images(repo_name, cache_dir=None, max_images=2):
    """GitHubのREADMEから実際のツール画像を取得する（1〜2枚）

    Args:
        repo_name: 'owner/repo' 形式のリポジトリ名
        cache_dir: 画像保存先ディレクトリ（デフォルト /tmp/broll_topic_cache）
        max_images: 取得する最大画像数
    Returns:
        ダウンロード済み画像ファイルパスのリスト
    """
    if cache_dir is None:
        cache_dir = Path("/tmp/broll_topic_cache")
    return _github_readme_images(repo_name, cache_dir, max_images=max_images)


def _make_kenburns(image, output_path, dur=3.0, size=960):
    """単一画像をKen Burns動画（ズームイン+ドリフト）に変換する。
    shortsmith方式: MoviePy ImageClip + resize(lambda t) でzoompan不使用。
    失敗時はffmpegシンプル変換にフォールバック。
    Returns: 成功時 output_path (str)、失敗時 None
    """
    try:
        import numpy as np
        from PIL import Image as PILImage
        # moviepy 2.x系のimport
        try:
            from moviepy import ImageClip, ColorClip, CompositeVideoClip
        except ImportError:
            from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip

        target_w, target_h = size, size
        with PILImage.open(str(image)) as handle:
            img = handle.convert("RGB")
            scale = max(target_w / img.width, target_h / img.height) * 1.15
            img = img.resize((int(img.width * scale), int(img.height * scale)), PILImage.LANCZOS)
            frame = np.array(img)

        base = ImageClip(frame).with_duration(dur)
        zoom_start = 1.0
        zoom_end = 1.08
        base = base.resized(lambda t: zoom_start + (zoom_end - zoom_start) * (t / max(dur, 0.1)))

        max_dx = min(60, max(0, base.w - target_w) // 4)
        max_dy = min(60, max(0, base.h - target_h) // 4)
        cx = -((base.w - target_w) / 2)
        cy = -((base.h - target_h) / 2)
        moving = base.with_position(
            lambda t: (
                cx + max_dx * 0.3 * (t / max(dur, 0.1)),
                cy + max_dy * 0.2 * (t / max(dur, 0.1)),
            )
        )
        backdrop = ColorClip((target_w, target_h), color=(0, 0, 0)).with_duration(dur)
        comp = CompositeVideoClip([backdrop, moving], size=(target_w, target_h)).with_duration(dur)
        comp.write_videofile(
            str(output_path),
            fps=30, codec="libx264", preset="fast",
            ffmpeg_params=["-crf", "22", "-pix_fmt", "yuv420p"],
            logger=None, audio=False
        )
        if os.path.exists(str(output_path)) and os.path.getsize(str(output_path)) > 10000:
            return str(output_path)
        print(f"   ⚠️ Ken Burns(MoviePy)出力が小さすぎる")
    except Exception as e:
        print(f"   ⚠️ Ken Burns(MoviePy)失敗: {e}")

    # フォールバック: ffmpegシンプル変換
    try:
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(image),
            "-vf", f"scale={size}:{size}:force_original_aspect_ratio=increase,crop={size}:{size}",
            "-t", str(dur), "-r", "30", "-c:v", "libx264", "-preset", "fast",
            "-crf", "22", "-pix_fmt", "yuv420p", str(output_path),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(str(output_path)):
            return str(output_path)
        print(f"   ⚠️ Ken Burns(ffmpeg)失敗: {r.stderr[-200:]}")
    except Exception as e2:
        print(f"   ⚠️ Ken Burns(ffmpeg)例外: {e2}")
    return None
def _extract_english_query(visual_query):
    """visual_queryから英語部分のみ抽出する。短すぎる場合は技術系デフォルト。
    Returns: 簡潔な英語検索クエリ（str）
    """
    if not visual_query:
        return "technology abstract"
    en = " ".join(re.findall(r"[A-Za-z][A-Za-z0-9 .\-_/]*", visual_query)).strip()
    en = re.sub(r"\s+", " ", en).strip()
    if len(en) < 3:
        en = "technology abstract"
    tokens = [t for t in re.split(r"[\s,._\-/]+", en) if t]
    stopwords = {"a", "an", "the", "and", "or", "of", "for", "to", "with", "on", "in", "it", "that", "this", "is", "are"}
    clean = [t for t in tokens if t.lower() not in stopwords][:4]
    if not clean:
        clean = ["technology", "abstract"]
    return " ".join(clean)


def _make_black_screen(output_path, dur=8.0, size=960):
    """最終フォールバック: 真っ黒な960x960動画を生成する。"""
    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=960x960:d=%s" % dur,
            "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-pix_fmt", "yuv420p",
            str(output_path),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(str(output_path)):
            return str(output_path)
    except Exception as e:
        print(f"   ⚠️ 黒画面生成失敗: {e}")
    return None


def fetch_broll_from_topic(topic, visual_query, cache_dir=None, direct_url=None):
    """B-roll取得（優先順位でフォールバック）。

    優先順位:
      1. Playwrightで公式HPスクリーンショット → Ken Burns動画（最優先）
         direct_urlが指定された場合はそのURLを直接使用
      2. GitHub READMEの実際のツール画像 → Ken Burns動画
      3. Pexelsでシンプルな英語クエリ検索（フォールバック1）
      4. 黒画面（最終フォールバック）

    Returns: 動画ファイルパス or None
    """
    if cache_dir is None:
        cache_dir = Path("/tmp/broll_topic_cache")
    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    # 1. Playwrightで公式HP撮影 → Ken Burns動画（最優先）
    playwright_shot = fetch_broll_playwright(topic, cache_dir, direct_url=direct_url)
    if playwright_shot:
        print(f"   ✅ Playwright公式HP → Ken Burns動画: {playwright_shot}")
        return playwright_shot

    # 2. GitHub READMEの実画像 → Ken Burns動画
    repo = _match_github_repo(topic)
    if repo:
        print(f"   [fetch_broll_from_topic] GitHub README画像取得: {repo}")
        gh_images = _fetch_github_readme_images(repo, cache_dir, max_images=2)
        if gh_images:
            img = gh_images[0]
            out = Path(cache_dir) / f"{repo.split('/')[-1]}_kenburns.mp4"
            if not out.exists() or out.stat().st_size == 0:
                result = _make_kenburns(img, out, dur=8.0)
            else:
                result = str(out)
            if result and os.path.exists(result):
                print(f"   ✅ GitHub README → Ken Burns動画: {result}")
                return result
            print(f"   ⚠️ GitHub README画像のKen Burns変換に失敗 → フォールバック")

    # 3. Pexelsでシンプルな英語クエリ（フォールバック1）
    en_query = _extract_english_query(visual_query)
    print(f"   [fetch_broll_from_topic] Pexels検索: '{en_query} cinematic'")
    result = _pexels_download(en_query, cache_dir)
    if result:
        print(f"   ✅ Pexels hit: {result}")
        return result
    print(f"   [fetch_broll_from_topic] ⚠️ Pexels空 → 黒画面へフォールバック")

    # 4. 黒画面（最終フォールバック）
    out = Path(cache_dir) / "black_screen.mp4"
    if not out.exists() or out.stat().st_size == 0:
        result = _make_black_screen(out, dur=8.0)
    else:
        result = str(out)
    if result and os.path.exists(result):
        print(f"   ✅ 黒画面B-roll: {result}")
        return result

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

def _download_mixkit_music(mood="default", cache_dir=None):
    """Mixkit無料音楽をダウンロード（209件・APIキー不要）"""
    import json, random
    music_file = os.path.join(os.path.dirname(__file__), "assets", "mixkit_music.json")
    if not os.path.exists(music_file):
        return None
    with open(music_file) as f:
        music_db = json.load(f)
    
    mood_cat = {
        "hook": "electronic",
        "interrupt": "hip-hop", 
        "value": "corporate",
        "cta": "cinematic",
        "default": "cinematic",
    }
    cat = mood_cat.get(mood, "cinematic")
    ids = music_db.get(cat, music_db.get("cinematic", []))
    if not ids:
        return None
    
    music_id = random.choice(ids)
    cache_path = Path(cache_dir) if cache_dir else Path("/tmp/bgm_cache")
    cache_path.mkdir(exist_ok=True)
    out = cache_path / f"mixkit_music_{music_id}.mp3"
    
    if out.exists():
        return str(out)
    
    url = f"https://assets.mixkit.co/music/{music_id}/{music_id}.mp3"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30, stream=True)
        if r.status_code == 200:
            with open(out, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"   Mixkit音楽 ✅ {music_id}")
            return str(out)
    except Exception as e:
        print(f"   Mixkit音楽失敗: {e}")
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
    """BGMダウンロード（Mixkit→Pixabay→FreeSound→SoundHelixフォールバック連鎖）
    Returns (bgm_path, bpm) — bpmを同時に推定して返す
    """
    bgm_path = Path(work_dir) / "bgm.mp3"
    if bgm_path.exists():
        bpm = estimate_bpm_simple(str(bgm_path))
        return str(bgm_path), bpm
    
    # Mixkit音楽を最初に試す（無料・高品質・APIキー不要）
    mixkit_bgm = _download_mixkit_music(cache_dir=work_dir)
    if mixkit_bgm:
        bpm = estimate_bpm_simple(mixkit_bgm)
        print(f"   BPM: {bpm}")
        return mixkit_bgm, bpm
    
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
            bpm = estimate_bpm_simple(str(bgm_path))
            print(f"   BPM: {bpm}")
            return str(bgm_path), bpm
    except Exception as e:
        print(f"   BGMダウンロード失敗: {e}")
    return None, 120.0

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
    elif interrupt_type == "zoom_punch_hook":
        _run(["ffmpeg", "-y", "-i", bg_path,
              "-r", "30",
              "-vf", "scale=iw*1.25:ih*1.25,crop=iw/1.25:ih/1.25,scale=960:960:force_original_aspect_ratio=increase,crop=960:960",
              "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-pix_fmt", "yuv420p", "-r", "30", out_path])
    elif interrupt_type == "pan_left":
        _run(["ffmpeg", "-y", "-i", bg_path,
              "-r", "30",
              "-vf", "scale=1280:960,crop=960:960:0:0",
              "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-pix_fmt", "yuv420p", "-r", "30", out_path])
    elif interrupt_type == "pan_right":
        _run(["ffmpeg", "-y", "-i", bg_path,
              "-r", "30",
              "-vf", "scale=1280:960,crop=960:960:320:0",
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

def mix_bgm(video_path, bgm_path, out_path, voice_vol=0.85, music_vol=0.08):
    """BGMをミックス（voice 85% + music 18%）
    music_vol=0.08 (改定: 旧0.08から増強)
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

def add_sfx_to_scene(input_path, out_path, mood="default", dur=None, add_cut=True, sfx_dir=None):
    """シーン完成動画にSFXを追加（BGMと別トラックで管理）。

    - mood == "hook"      : assets/sfx/zoom_hit.wav を動画冒頭0.0sに追加
    - mood == "interrupt" : assets/sfx/whoosh.wav  を動画冒頭0.0sに追加
    - シーン切替時(add_cut)  : assets/sfx/cut.wav   を動画末尾に追加
    - SFXファイルが存在しない場合はスキップ（音声なし時もそのまま出力）
    Returns: 出力パス（out_path）
    """
    _run = lambda args: subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if sfx_dir is None:
        sfx_dir = Path(__file__).parent / "assets" / "sfx"
    if dur is None:
        dur = get_video_duration(input_path)

    # --- 使用するSFXキューの決定（ファイル存在時のみ）---
    cues = []  # [(sfx_path, 開始位置秒)]
    lead = {"hook": "zoom_hit.wav", "interrupt": "whoosh.wav"}.get(mood)
    if lead:
        p = Path(sfx_dir) / lead
        if p.exists():
            cues.append((str(p), 0.0))
    if add_cut:
        cut_p = Path(sfx_dir) / "cut.wav"
        if cut_p.exists():
            try:
                cut_dur = get_video_duration(str(cut_p))
            except Exception:
                cut_dur = 0.2
            cues.append((str(cut_p), max(0.0, dur - cut_dur)))

    if not cues or not has_audio_stream(input_path):
        # SFXなし or 元音声なし → そのままコピー
        r = _run(["ffmpeg", "-y", "-i", input_path, "-c", "copy", "-t", str(dur), out_path])
        if r.returncode != 0:
            import shutil; shutil.copy(input_path, out_path)
        return out_path

    try:
        cmd = ["ffmpeg", "-y", "-i", input_path]
        for p, _pos in cues:
            cmd += ["-i", p]
        parts = ["[0:a]aformat=channel_layouts=stereo[voice];"]
        for i, (p, pos) in enumerate(cues):
            adelay_ms = int(pos * 1000)
            parts.append(
                f"[{i + 1}:a]aformat=channel_layouts=stereo,volume=1.0,"
                f"adelay={adelay_ms}|{adelay_ms}[sfx{i}];"
            )
        tags = "".join(f"[sfx{i}]" for i in range(len(cues)))
        parts.append(f"[voice]{tags}amix=inputs={len(cues) + 1}:duration=first:normalize=0[out]")
        cmd += ["-filter_complex", "".join(parts),
                "-map", "0:v", "-map", "[out]",
                "-t", str(dur), "-c:v", "copy", "-c:a", "aac",
                out_path]
        r = _run(cmd)
        if r.returncode != 0:
            raise RuntimeError(f"add_sfx_to_scene:\n{r.stderr[-400:]}")
        print(f"   🔊 SFX追加: mood={mood}, cues={[os.path.basename(p) for p, _ in cues]}")
    except Exception as e:
        print(f"   ⚠️ add_sfx_to_scene失敗 ({e}) → 元音声のまま出力")
        import shutil; shutil.copy(input_path, out_path)
    return out_path


def apply_zoom_pulse(input_path, out_path, dur=None, fps=30):
    """ズームパルス: シーン冒頭1秒（30フレーム）で1.0→1.06倍にゆっくりズームイン。

    zoompan: on<=30(最初の1秒)は1.0+on*0.002で徐々にズーム、以降は1.06倍で静止。
    既存のscale/cropされた960x960入力に適用する。
    Returns: 出力パス（out_path）
    """
    _run = lambda args: subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if dur is None:
        dur = get_video_duration(input_path)
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf",
        "zoompan=z='if(lte(on,30),1.0+on*0.002,1.06)':d=1:"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=960x960:fps=%d" % fps,
        "-r", str(fps), "-t", str(dur),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-an", out_path,
    ]
    r = _run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"apply_zoom_pulse:\n{r.stderr[-400:]}")
    return out_path


def beat_sync_bgm(video_path, bgm_path, out_path, voice_vol=0.85, music_vol=0.08, bpm=None):
    """BGMビート同期（シンプル版）: mix_bgm()の代わりに使用。

    estimate_bpm_simple()でBPMを取得し、そのビート周期に合わせてBGMボリュームを
    動的に変化させる（ダッキング）。
    実装を複雑化しないため、BPM→1拍の長さから正弦波ベースの音量エンベロープを
    volumeフィルタ（eval=frame, t変数）で簡易適用する。
    失敗時はmix_bgm()にフォールバック。
    """
    import shutil
    _run = lambda args: subprocess.run([str(a) for a in args], capture_output=True, text=True)
    dur = get_video_duration(video_path)
    if bpm is None:
        bpm = estimate_bpm_simple(bgm_path)
    if not bpm or bpm <= 0:
        bpm = 120.0
    beat_dur = 60.0 / bpm

    if not has_audio_stream(video_path):
        print("   ⚠️ raw_output に音声ストリームなし → 音声なしのまま出力")
        _run(["ffmpeg", "-y", "-i", video_path, "-c", "copy", "-t", str(dur), out_path])
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
              f"[music]volume='0.6+0.4*abs(sin(2*PI*t/{beat_dur}))':eval=frame[duck];"
              f"[duck][voice]amix=inputs=2:duration=first[out]",
              "-map", "0:v", "-map", "[out]",
              "-t", str(dur),
              "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac",
              out_path])
        if r.returncode != 0:
            raise RuntimeError(f"beat_sync_bgm failed:\n{r.stderr[-500:]}")
        print(f"   🎧 BGMビート同期適用 ({bpm:.0f} BPM, 1拍={beat_dur:.2f}s)")
    except Exception as e:
        print(f"   ⚠️ beat_sync_bgm失敗 ({e}) → 通常mix_bgmでフォールバック")
        mix_bgm(video_path, bgm_path, out_path, voice_vol=voice_vol, music_vol=music_vol)

def add_loop_ending(concat_file, first_scene_path, output_path):
    """ループ構造: 最後に最初のシーンを0.5秒追加してループ感を出す"""
    _run = lambda args: subprocess.run([str(a) for a in args], capture_output=True, text=True)
    loop_clip = output_path.replace(".mp4", "_loop_clip.mp4")
    _run(["ffmpeg", "-y", "-i", first_scene_path, "-t", "0.8",
          "-vf", "fade=t=out:st=0.5:d=0.3",
          "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p", loop_clip])
    return loop_clip

def generate_lut_cube(style="cinematic", size=33):
    """.cube LUTファイルを生成（ffmpeg lut3dフィルター用）
    スタイル: cinematic, warm, cool, vintage
    仕様: 33x33x33 3D LUT (Adobe Cube format)
    """
    size = max(16, min(65, size))
    lut = []
    for b in range(size):
        for g in range(size):
            for r_ in range(size):
                nr = r_ / (size - 1)
                ng = g / (size - 1)
                nb = b / (size - 1)
                if style == "cinematic":
                    out_r = nr ** (1/2.2)
                    out_g = ng ** (1/2.2)
                    out_b = nb ** (1/2.2)
                    contrast = 1.15
                    out_r = (out_r - 0.5) * contrast + 0.5
                    out_g = (out_g - 0.5) * contrast + 0.5
                    out_b = (out_b - 0.5) * contrast + 0.5
                    out_r += 0.02
                    out_b -= 0.02
                elif style == "warm":
                    out_r = nr ** 0.95
                    out_g = ng ** 0.98
                    out_b = nb ** 1.05
                    out_r += 0.04
                    out_g += 0.01
                    out_b -= 0.02
                elif style == "cool":
                    out_r = nr ** 1.05
                    out_g = ng ** 0.98
                    out_b = nb ** 0.92
                    out_r -= 0.03
                    out_g += 0.01
                    out_b += 0.05
                elif style == "vintage":
                    out_r = nr * 0.9 + 0.05
                    out_g = ng * 0.85 + 0.03
                    out_b = nb * 0.7 + 0.02
                    sepia = out_r * 0.393 + out_g * 0.769 + out_b * 0.189
                    out_r = out_r * 0.8 + sepia * 0.2
                    out_g = out_g * 0.85 + sepia * 0.15
                    out_b = out_b * 0.7 + sepia * 0.3
                else:
                    out_r, out_g, out_b = nr, ng, nb
                out_r = max(0.0, min(1.0, out_r))
                out_g = max(0.0, min(1.0, out_g))
                out_b = max(0.0, min(1.0, out_b))
                lut.append(f"{out_r:.6f} {out_g:.6f} {out_b:.6f}")
    lines = [
        "TITLE \"OpenMontage LUT\"",
        f"LUT_3D_SIZE {size}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
        "",
    ] + lut
    return "\n".join(lines)

def apply_lut_to_video(input_path, output_path, style="cinematic", dur=None):
    """LUTカラーグレーディングを動画に適用"""
    lut_cube = generate_lut_cube(style)
    lut_path = output_path.replace(".mp4", ".cube")
    with open(lut_path, "w") as f:
        f.write(lut_cube)
    cmd = ["ffmpeg", "-y", "-i", input_path,
           "-vf", f"lut3d={lut_path}",
           "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p"]
    if dur:
        cmd.extend(["-t", str(dur)])
    cmd.append(output_path)
    subprocess.run([str(a) for a in cmd], capture_output=True, text=True, check=True)

def estimate_bpm_simple(audio_path):
    """BPM推定（librosa不使用・軽量版）
    ffmpeg ashowinfo + 波形エンベロープ解析でBPMを推定。
    失敗時はデフォルト120BPMを返す。
    """
    import struct, math
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,sample_rate",
             "-of", "json", audio_path],
            capture_output=True, text=True, timeout=10
        )
        info = json.loads(r.stdout)
        streams = info.get("streams", [])
        if not streams:
            return 120.0
        sr = int(streams[0].get("sample_rate", 44100))
        tmp_wav = audio_path + ".bpm_tmp.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path,
             "-ac", "1", "-ar", str(sr), "-t", "30",
             "-f", "wav", tmp_wav],
            capture_output=True, text=True, timeout=30
        )
        if not os.path.exists(tmp_wav):
            return 120.0
        with open(tmp_wav, "rb") as f:
            f.read(44)
            raw = f.read()
        samples = struct.unpack(f"<{len(raw)//2}h", raw)
        samples = [float(s) / 32768.0 for s in samples]

        hop = int(sr * 0.02)
        env = []
        for i in range(0, len(samples) - hop, hop):
            seg = samples[i:i + hop]
            env.append(math.sqrt(sum(s * s for s in seg) / max(len(seg), 1)))

        min_bpm, max_bpm = 60, 180
        min_interval = int(60.0 / max_bpm * sr / hop)
        max_interval = int(60.0 / min_bpm * sr / hop)

        best_bpm = 120.0
        best_score = 0.0
        for lag in range(min_interval, max_interval + 1):
            score = 0.0
            for i in range(0, len(env) - lag, lag):
                score += env[i] * env[i + lag]
            if score > best_score:
                best_score = score
                best_bpm = 60.0 / (lag * hop / sr)

        try:
            os.remove(tmp_wav)
        except:
            pass

        best_bpm = max(min_bpm, min(max_bpm, best_bpm))
        return round(best_bpm, 1)
    except Exception:
        return 120.0

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
