#!/usr/bin/env python3
"""
content_plan.json の最初のトピックを読み、ffmpeg_pipeline_v1_improved.py の
合成ロジックを流用して動画を生成し、output/auto_log.json に記録する。
"""
import sys, json, os, re, random
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))
from conduit_core import tts_japanese, fetch_broll_cinematic, download_bgm, probe_dur, mix_bgm
from ffmpeg_pipeline_v1_improved import (
    WORK_DIR, OUTPUT_DIR, PEXELS_CACHE, CHAR_PATH, FONT_PATHS,
    MOOD_COLORS, compose_scene as _original_compose_scene,
    gen_overlay, _run
)

# 1. content_plan.json を読み込み
plan_path = ROOT_DIR / "sns_automation" / "content_plan.json"
with open(plan_path, "r", encoding="utf-8") as f:
    plan = json.load(f)

if not plan.get("plans"):
    print("⚠️ content_plan.jsonが空です。デフォルトトピックを使用します。")
    plan = {"plans": [{
        "topic": "LangChain",
        "repo_name": "langchain-ai/langchain",
        "hook": "え、マジ？LangChainでAI開発がここまで変わるなんて",
        "hashtags": ["#AI", "#LangChain", "#自動化", "#エンジニア", "#Shorts"]
    }]}

if not plan.get("plans"):
    plan = {"plans": [{
        "topic": "LangChain",
        "repo_name": "langchain-ai/langchain",
        "hook": "え、マジ？LangChainでAI開発がここまで変わるなんて",
        "hashtags": ["#AI", "#LangChain", "#自動化", "#エンジニア", "#Shorts"]
    }]}
    print("⚠️ content_plan.jsonが空 → デフォルトトピック使用")

first = plan["plans"][0]
topic = first["topic"]
hashtags = first["hashtags"]

# ランダムテーマ選択（就活テーマは完全排除）
THEMES = [
    "AI開発", "副業", "自動化", "生産性", "投資", "フリーランス", "節約"
]
theme = random.choice(THEMES)

# 強フック生成
HOOKS = [
    f"{topic}を知らないエンジニアは損してる",
    f"え、{topic}が無料？信じられない",
    f"97%の開発者が知らない{topic}の真実",
    f"深夜2時に発見した{topic}がヤバすぎる",
    f"これを見た後、{topic}を使わない理由がなくなる",
    f"{topic}を使ったら残業がゼロになった話",
    f"97%の開発者が知らない{topic}の真実",
]
hook_text = random.choice(HOOKS)

# ダミースクリプト生成（generate_script_deepseekを使わずローカル生成）
script_lines = [
    f"{hook_text}。",
    f"今日は{topic}を使って{theme}を効率化する方法を解説する。",
    f"普通の人なら知らないかもしれないけど、この{topic}を使えば{theme}の生産性が3倍になる。",
    f"例えば、週に10時間かかっていた作業が一瞬で終わる。",
    f"しかも、インストールはたったの1コマンド。",
    f"実際に使ってみると、驚くほどシンプルで直感的だ。",
    f"これは2025年現在、最も注目すべき{theme}ツールの一つと言える。",
    "コメント欄にAIconduitと書くと、1分以内に無料プレゼントの受け取り方法をお届けします！",
]

# ナレーションを15文字以内に分割（句読点+15文字ルール）
def split_narration_short(text, max_chars=15):
    segments = []
    for part in re.split(r'[。！？\n]+', text):
        part = part.strip()
        if not part:
            continue
        while len(part) > max_chars:
            # 句読点で切れる位置を探す
            cut = -1
            for sep in ['、', '，', ' ', '　']:
                pos = part.find(sep, max_chars // 2)
                if 0 < pos <= max_chars:
                    cut = pos
                    break
            if cut < 0:
                cut = max_chars
            segments.append(part[:cut])
            part = part[cut:].lstrip('、， ')
        if part:
            segments.append(part)
    return segments

shortened_lines = []
for line in script_lines:
    shortened_lines.extend(split_narration_short(line))
script_lines = shortened_lines
script_60s = "".join(script_lines)

print(f"\n🚀 テーマ: {theme}")
print(f"   トピック: {topic}")
print(f"   フック: {hook_text}")

# 2. スクリプトを scene に分割（句読点/改行ベース）
sentences = re.split(r'[。！？\n]+', script_60s)
sentences = [s.strip() for s in sentences if len(s.strip()) > 5]

# 3. scene 構造を構築
scenes = []
moods = ["hook", "interrupt", "value", "secondary_hook", "value", "value", "interrupt", "cta"]
interrupts = ["zoom_punch", "color_flash", "text_pop", "speed_ramp", "cut_zoom", "none"]
visual_queries = [
    f"{topic} futuristic {theme} concept",
    f"{topic} open source dashboard {theme}",
    "AI automation workflow interface dark mode",
    "programming developer coding setup desk",
    f"freelance {theme} laptop workspace",
    "tech startup innovation concept art",
    f"investment crypto {theme} dashboard",
    "productivity app minimalist workspace",
]

for i, sent in enumerate(sentences[:8]):
    mood = moods[i] if i < len(moods) else "value"
    scenes.append({
        "id": i + 1,
        "narration": sent,
        "caption": re.sub(r"[^\w\s]", "", sent)[:8],
        "visual_prompt": visual_queries[i] if i < len(visual_queries) else visual_queries[-1],
        "interrupt": random.choice(interrupts) if mood == "interrupt" else "none",
        "mood": mood,
    })

# hook は最初のシーンの caption に使う
if scenes:
    scenes[0]["caption"] = hook_text[:30]

print(f"   {len(scenes)} シーン生成済み")

# 4. TTS 生成
print("\n[1/4] 🎙️ TTS 生成中...")
for s in scenes:
    p = str(WORK_DIR / f"narr_{s['id']:02d}.mp3")
    tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]", "", s.get("narration", "")), p, speed=1.08)
    dur = probe_dur(p)
    s["audio_path"] = p
    s["duration"] = dur
    print(f"   Scene {s['id']}: {dur:.1f}s")

