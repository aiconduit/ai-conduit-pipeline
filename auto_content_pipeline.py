#!/usr/bin/env python3
"""
AI Conduit 完全自動コンテンツ生成パイプライン
GitHubリポジトリ名を入力するだけで投稿可能な動画を生成

使い方:
    python3 auto_content_pipeline.py "MadsLorentzen/ai-job-search" "17500" "Claude Codeで就活自動化"
"""
import sys, json, os, subprocess, requests, random
from pathlib import Path

# === 設定 ===
GROQ_API_KEY = "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"
PEXELS_API_KEY = "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW"
ROOT_DIR = Path(__file__).parent
COMPOSER_DIR = ROOT_DIR / "remotion-composer"
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PROPS_DIR = COMPOSER_DIR / "public" / "demo-props"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
NARRATION_DIR = Path("/tmp/narration")

for d in [OUTPUT_DIR, PROPS_DIR, PEXELS_CACHE, NARRATION_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# === Step 1: Groqでスクリプト生成 ===
def generate_script(repo: str, stars: str, description: str) -> dict:
    print(f"[1/5] 📝 スクリプト生成中... ({repo})")
    prompt = f"""あなたはAI・GitHubトレンド紹介SNSチャンネルのスクリプトライターです。
日本語で、エンジニア向けの短尺動画(25秒)のスクリプトを作成してください。

リポジトリ: {repo}
スター数: {stars}
概要: {description}

構造: Hook(2秒) → What(5秒) → How(10秒) → Why(5秒) → CTA(3秒)
- Hook: スター数や急上昇という数字で注目を引く
- CTA: コメントにconduitと入れてくれた方にテンプレートプレゼント
- 3人称、パンチのある日本語

以下のJSON形式のみ出力:
{{"hook":"...","what":"...","how":"...","why":"...","cta":"...","narration_full":"...","pexels_keywords":["...","...","..."],"hook_text_overlay":"...","title_text":"..."}}"""

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
    )
    text = r.json()["choices"][0]["message"]["content"].strip()
    if "```" in text:
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

