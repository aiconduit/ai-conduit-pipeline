import re
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

# パイプライン選択（カテゴリ・ランダムで最適なスタイルを選択）
import subprocess as _sp
def _run_pipeline(pipeline_script, plan_json_path, topic, source_repo=""):
    """指定パイプラインを実行して動画を生成"""
    env = os.environ.copy()
    env["PIPELINE_TOPIC"] = topic
    env["PIPELINE_REPO"] = source_repo
    env["PIPELINE_PLAN"] = str(plan_json_path)
    result = _sp.run(
        ["python3", str(ROOT_DIR / pipeline_script), str(plan_json_path)],
        capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        print(f"⚠️ {pipeline_script} 失敗: {result.stderr[-300:]}")
        return False
    return True

PIPELINE_BY_CATEGORY = {
    "claude_code": ["ffmpeg_pipeline_v30_screenrec.py", "ffmpeg_pipeline_v33_hormozi.py"],
    "codex": ["ffmpeg_pipeline_v30_screenrec.py", "ffmpeg_pipeline_v34_mrbeast.py"],
    "gemini": ["ffmpeg_pipeline_v30_screenrec.py", "ffmpeg_pipeline_v33_hormozi.py"],
    "ai_tools": ["ffmpeg_pipeline_v33_hormozi.py", "ffmpeg_pipeline_v34_mrbeast.py"],
    "default": ["ffmpeg_pipeline_v1_improved.py"],
}

# 1. news_content_plan.json を読み込み
plan_path = ROOT_DIR / "sns_automation" / "news_content_plan.json"
with open(plan_path, "r", encoding="utf-8") as f:
    plan = json.load(f)

news_item = plan.get("news_item", {})
content = plan if plan.get("selected_title") else plan.get("plan", plan)

# topic = YouTubeタイトル（selected_title → news_item.title の順でフォールバック）
plan_data = content.get("plan", content)
topic = plan.get("selected_title") or plan_data.get("selected_title") or news_item.get("title", "")
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
CTA_TEXT = f"概要欄のリンクから無料で受け取れます。コメントにAIと書いてください。"

# 2. script_60s を構築（plan.script.scenes[].narration を連結）
plan = content  # ai_tool_content_plannerはトップレベルにscriptを保存
# 新旧両フォーマット対応（script.scenes または scenes）
_scenes_data = plan.get("script", {}).get("scenes", []) or plan.get("scenes", [])
scene_narrations = [s.get("narration", "") for s in _scenes_data]
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
CTA_TEXT = f"概要欄のリンクから無料で受け取れます。コメントにAIと書いてください。"
raw_scenes = plan.get("script", {}).get("scenes", []) or plan.get("scenes", [])
mood_map = {
    # 旧5シーン型
    "Hook": "hook", "Fact_1": "interrupt", "Fact_2": "value", "Twist": "value", "CTA": "cta",
    # 新7シーン型
    "Problem": "hook", "Solution": "value", "Step1": "value", "Step2": "value", "Result": "value",
    # その他
    "How": "value", "Bonus": "value", "Tip": "value", "Demo": "value",
}
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
    "hook": "frustrated developer typing computer problem",
    "value": "developer coding terminal dark screen solution",
    "interrupt": f"{topic} AI speed performance result",
    "cta": "gift download reward success developer",
}


# B-roll B: 内容に関係なくtech系映像に固定（コード画面・PC操作・AI技術）
import random as _rand_broll

