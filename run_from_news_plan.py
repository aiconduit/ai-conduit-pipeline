#!/usr/bin/env python3
"""
news_content_plan.json を読み、ffmpeg_pipeline_v1_improved.py の
合成ロジックを流用して動画を生成し、output/auto_log.json に記録する。

run_from_content_plan.py と同じ動画生成フローを使用するが、
入力ソースが news_content_plan.json になり、固定の5シーン構成を持つ。
"""
import sys, json, os, re, random
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))
from conduit_core import (
    tts_japanese, fetch_broll_cinematic, fetch_broll_from_topic,
    download_bgm, probe_dur, mix_bgm, generate_word_subtitle_audio, beat_sync_bgm,
)
import ffmpeg_pipeline_v1_improved as _pipeline_mod
from ffmpeg_pipeline_v1_improved import (
    WORK_DIR, OUTPUT_DIR, PEXELS_CACHE, CHAR_PATH, FONT_PATHS,
    MOOD_COLORS, compose_scene as _original_compose_scene,
    gen_overlay, _run
)

# 1. news_content_plan.json を読み込み
plan_path = ROOT_DIR / "sns_automation" / "news_content_plan.json"
with open(plan_path, "r", encoding="utf-8") as f:
    plan = json.load(f)

news_item = plan.get("news_item", {})
content = plan.get("plan", {})

# topic = YouTubeタイトル（selected_title → news_item.title の順でフォールバック）
plan_data = content.get("plan", content)
topic = plan_data.get("selected_title") or news_item.get("title", "")
if not topic:
    print("⚠️ news_content_plan.jsonからタイトルが取得できません。デフォルトを使用します。")
    topic = "AI News"
    news_item = {"title": topic, "url": "", "source": "unknown", "score": 0}
    content = {"selected_title": topic, "hashtags": ["#AI"], "script": {"scenes": []}}

hashtags = content.get("hashtags", [])
repo_name = content.get("repo_name", "") or ""
source = content.get("source") or news_item.get("source", "news")
generated_at = plan.get("generated_at", "")

# CTAナレーション（固定）
CTA_TEXT = f"詳細は概要欄をチェック！コメントにAIconduitと書いてプレゼントをゲット！"

# 2. script_60s を構築（plan.script.scenes[].narration を連結）
plan = content.get("plan", content)
scene_narrations = [s.get("narration", "") for s in plan.get("script", {}).get("scenes", [])]
script_60s = "".join(scene_narrations).strip()
if not script_60s:
    print("⚠️ scriptが空です。デフォルトナレーションを使用します。")
    script_60s = f"{topic}が発表された。これは凄い。詳細はぜひチェックを。"

# 絵文字除去
script_60s = re.sub(r"[\U0001F000-\U0001FAFF]", "", script_60s)

print(f"\n🚀 ニューストピック: {topic}")
print(f"   ソース: {source}")
print(f"   スクリプト: {script_60s}")

# 3. 固定5シーン構成
#    Scene 1 (hook)      : script_60s の最初の30文字
#    Scene 2 (interrupt) : 次の30文字
#    Scene 3 (value)     : 次の40文字
#    Scene 4 (value)     : 残り（最大40文字）
#    Scene 5 (cta)       : 固定CTA
# scenesのnarrationを直接使用
CTA_TEXT = f"詳細は概要欄をチェック！コメントにAIconduitと書いてプレゼントをゲット！"
raw_scenes = plan.get("script", {}).get("scenes", [])
mood_map = {"Hook": "hook", "Fact_1": "interrupt", "Fact_2": "value", "Twist": "value", "CTA": "cta"}
scene_specs = []
for s in raw_scenes:
    title = s.get("scene_title", "value")
    narration = s.get("narration", "").strip()
    if not narration or len(narration) < 3:
        continue
    mood = mood_map.get(title, "value")
    if title == "CTA":
        narration = CTA_TEXT
    scene_specs.append({"shot": title.lower(), "mood": mood, "narration": narration})
if not scene_specs:
    scene_specs = [{"shot": "hook", "mood": "hook", "narration": script_60s[:50] or "AIニュース速報"}]

MOOD_VISUAL_QUERIES = {
    "hook": f"{topic} breaking news alert futuristic",
    "value": f"{topic} technology innovation concept",
    "interrupt": f"{topic} AI speed performance result",
    "cta": "AI automation futuristic digital abstract",
}


# B-roll B: 内容に関係なくtech系映像に固定（コード画面・PC操作・AI技術）
import random as _rand_broll
TECH_BROLL_QUERIES = [
    "person typing laptop coding",
    "computer screen code programming",
    "software developer working keyboard",
    "AI technology data visualization",
    "typing fast computer screen dark",
]
MOOD_VISUAL_QUERIES_2 = {
    "hook": _rand_broll.choice(TECH_BROLL_QUERIES),
    "value": _rand_broll.choice(TECH_BROLL_QUERIES),
    "interrupt": _rand_broll.choice(TECH_BROLL_QUERIES),
    "cta": _rand_broll.choice(TECH_BROLL_QUERIES),
}
def mood_visual_query(topic, mood):
    """topicとmoodに応じてvisual_queryを生成する"""
    return MOOD_VISUAL_QUERIES.get(mood, MOOD_VISUAL_QUERIES["value"])