# === Step 2: Pexelsでb-roll取得 ===
def fetch_pexels(query: str, count: int = 1) -> list[str]:
    print(f"   🎬 Pexels検索: '{query}'")
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 5, "orientation": "portrait", "size": "medium"}
    r = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=10)
    if r.status_code != 200:
        return []
    videos = r.json().get("videos", [])
    valid = [v for v in videos if v.get("duration", 0) >= 4]
    if not valid:
        return []
    selected = random.sample(valid, min(count, len(valid)))
    paths = []
    for v in selected:
        files = sorted(v.get("video_files", []), key=lambda x: x["width"] * x["height"], reverse=True)
        if not files:
            continue
        url = files[0]["link"]
        safe = query.replace(" ", "_")[:25]
        fname = f"{safe}_{v['id']}.mp4"
        fpath = PEXELS_CACHE / fname
        if not fpath.exists():
            resp = requests.get(url, stream=True, timeout=30)
            with open(fpath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
        paths.append(str(fpath))
    return paths

# === Step 3: Remotion props生成(縦型9:16) ===
def build_props(script: dict, repo: str, stars: str, pexels_paths: list) -> dict:
    accent = "#22D3EE"
    bg = "#0B0F1A"
    cuts = [
        # フック: スター数アテンション
        {
            "id": "attention",
            "source": "",
            "type": "stat_counter",
            "in_seconds": 0,
            "out_seconds": 3,
            "title": "今月のGitHubトレンド急上昇",
            "accentColor": "#F59E0B",
            "backgroundColor": bg,
            "stats": [
                {"label": "⭐ Stars", "value": int(stars.replace(",","")), "suffix": "", "color": "#F59E0B"},
            ]
        },
        # タイトル
        {
            "id": "title",
            "source": "",
            "type": "cinematic_title",
            "in_seconds": 3,
            "out_seconds": 6,
            "text": script.get("title_text", repo.split("/")[-1]),
            "subtitle": repo,
            "accentColor": accent,
            "backgroundColor": bg
        },
    ]

    # B-roll シーン
    t = 6
    for i, ppath in enumerate(pexels_paths[:2]):
        scene_text = [script.get("what",""), script.get("how","")][i] if i < 2 else ""
        cuts.append({
            "id": f"broll_{i}",
            "source": ppath,
            "type": "pexels_scene",
            "in_seconds": t,
            "out_seconds": t + 7,
            "text": scene_text[:40] if scene_text else None,
            "textPosition": "bottom",
            "accentColor": accent,
        })
        t += 7

    # ターミナルデモ(Pexelsが足りない場合)
    if len(pexels_paths) < 2:
        cuts.append({
            "id": "terminal",
            "source": "",
            "type": "terminal_scene",
            "in_seconds": t,
            "out_seconds": t + 8,
            "terminalTitle": repo.split("/")[-1],
            "prompt": "$",
            "accentColor": accent,
            "backgroundColor": bg,
            "steps": [
                {"kind": "cmd", "text": f"git clone github.com/{repo}", "typeSpeed": 0.02},
                {"kind": "out", "text": f"+ {repo.split('/')[-1]} cloned"},
                {"kind": "pill", "text": "AI powered ✨", "color": accent, "durationSeconds": 2},
            ]
        })
        t += 8

    # CTA
    cuts.append({
        "id": "cta",
        "source": "",
        "type": "subscribe_cta",
        "in_seconds": t,
        "out_seconds": t + 5,
        "handle": "@AI_Conduit",
        "message": "毎日AIトレンドを紹介中",
        "ctaText": "コメントに「conduit」でテンプレ無料プレゼント",
        "accentColor": accent,
        "backgroundColor": bg
    })

    return {"theme": "flat-motion-graphics", "cuts": cuts, "overlays": []}

# === Step 4: Remotionレンダリング(縦型) ===
def render_video(name: str, props: dict) -> Path:
    props_path = PROPS_DIR / f"{name}.json"
    with open(props_path, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)
    output_path = OUTPUT_DIR / f"{name}.mp4"
    print(f"[3/5] 🎬 レンダリング中... → {output_path.name}")
    subprocess.run([
        "npx", "remotion", "render", "src/index.tsx", "ExplainerVertical",
        str(output_path), "--props", str(props_path), "--codec", "h264",
    ], cwd=COMPOSER_DIR, check=True, capture_output=True)
    return output_path

# === Step 5: Edge-TTSナレーション合成 ===
def add_narration(video_path: Path, narration: str, name: str) -> Path:
    mp3_path = NARRATION_DIR / f"{name}.mp3"
    final_path = OUTPUT_DIR / f"{name}_narrated.mp4"
    print(f"[4/5] 🎙️ ナレーション生成中...")
    subprocess.run(["edge-tts", "--voice", "ja-JP-KeitaNeural", "--text", narration, "--write-media", str(mp3_path)], check=True)
    print(f"[5/5] 🔗 動画合成中... → {final_path.name}")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video_path), "-i", str(mp3_path),
        "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest",
        str(final_path)
    ], check=True, capture_output=True)
    return final_path

# === メイン ===
def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "MadsLorentzen/ai-job-search"
    stars = sys.argv[2] if len(sys.argv) > 2 else "17500"
    description = sys.argv[3] if len(sys.argv) > 3 else "GitHubトレンドリポジトリ"
    name = repo.split("/")[-1]

    print(f"\n🚀 AI Conduit 自動コンテンツ生成パイプライン")
    print(f"   リポジトリ: {repo} ({stars} stars)\n")

    # Step 1: スクリプト生成
    script = generate_script(repo, stars, description)
    print(f"   ✅ スクリプト生成完了")

    # Step 2: Pexels B-roll取得
    print(f"[2/5] 🎬 B-roll素材取得中...")
    pexels_paths = []
    for kw in script.get("pexels_keywords", ["programming", "technology"])[:2]:
        paths = fetch_pexels(kw, count=1)
        pexels_paths.extend(paths)

    # Step 3: props生成 & レンダリング
    props = build_props(script, repo, stars, pexels_paths)
    video_path = render_video(name, props)

    # Step 4: ナレーション合成
    narration = script.get("narration_full", "")
    final_path = add_narration(video_path, narration, name)

    print(f"\n✅ 完成: {final_path}")
    print(f"\n📋 キャプション案:")
    print(f"{script.get('narration_full','')}")
    print(f"\n#AI #GitHub #GitHubTrending #AIツール #エンジニア")

if __name__ == "__main__":
    main()