# シーンタイトル別の固有B-rollクエリ
SCENE_BROLL_QUERIES = {
    "Hook":     ["developer frustrated slow computer", "programmer stuck problem", "person annoyed laptop"],
    "Why":      ["developer stressed deadline", "computer error screen", "person worried work"],
    "Solution": ["developer excited discovery", "programmer breakthrough", "coding solution found"],
    "Step1":    ["hands typing terminal command", "close up keyboard typing", "terminal dark screen"],
    "Step2":    ["code editor screen close", "programming configuration", "developer focused screen"],
    "Result":   ["developer celebrating success", "programmer happy work", "person satisfied laptop"],
    "CTA":      ["phone notification", "mobile app download", "person sharing phone"],
    "hook":     ["developer frustrated problem", "programmer stuck error", "coding issue dark"],
    "value":    ["developer coding terminal", "programming dark screen", "software development"],
    "interrupt":["fast typing keyboard", "code running terminal", "developer quick action"],
    "cta":      ["gift box open", "download success", "developer sharing"],
}

def get_broll_query(shot_title: str) -> str:
    queries = SCENE_BROLL_QUERIES.get(shot_title, ["developer coding dark terminal"])
    return _rand_broll.choice(queries)

TECH_BROLL_QUERIES = ["developer coding terminal dark", "programming screen", "software development"]
MOOD_VISUAL_QUERIES_2 = {
    "hook": get_broll_query("hook"),
    "value": get_broll_query("value"),
    "interrupt": get_broll_query("interrupt"),
    "cta": get_broll_query("cta"),
}


# シーン別動画素材ライブラリ読み込み
import random as _rand_lib
VIDEO_LIBRARY = {}
try:
    _lib_path = "assets/video_library.json"
    if os.path.exists(_lib_path):
        with open(_lib_path, encoding="utf-8") as _lf:
            VIDEO_LIBRARY = json.load(_lf)
        print(f"✅ 動画ライブラリ: {sum(len(v) for v in VIDEO_LIBRARY.values())}本")
except Exception as _le:
    print(f"⚠️ 動画ライブラリ読み込み失敗: {_le}")

def get_scene_video_url(shot_title: str) -> str:
    """シーンタイトルに対応する動画URLをライブラリから取得"""
    key = shot_title.lower()
    videos = VIDEO_LIBRARY.get(key, VIDEO_LIBRARY.get("solution", []))
    if videos:
        return _rand_lib.choice(videos)["url"]
    return None

# ターミナルアニメーター読み込み
try:
    sys.path.insert(0, "sns_automation/scripts")
    from terminal_animator import generate_typing_animation, extract_commands_from_narration
    TERMINAL_ANIMATOR_AVAILABLE = True
    print("✅ ターミナルアニメーター読み込み完了")
except Exception as _te:
    TERMINAL_ANIMATOR_AVAILABLE = False
    print(f"⚠️ ターミナルアニメーター失敗: {_te}")

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

# シーン別モーション設定（forループ前に定義）
SCENE_MOTION = {
    "Hook":     {"zoom": "snap_zoom_in",  "kb": "diagonal",   "vf_extra": ""},
    "Why":      {"zoom": "slow_zoom_in",  "kb": "up_down",    "vf_extra": ""},
    "Solution": {"zoom": "hard_cut",      "kb": "left_right", "vf_extra": ""},
    "Step1":    {"zoom": "punch_in",      "kb": "right_left", "vf_extra": "eq=contrast=1.1"},
    "Step2":    {"zoom": "punch_in",      "kb": "down_up",    "vf_extra": "eq=contrast=1.1"},
    "Result":   {"zoom": "snap_zoom_out", "kb": "diagonal",   "vf_extra": ""},
    "CTA":      {"zoom": "fade_out",      "kb": "left_right", "vf_extra": ""},
}

scenes = []
for i, spec in enumerate(scene_specs):
    sent = spec["narration"]
    mood = spec["mood"]
    visual_query = mood_visual_query(topic, mood)
    # シーンタイトルに基づいてSCENE_MOTIONからKen Burnsスタイルを選択
    scroll_patterns = [0, 200, 500, 900, 1400]
    kb_styles = ["left_right", "right_left", "up_down", "down_up", "diagonal"]
    # シーンタイトルを取得（Hook/Why/Solution/Step1/Step2/Result/CTA）
    _scene_title = spec.get("shot", "").replace("_", "").title() if isinstance(spec, dict) else ""
    _motion = SCENE_MOTION.get(_scene_title, SCENE_MOTION.get("Solution", {"kb": "left_right", "zoom_factor": 1.05, "vf_extra": ""}))
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
        "ken_burns_style": _motion.get("kb", kb_styles[i % len(kb_styles)]),
        "visual_2": MOOD_VISUAL_QUERIES_2.get(spec["mood"], f"{topic} technology abstract"),
    }
    scenes.append(scene)