interrupts = ["zoom_punch", "color_flash", "text_pop", "speed_ramp", "cut_zoom", "none"]

scenes = []
for i, spec in enumerate(scene_specs):
    sent = spec["narration"]
    mood = spec["mood"]
    visual_query = mood_visual_query(topic, mood)
    # シーンごとにスクロール位置とKen Burnsスタイルを変える
    scroll_patterns = [0, 200, 500, 900, 1400]
    kb_styles = ["left_right", "right_left", "up_down", "down_up", "diagonal"]
    scene = {
        "id": i + 1,
        "caption": re.sub(r"[^\w\s]", "", sent)[:8],
        "visual_prompt": visual_query,
        "interrupt": random.choice(interrupts) if mood == "interrupt" else "none",
        "mood": mood,
        "visual_1": visual_query,
        "topic": topic,
        "repo_name": repo_name,
        "narration": sent,
        "news_url": news_item.get("url", ""),
        "scroll_y": scroll_patterns[i % len(scroll_patterns)],
        "ken_burns_style": kb_styles[i % len(kb_styles)],
        "visual_2": MOOD_VISUAL_QUERIES_2.get(spec["mood"], f"{topic} technology abstract"),
    }
    scenes.append(scene)

# hook は最初のシーンの caption に使う
scenes[0]["caption"] = script_60s[:30]

print(f"   {len(scenes)} シーン生成済み")

# 4. TTS 生成（各セグメントを分割後、個別のシーンとして処理）
print("\n[1/4] 🎙️ TTS 生成中...")
for s in scenes:
    p = str(WORK_DIR / f"narr_{s['id']:04d}.wav")
    narration_text = s["narration"]
    try:
        audio_path, timestamps = generate_word_subtitle_audio(narration_text, p, speed=1.08)
        dur = (timestamps[-1]["start_ms"] + timestamps[-1]["duration_ms"]) / 1000.0 if timestamps else probe_dur(audio_path)
    except Exception as e:
        print(f"   ⚠️ TTS失敗({e}), フォールバック")
        mp3_p = p.replace(".wav", ".mp3")
        tts_japanese(narration_text, mp3_p, speed=1.08)
        audio_path = mp3_p
        timestamps = []
        dur = probe_dur(audio_path)
    s["audio_path"] = audio_path
    s["duration"] = dur
    s["word_timestamps"] = timestamps
    print(f"   Scene {s['id']} [{s['mood']}]: '{narration_text}' ({dur:.1f}s, {len(timestamps)} words)")

# 5. BGM ダウンロード
print("\n[2/4] 🎵 BGM ダウンロード中...")
bgm_result = download_bgm(str(WORK_DIR))
bgm_path = bgm_result[0] if isinstance(bgm_result, tuple) else bgm_result
print(f"   BGM: {'✅' if bgm_path else '❌ スキップ'}")

# 6. 固定イントロ生成（2秒: AI Conduitロゴ）
print("\n[3/4] 🎬 シーン合成中...")
from PIL import Image, ImageDraw, ImageFont as _PILFont

def _load_font(size):
    for p in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
               "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
               "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(p):
            try: return _PILFont.truetype(p, size)
            except: pass
    return _PILFont.load_default()