# 5. BGM ダウンロード
print("\n[2/4] 🎵 BGM ダウンロード中...")
bgm_path = download_bgm(str(WORK_DIR))
print(f"   BGM: {'✅' if bgm_path else '❌ スキップ'}")

# 6. シーン合成
print("\n[3/4] 🎬 シーン合成中...")
files = []
for i, s in enumerate(scenes):
    f = _original_compose_scene(s, i)
    files.append(f)
    print(f"   Scene {s['id']} [{s['mood']}]: done")

# 7. ループエンディング
print("   ループエンディング追加...")
loop_clip = str(WORK_DIR / "loop_end.mp4")
_run(["ffmpeg", "-y", "-i", files[0], "-t", "0.8",
      "-vf", "fade=t=out:st=0.5:d=0.3",
      "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p", loop_clip])
files.append(loop_clip)

# 8. 連結
print("\n[4/4] 🔗 連結 + BGM ミックス中...")
concat = str(WORK_DIR / "concat.txt")
with open(concat, "w") as f:
    for sf in files:
        f.write(f"file '{sf}'\n")
raw_output = str(WORK_DIR / "raw_output.mp4")
# 全入力を libx264 yuv420p に統一してから concat
norm_dir = WORK_DIR / "norm"
norm_dir.mkdir(exist_ok=True)
norm_list = []
for i, sf in enumerate(files):
    norm_path = str(norm_dir / f"norm_{i:02d}.mp4")
    _run(["ffmpeg", "-y", "-i", sf,
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
          "-pix_fmt", "yuv420p", "-c:a", "aac", norm_path])
    norm_list.append(norm_path)
with open(concat, "w") as f:
    for p in norm_list:
        f.write(f"file '{p}'\n")
_run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
      "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac",
      "-pix_fmt", "yuv420p", raw_output])

# 9. BGM ミックス
final_filename = f"v1imp_{topic.replace('/', '_').replace(' ', '_')}.mp4"
final_output = str(OUTPUT_DIR / final_filename)
if bgm_path and os.path.exists(bgm_path):
    mix_bgm(raw_output, bgm_path, final_output, voice_vol=0.85, music_vol=0.08)
else:
    import shutil
    shutil.copy(raw_output, final_output)

total = probe_dur(final_output)
print(f"\n✅ 完成: {final_output} ({total:.1f}s)")
print(f"   特徴: content_plan トピック / BGM ミックス / パターンインタラプト / ループ構造")

# 11. pycaps ワードバイワード字幕焼き込み
print("\n[5/4] 📝 字幕焼き込み中...")
subtitled_output = str(OUTPUT_DIR / f"sub_{final_filename}")
try:
    sys.path.insert(0, str(ROOT_DIR / "sns_automation" / "scripts"))
    from add_subtitles import add_word_focus_subtitles
    add_word_focus_subtitles(final_output, subtitled_output)
    final_output = subtitled_output
    print(f"   字幕追加完了: {final_output}")
except Exception as e:
    print(f"   ⚠️ 字幕焼き込み失敗（元の動画を維持）: {e}")

# 10. output/auto_log.json に記録
log_path = ROOT_DIR / "output" / "auto_log.json"
log_entry = {
    "generated_at": plan["generated_at"],
    "timestamp": plan["generated_at"],
    "source": plan["source"],
    "topic": topic,
    "theme": theme,
    "hook": hook_text,
    "script": script_60s,
    "hashtags": hashtags,
    "output_file": final_filename,
    "output_path": final_output,
    "duration_seconds": round(total, 1),
    "pipeline": "ffmpeg_pipeline_v1_improved",
    "scenes_count": len(scenes),
}
with open(log_path, "w", encoding="utf-8") as f:
    json.dump(log_entry, f, ensure_ascii=False, indent=2)
print(f"\n📝 ログ: {log_path}")