# hook は最初のシーンの caption に使う
scenes[0]["caption"] = script_60s[:30]

print(f"   {len(scenes)} シーン生成済み")

# 4. TTS 生成（各セグメントを分割後、個別のシーンとして処理）
print("\n[1/4] 🎙️ TTS 生成中...")
# moodごとのTTS rate/pitch設定
MOOD_TTS_PARAMS = {
    # 旧型対応
    "hook":           {"rate": "+8%",  "pitch": "+3Hz"},
    "interrupt":      {"rate": "+5%",  "pitch": "+2Hz"},
    "value":          {"rate": "-5%",  "pitch": "-2Hz"},
    "secondary_hook": {"rate": "+5%",  "pitch": "+2Hz"},
    "cta":            {"rate": "+3%",  "pitch": "+5Hz"},
    "default":        {"rate": "-5%",  "pitch": "-3Hz"},
    # 新7シーン型
    "Why":            {"rate": "-3%",  "pitch": "-2Hz"},  # 落ち着いた説明
    "Solution":       {"rate": "+5%",  "pitch": "+2Hz"},  # 明快・前向き
    "Step1":          {"rate": "-5%",  "pitch": "-3Hz"},  # ゆっくり・明確
    "Step2":          {"rate": "-5%",  "pitch": "-3Hz"},  # ゆっくり・明確
    "Result":         {"rate": "+8%",  "pitch": "+4Hz"},  # 達成感
}

for s in scenes:
    p = str(WORK_DIR / f"narr_{s['id']:04d}.wav")
    narration_text = s["narration"]
    tts_params = MOOD_TTS_PARAMS.get(s.get("mood", "default"), MOOD_TTS_PARAMS["default"])
    try:
        audio_path, timestamps = generate_word_subtitle_audio(
            narration_text, p, speed=1.05,
            rate=tts_params["rate"], pitch=tts_params["pitch"])
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

intro_clip = None  # サムネはthumbnail_main.jpgを使用
intro_clip = None  # サムネはthumbnail_main.jpgを使用
# シーン合成
files = []
# サムネイル画像を冒頭に表示（タイトル音声付き）
_thumb_path = ROOT_DIR / "assets" / "thumbnail_main.jpg"
_thumb_clip = str(WORK_DIR / "thumbnail_intro.mp4")
_thumb_audio = str(WORK_DIR / "thumbnail_audio.mp3")
if _thumb_path.exists():
    # タイトルをTTSで読み上げ
    _thumb_title = plan.get("selected_title") or plan.get("script", {}).get("title") or "Claude CodeがMCPで神になった"
    try:
        tts_japanese(_thumb_title, _thumb_audio, speed=1.0)
        _thumb_dur = max(probe_dur(_thumb_audio) + 0.3, 2.0)
    except Exception as _te:
        print(f"⚠️ サムネTTSスキップ: {_te}")
        _thumb_audio = None
        _thumb_dur = 2.5
    # 映像生成
    _thumb_video = str(WORK_DIR / "thumbnail_video.mp4")
    _run(["ffmpeg", "-y", "-loop", "1", "-i", str(_thumb_path),
          "-t", str(_thumb_dur), "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-an", "-pix_fmt", "yuv420p", _thumb_video])
    # 音声と映像を合成
    if _thumb_audio and os.path.exists(_thumb_audio):
        _run(["ffmpeg", "-y", "-i", _thumb_video, "-i", _thumb_audio,
              "-c:v", "copy", "-c:a", "aac", "-shortest", _thumb_clip])
    else:
        import shutil; shutil.copy(_thumb_video, _thumb_clip)
    files.insert(0, _thumb_clip)
    print(f"✅ サムネイントロ追加 ({_thumb_dur:.1f}秒・音声付き)")