intro_clip = None
try:
    intro_img = Image.new("RGB", (1080, 1920), (10, 10, 15))
    d = ImageDraw.Draw(intro_img)
    d.rectangle([0, 0, 1080, 8], fill=(255, 220, 0))
    d.rectangle([0, 1912, 1080, 1920], fill=(255, 220, 0))
    for txt, col, y, sz in [
        ("AI Conduit", (255,220,0), 800, 120),
        ("AIニュース速報", (200,200,200), 960, 56),
    ]:
        f = _load_font(sz)
        bb = d.textbbox((0,0), txt, font=f)
        d.text(((1080-(bb[2]-bb[0]))//2, y), txt, fill=col, font=f)
    intro_png = str(WORK_DIR / "intro.png")
    intro_img.save(intro_png)
    intro_clip = str(WORK_DIR / "intro.mp4")
    _run(["ffmpeg", "-y", "-loop", "1", "-i", intro_png, "-t", "2.0",
          "-vf", "fade=t=in:st=0:d=0.3,fade=t=out:st=1.5:d=0.5,scale=1080:1920",
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-pix_fmt", "yuv420p", "-an", intro_clip])
    print("   ✅ イントロ生成完了")
except Exception as _e:
    print(f"   ⚠️ イントロスキップ: {_e}")
    intro_clip = None

# シーン合成
files = []
for i, s in enumerate(scenes):
    s["visual_1"] = mood_visual_query(s["topic"], s["mood"])
    f = _original_compose_scene(s, i)
    files.append(f)
    print(f"   Scene {s['id']} [{s['mood']}]: done")

# エンディングカード生成（2秒）
outro_clip = None
try:
    outro_img = Image.new("RGB", (1080, 1920), (10, 10, 15))
    d2 = ImageDraw.Draw(outro_img)
    d2.rectangle([0, 0, 1080, 8], fill=(255, 220, 0))
    for txt, col, y, sz in [
        ("チャンネル登録", (255,220,0), 750, 80),
        ("コメント & いいね！", (255,255,255), 880, 72),
        ("概要欄もチェック", (200,200,200), 1010, 60),
        ("AI Conduit", (150,150,150), 1180, 50),
    ]:
        f2 = _load_font(sz)
        bb2 = d2.textbbox((0,0), txt, font=f2)
        d2.text(((1080-(bb2[2]-bb2[0]))//2, y), txt, fill=col, font=f2)
    outro_png = str(WORK_DIR / "outro.png")
    outro_img.save(outro_png)
    outro_clip = str(WORK_DIR / "outro.mp4")
    _run(["ffmpeg", "-y", "-loop", "1", "-i", outro_png, "-t", "2.0",
          "-vf", "fade=t=in:st=0:d=0.3,scale=1080:1920",
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-pix_fmt", "yuv420p", "-an", outro_clip])
    print("   ✅ エンディングカード生成完了")
except Exception as _e:
    print(f"   ⚠️ エンディングスキップ: {_e}")
    outro_clip = None

# ループエンディング
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
# イントロ・アウトロをfilesに追加
all_clips = []
if intro_clip and os.path.exists(intro_clip):
    all_clips.append(intro_clip)
all_clips.extend(files)
if outro_clip and os.path.exists(outro_clip):
    all_clips.append(outro_clip)
files = all_clips

norm_list = []
for i, sf in enumerate(files):
    norm_path = str(norm_dir / f"norm_{i:02d}.mp4")
    _run(["ffmpeg", "-y", "-i", sf,
          "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-pix_fmt", "yuv420p", "-c:a", "aac", norm_path])
    norm_list.append(norm_path)
with open(concat, "w") as f:
    for p in norm_list:
        f.write(f"file '{p}'\n")
# 連結（シンプルfade in/out + concat）
if len(norm_list) >= 2:
    try:
        n = len(norm_list)
        input_args = []
        for np_ in norm_list:
            input_args += ["-i", np_]
        filter_v = ""
        filter_a = ""
        for j in range(n):
            filter_v += f"[{j}:v]fade=t=in:st=0:d=0.15,fade=t=out:st=0.7:d=0.15[v{j}];"
            filter_a += f"[{j}:a]" if f"[{j}:a]" else ""
        filter_v += "".join(f"[v{j}]" for j in range(n))
        filter_v += f"concat=n={n}:v=1:a=0[vout]"
        # 音声は別でconcat
        filter_a = "".join(f"[{j}:a]" for j in range(n))
        filter_a += f"concat=n={n}:v=0:a=1[aout]"
        _run(["ffmpeg", "-y"] + input_args + [
            "-filter_complex", filter_v + ";" + filter_a,
            "-map", "[vout]", "-map", "[aout]",
            "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-pix_fmt", "yuv420p", raw_output])
        print("   ✅ fade付き連結完了")
    except Exception as _xe:
        print(f"   ⚠️ fadeスキップ ({_xe}) → 通常concat")
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac",
              "-pix_fmt", "yuv420p", raw_output])
else:
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac",
          "-pix_fmt", "yuv420p", raw_output])

# 9. BGM ミックス
final_filename = f"v2news_{topic[:20]}.mp4"
final_output = str(OUTPUT_DIR / final_filename)
if bgm_path and os.path.exists(bgm_path):
    try:
        beat_sync_bgm(raw_output, bgm_path, final_output, voice_vol=0.85, music_vol=0.08)
        print("   ✅ ビートシンクBGMミックス完了")
    except Exception as _be:
        print(f"   ⚠️ ビートシンクスキップ ({_be}) → 通常ミックス")
        mix_bgm(raw_output, bgm_path, final_output, voice_vol=0.85, music_vol=0.08)
else:
    import shutil
    shutil.copy(raw_output, final_output)

total = probe_dur(final_output)
print(f"\n✅ 完成: {final_output} ({total:.1f}s)")
print(f"   特徴: news_content_plan / BGM ミックス / 固定5シーン / ループ構造")

# 字幕はffmpeg_pipeline内でASS形式で焼き込み済み

# 10. output/auto_log.json に記録
log_path = ROOT_DIR / "output" / "auto_log.json"
log_entry = {
    "generated_at": generated_at,
    "timestamp": generated_at,
    "source": source,
    "topic": topic,
    "news_item": news_item,
    "output_file": final_filename,
    "output_path": final_output,
    "duration_seconds": round(total, 1),
    "pipeline": "ffmpeg_pipeline_v1_improved",
    "mode": "news_content_plan",
    "scenes_count": len(scenes),
    "script_60s": script_60s,
}
with open(log_path, "w", encoding="utf-8") as f:
    json.dump(log_entry, f, ensure_ascii=False, indent=2)
print(f"\n📝 ログ: {log_path}")