else:
    print("⚠️ thumbnail_main.jpg が見つかりません")
    print("⚠️ thumbnail_main.jpg が見つかりません")
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
# 連結（映像はfade、音声は別途concat）
import subprocess as _sp

def _has_audio(path):
    r = _sp.run(["ffprobe", "-v", "error", "-select_streams", "a",
                 "-show_entries", "stream=index", "-of", "csv=p=0", path],
                capture_output=True, text=True)
    return bool(r.stdout.strip())

# 63パターン10グループからランダム選択してxfadeトランジション適用
import random as _rand_mot
_MOTION_GROUPS = {
    # カット系・スピード感
    "A": {"hook": "zoomin",      "interrupt": "slideleft",  "value": "fade",        "secondary_hook": "diagtl",    "cta": "fadeblack"},
    "B": {"hook": "fade",        "interrupt": "dissolve",   "value": "zoomin",      "secondary_hook": "wipetl",    "cta": "fadewhite"},
    "C": {"hook": "slideleft",   "interrupt": "zoomin",     "value": "slideright",  "secondary_hook": "dissolve",  "cta": "fadeblack"},
    "D": {"hook": "diagtl",      "interrupt": "fadeblack",  "value": "circleopen",  "secondary_hook": "radial",    "cta": "fade"},
    "E": {"hook": "slideup",     "interrupt": "slidedown",  "value": "wipeleft",    "secondary_hook": "fade",      "cta": "fadewhite"},
    "F": {"hook": "dissolve",    "interrupt": "slideleft",  "value": "diagtr",      "secondary_hook": "slideup",   "cta": "fadeblack"},
    "G": {"hook": "circleopen",  "interrupt": "fade",       "value": "zoomin",      "secondary_hook": "wiperight", "cta": "fadewhite"},
    "H": {"hook": "wipetl",      "interrupt": "diagbl",     "value": "radial",      "secondary_hook": "slidedown", "cta": "fade"},
    "I": {"hook": "fadeblack",   "interrupt": "zoomin",     "value": "slideup",     "secondary_hook": "circleopen","cta": "wipeleft"},
    "J": {"hook": "radial",      "interrupt": "wiperight",  "value": "fadewhite",   "secondary_hook": "dissolve",  "cta": "dissolve"},
    # シネマティック系
    "K": {"hook": "dissolve",    "interrupt": "fade",       "value": "circleopen",  "secondary_hook": "fadewhite", "cta": "fadeblack"},
    "L": {"hook": "wiperight",   "interrupt": "wipetl",     "value": "slideleft",   "secondary_hook": "diagtr",    "cta": "dissolve"},
    "M": {"hook": "diagbl",      "interrupt": "circleopen", "value": "fadeblack",   "secondary_hook": "zoomin",    "cta": "fadewhite"},
    "N": {"hook": "slidedown",   "interrupt": "radial",     "value": "diagtl",      "secondary_hook": "dissolve",  "cta": "fade"},
    "O": {"hook": "fadewhite",   "interrupt": "slideup",    "value": "wiperight",   "secondary_hook": "wipetl",    "cta": "zoomin"},
    # エネルギー系
    "P": {"hook": "zoomin",      "interrupt": "diagbl",     "value": "slideleft",   "secondary_hook": "fadeblack", "cta": "circleopen"},
    "Q": {"hook": "slideleft",   "interrupt": "dissolve",   "value": "diagtl",      "secondary_hook": "wipeleft",  "cta": "dissolve"},
    "R": {"hook": "circleopen",  "interrupt": "slidedown",  "value": "fade",        "secondary_hook": "diagbl",    "cta": "fade"},
    "S": {"hook": "diagtr",      "interrupt": "wipeleft",   "value": "slideup",     "secondary_hook": "radial",    "cta": "fadeblack"},
    "T": {"hook": "wipeleft",    "interrupt": "circleopen", "value": "dissolve",    "secondary_hook": "slidedown", "cta": "zoomin"},
}
_gkey = _rand_mot.choice(list(_MOTION_GROUPS.keys()))
_mxfade = _MOTION_GROUPS[_gkey]
print(f"[Motion] グループ{_gkey}を選択: {_mxfade}", flush=True)

video_only = str(WORK_DIR / "video_only.mp4")
_xfade_dur = 0.2
if len(norm_list) >= 2:
    import subprocess as _xsp
    def _probe_dur(p):
        res = _xsp.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",p],
                       capture_output=True, text=True)
        try: return float(res.stdout.strip())
        except: return 3.0
    _durations = [_probe_dur(p) for p in norm_list]
    _inputs = []
    for p in norm_list: _inputs.extend(["-i", p])
    _fparts = []
    _running = _durations[0] - _xfade_dur
    _moods = [s.get("mood","value") for s in scene_specs] if "scene_specs" in dir() else ["hook"] + ["value"]*(len(norm_list)-2) + ["cta"]
    # 最初のxfade: [0:v][1:v] -> [v0]
    _xf1 = _mxfade.get(_moods[1] if len(_moods)>1 else "value", "fade")
    _fparts.append(f"[0:v][1:v]xfade=transition={_xf1}:duration={_xfade_dur}:offset={_running:.3f}[v0]")
    for _i in range(2, len(norm_list)):
        _running += _durations[_i-1] - _xfade_dur
        _xfi = _mxfade.get(_moods[_i] if _i < len(_moods) else "value", "fade")
        # 前のタグ[v{_i-2}]と新しい入力[{_i}:v]を結合して[v{_i-1}]を出力
        _fparts.append(f"[v{_i-2}][{_i}:v]xfade=transition={_xfi}:duration={_xfade_dur}:offset={_running:.3f}[v{_i-1}]")
    # 最後のタグにformat追加（セミコロンで区切る）
    _last_idx = len(norm_list) - 2
    _fstr = ";".join(_fparts) + f";[v{_last_idx}]format=yuv420p[out]"
    _run(["ffmpeg","-y"] + _inputs + ["-filter_complex",_fstr,"-map","[out]",
          "-r","30","-c:v","libx264","-preset","fast","-crf","20","-pix_fmt","yuv420p","-an",video_only])
else:
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
          "-pix_fmt", "yuv420p", "-an", video_only])
print("   ✅ 映像連結完了（グループ{_gkey}）".format(_gkey=_gkey), flush=True)

# 音声ありのクリップだけでconcat
# サムネクリップ(norm_00)を音声から除外してシーン音声のみ使用
_thumb_norm = str(WORK_DIR / "norm" / "norm_00.mp4")
audio_clips = [f for f in norm_list if _has_audio(f) and f != _thumb_norm]
if audio_clips:
    audio_concat = str(WORK_DIR / "audio_concat.txt")
    with open(audio_concat, "w") as _af:
        for ac in audio_clips:
            _af.write(f"file '{ac}'\n")
    audio_only_raw = str(WORK_DIR / "audio_only_raw.aac")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", audio_concat,
          "-vn", "-c:a", "aac", audio_only_raw])

    # イントロ・アウトロの長さ分の無音を追加してタイミングを合わせる
    # サムネクリップの長さを使ってタイミングを合わせる
    _thumb_clip_path = str(WORK_DIR / "thumbnail_intro.mp4")
    intro_dur = probe_dur(_thumb_clip_path) if os.path.exists(_thumb_clip_path) else (probe_dur(intro_clip) if intro_clip and os.path.exists(str(intro_clip or "")) else 0.0)
    outro_dur = probe_dur(outro_clip) if outro_clip and os.path.exists(str(outro_clip or "")) else 0.0
    audio_only = str(WORK_DIR / "audio_only.aac")
    if intro_dur > 0 or outro_dur > 0:
        silence_intro = str(WORK_DIR / "silence_intro.aac")
        silence_outro = str(WORK_DIR / "silence_outro.aac")
        parts = []
        if intro_dur > 0:
            _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                  "-t", str(intro_dur), "-c:a", "aac", silence_intro])
            parts.append(silence_intro)
        parts.append(audio_only_raw)
        if outro_dur > 0:
            _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                  "-t", str(outro_dur), "-c:a", "aac", silence_outro])
            parts.append(silence_outro)
        # 無音+音声+無音を連結
        sil_concat = str(WORK_DIR / "sil_concat.txt")
        with open(sil_concat, "w") as _sf:
            for p in parts:
                _sf.write(f"file '{p}'\n")
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", sil_concat,
              "-c:a", "aac", audio_only])
        print(f"   ✅ 無音追加（イントロ{intro_dur:.1f}s + 音声 + アウトロ{outro_dur:.1f}s）")
    else:
        import shutil; shutil.copy(audio_only_raw, audio_only)

    # 映像+音声を合成
    _run(["ffmpeg", "-y", "-i", video_only, "-i", audio_only,
          "-c:v", "copy", "-c:a", "aac", "-shortest", raw_output])
    print("   ✅ 映像+音声合成完了")
else:
    print("   ⚠️ 音声クリップなし → 映像のみ")
    import shutil; shutil.copy(video_only, raw_output)


# 9. BGM ミックス
safe_topic = re.sub(r"[:/\\*?<>|]", "", topic[:20])
final_filename = f"v2news_{safe_topic}.mp4"
final_filename = f"v2news_{safe_topic}.mp4"
final_output = str(OUTPUT_DIR / final_filename)
if bgm_path and os.path.exists(bgm_path):
    try:
        beat_sync_bgm(raw_output, bgm_path, final_output, voice_vol=0.85, music_vol=0.08)
        print("   ✅ ビートシンクBGMミックス完了")
    except Exception as _be:
        print(f"   ⚠️ ビートシンクスキップ ({_be}) → 通常ミックス")
        mix_bgm(raw_output, bgm_path, final_output, voice_vol=0.85, music_vol=0.08)

# 音声品質向上: モノラル→ステレオ・ビットレート128kbps・映像4Mbps
if os.path.exists(final_output):
    hq_output = final_output.replace(".mp4", "_hq.mp4")
    _run(["ffmpeg", "-y", "-i", final_output,
          "-c:v", "libx264", "-preset", "fast", "-b:v", "4000k", "-maxrate", "4000k",
          "-c:a", "aac", "-b:a", "128k", "-ac", "2", "-ar", "44100",
          "-pix_fmt", "yuv420p", hq_output])
    if os.path.exists(hq_output) and os.path.getsize(hq_output) > 100000:
        import shutil; shutil.move(hq_output, final_output)
        print("   ✅ 高品質エンコード完了（ステレオ・4Mbps）")
else:
    import shutil
    shutil.copy(raw_output, final_output)

total = probe_dur(final_output)
# Jenny Hoyos法則: 最後0.5秒をトリム（リテンション+5%効果）
if total > 5:
    trimmed = final_output.replace(".mp4", "_trimmed.mp4")
    _run(["ffmpeg", "-y", "-i", final_output,
          "-t", str(round(total - 0.5, 2)),
          "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", trimmed])
    if os.path.exists(trimmed) and os.path.getsize(trimmed) > 100000:
        import shutil; shutil.move(trimmed, final_output)
        total = probe_dur(final_output)
        print(f"   ✂️ 最後0.5秒トリム完了（Jenny Hoyos法則）")
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
