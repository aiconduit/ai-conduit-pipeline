#!/usr/bin/env python3
"""
パイプライン3 HyperFramesビデオエンジン - プロ品質版
各シーンをGSAPアニメーション付きのプロ品質HTMLで生成
"""
import os, json, subprocess, shutil
from pathlib import Path

WORK_DIR = Path("/tmp/pipeline3_work")
W, H = 1080, 1920

def _run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)

def probe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 4.0

SCENE_STYLES = {
    "Hook": {
        "bg": "#050510",
        "accent": "#FF4500",
        "accent2": "#FF8C00",
        "text": "#FFFFFF",
        "style": "hook",
    },
    "Why": {
        "bg": "#08080F",
        "accent": "#FF2D55",
        "accent2": "#FF6B6B",
        "text": "#FFFFFF",
        "style": "why",
    },
    "Solution": {
        "bg": "#050A1A",
        "accent": "#00D4FF",
        "accent2": "#0080FF",
        "text": "#FFFFFF",
        "style": "solution",
    },
    "Step1": {
        "bg": "#080510",
        "accent": "#A855F7",
        "accent2": "#7C3AED",
        "text": "#FFFFFF",
        "style": "step",
    },
    "Step2": {
        "bg": "#050A08",
        "accent": "#00FF88",
        "accent2": "#00CC6A",
        "text": "#FFFFFF",
        "style": "step",
    },
    "Result": {
        "bg": "#050A0A",
        "accent": "#FFD700",
        "accent2": "#FFA500",
        "text": "#FFFFFF",
        "style": "result",
    },
    "CTA": {
        "bg": "#050510",
        "accent": "#FF4500",
        "accent2": "#FF8C00",
        "text": "#FFFFFF",
        "style": "cta",
    },
}

def get_style(title):
    for key in SCENE_STYLES:
        if key.lower() in title.lower():
            return SCENE_STYLES[key]
    return SCENE_STYLES["Solution"]

def generate_scene_html(scene: dict, idx: int, total: int, audio_dur: float) -> str:
    title = scene.get("title", "value")
    narration = scene.get("narration", "")
    caption = scene.get("caption", "")
    dur = max(audio_dur + 0.3, 2.5)
    s = get_style(title)

    # 共通パーティクル・グリッドライン
    particles = ""
    for i in range(12):
        x = (i * 97) % 1080
        y = (i * 137) % 1920
        size = 2 + (i % 4)
        delay = i * 0.3
        particles += f'<div class="particle" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;animation-delay:{delay}s"></div>'

    # スタイル別レイアウト
    style_type = s["style"]

    if style_type == "hook":
        content = f"""
<div class="hook-container">
  <div class="hook-label">HOOK</div>
  <div class="hook-line"></div>
  <div class="hook-text">{narration}</div>
  <div class="hook-sub">{caption}</div>
  <div class="hook-arrow">▼</div>
</div>"""
        extra_css = f"""
.hook-container {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:960px; text-align:center; }}
.hook-label {{ font-size:36px; color:{s['accent']}; letter-spacing:12px; font-weight:900; opacity:0; }}
.hook-line {{ width:0; height:4px; background:linear-gradient(90deg,{s['accent']},{s['accent2']}); margin:30px auto; border-radius:2px; }}
.hook-text {{ font-size:88px; font-weight:900; color:{s['text']}; line-height:1.2; margin:40px 0; opacity:0; text-shadow:0 0 40px {s['accent']}88; }}
.hook-sub {{ font-size:52px; color:{s['accent']}; font-weight:700; opacity:0; }}
.hook-arrow {{ font-size:60px; color:{s['accent']}; opacity:0; margin-top:60px; animation:bounce 1s ease-in-out infinite; }}
@keyframes bounce {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(20px)}} }}
"""
        anim_js = f"""
tl.to('.hook-label', {{opacity:1, letterSpacing:'8px', duration:0.6, ease:'power2.out'}}, 0.2)
  .to('.hook-line', {{width:'600px', duration:0.5, ease:'power2.inOut'}}, 0.5)
  .to('.hook-text', {{opacity:1, y:0, duration:0.7, ease:'back.out(1.5)'}}, 0.8)
  .to('.hook-sub', {{opacity:1, duration:0.5}}, 1.3)
  .to('.hook-arrow', {{opacity:1, duration:0.4}}, 1.6)
"""

    elif style_type in ["step", "solution"]:
        step_num = idx
        content = f"""
<div class="step-container">
  <div class="step-num">{step_num:02d}</div>
  <div class="step-divider"></div>
  <div class="step-title">{caption or title}</div>
  <div class="step-text">{narration}</div>
  <div class="step-bar"><div class="step-fill"></div></div>
</div>"""
        extra_css = f"""
.step-container {{ position:absolute; top:50%; left:60px; right:60px; transform:translateY(-50%); }}
.step-num {{ font-size:200px; font-weight:900; color:{s['accent']}18; line-height:1; position:absolute; top:-80px; right:0; font-family:monospace; }}
.step-divider {{ width:0; height:6px; background:linear-gradient(90deg,{s['accent']},{s['accent2']}); border-radius:3px; margin-bottom:40px; }}
.step-title {{ font-size:55px; color:{s['accent']}; font-weight:900; letter-spacing:2px; opacity:0; margin-bottom:30px; }}
.step-text {{ font-size:80px; font-weight:800; color:{s['text']}; line-height:1.25; opacity:0; }}
.step-bar {{ width:100%; height:4px; background:#ffffff15; border-radius:2px; margin-top:60px; }}
.step-fill {{ width:0%; height:100%; background:linear-gradient(90deg,{s['accent']},{s['accent2']}); border-radius:2px; }}
"""
        fill_pct = int((idx / total) * 100)
        anim_js = f"""
tl.to('.step-divider', {{width:'100%', duration:0.5, ease:'power2.inOut'}}, 0.2)
  .to('.step-title', {{opacity:1, x:0, duration:0.5, ease:'power2.out'}}, 0.5)
  .to('.step-text', {{opacity:1, y:0, duration:0.6, ease:'back.out(1.2)'}}, 0.7)
  .to('.step-fill', {{width:'{fill_pct}%', duration:0.8, ease:'power2.inOut'}}, 1.0)
"""

    elif style_type == "result":
        content = f"""
<div class="result-container">
  <div class="result-icon">✅</div>
  <div class="result-title">{caption or '結果'}</div>
  <div class="result-text">{narration}</div>
  <div class="result-glow"></div>
</div>"""
        extra_css = f"""
.result-container {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-55%); width:960px; text-align:center; }}
.result-icon {{ font-size:180px; opacity:0; transform:scale(0.3); }}
.result-title {{ font-size:55px; color:{s['accent']}; font-weight:900; letter-spacing:4px; opacity:0; margin:20px 0; }}
.result-text {{ font-size:78px; font-weight:800; color:{s['text']}; line-height:1.3; opacity:0; }}
.result-glow {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:600px; height:600px; background:radial-gradient(circle,{s['accent']}22,transparent 70%); border-radius:50%; opacity:0; z-index:-1; }}
"""
        anim_js = f"""
tl.to('.result-glow', {{opacity:1, scale:1.3, duration:1.0, ease:'power1.out'}}, 0)
  .to('.result-icon', {{opacity:1, scale:1, duration:0.6, ease:'back.out(2)'}}, 0.3)
  .to('.result-title', {{opacity:1, duration:0.4}}, 0.8)
  .to('.result-text', {{opacity:1, y:0, duration:0.6, ease:'power2.out'}}, 1.0)
"""

    elif style_type == "cta":
        content = f"""
<div class="cta-container">
  <div class="cta-ring"></div>
  <div class="cta-main">コメントに<br><span>AI</span>と<br>書いてください</div>
  <div class="cta-sub">{narration}</div>
  <div class="cta-arrow">→</div>
</div>"""
        extra_css = f"""
.cta-container {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:960px; text-align:center; }}
.cta-ring {{ width:400px; height:400px; border:6px solid {s['accent']}44; border-radius:50%; position:absolute; top:50%; left:50%; transform:translate(-50%,-120%); opacity:0; }}
.cta-main {{ font-size:100px; font-weight:900; color:{s['text']}; line-height:1.2; opacity:0; }}
.cta-main span {{ color:{s['accent']}; font-size:140px; }}
.cta-sub {{ font-size:50px; color:#ffffff88; margin-top:40px; opacity:0; }}
.cta-arrow {{ font-size:80px; color:{s['accent']}; opacity:0; margin-top:30px; }}
"""
        anim_js = f"""
tl.to('.cta-ring', {{opacity:1, scale:2, duration:1.0, ease:'power1.out'}}, 0)
  .to('.cta-main', {{opacity:1, scale:1, duration:0.7, ease:'back.out(1.5)'}}, 0.4)
  .to('.cta-sub', {{opacity:1, duration:0.5}}, 0.9)
  .to('.cta-arrow', {{opacity:1, x:0, duration:0.4}}, 1.1)
"""

    else:  # why
        content = f"""
<div class="why-container">
  <div class="why-badge">WHY</div>
  <div class="why-text">{narration}</div>
  <div class="why-emphasis">{caption}</div>
</div>"""
        extra_css = f"""
.why-container {{ position:absolute; top:50%; left:60px; right:60px; transform:translateY(-50%); }}
.why-badge {{ display:inline-block; background:{s['accent']}; color:#000; font-size:36px; font-weight:900; padding:10px 40px; border-radius:50px; letter-spacing:8px; opacity:0; margin-bottom:50px; }}
.why-text {{ font-size:82px; font-weight:800; color:{s['text']}; line-height:1.3; opacity:0; }}
.why-emphasis {{ font-size:55px; color:{s['accent']}; font-weight:700; margin-top:40px; opacity:0; border-left:8px solid {s['accent']}; padding-left:30px; }}
"""
        anim_js = f"""
tl.to('.why-badge', {{opacity:1, y:0, duration:0.5, ease:'back.out(1.5)'}}, 0.2)
  .to('.why-text', {{opacity:1, y:0, duration:0.7, ease:'power2.out'}}, 0.6)
  .to('.why-emphasis', {{opacity:1, x:0, duration:0.5, ease:'power2.out'}}, 1.1)
"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:{W}px; height:{H}px; background:{s['bg']}; overflow:hidden;
  font-family:'Noto Sans JP','Hiragino Sans','Yu Gothic',sans-serif; }}

/* グリッド背景 */
.grid {{ position:absolute; inset:0; opacity:0.04;
  background-image:linear-gradient({s['accent']} 1px,transparent 1px),
                   linear-gradient(90deg,{s['accent']} 1px,transparent 1px);
  background-size:80px 80px; }}

/* パーティクル */
.particle {{ position:absolute; background:{s['accent']}; border-radius:50%; opacity:0;
  animation:float 4s ease-in-out infinite; }}
@keyframes float {{
  0%,100%{{transform:translateY(0);opacity:0.3}}
  50%{{transform:translateY(-30px);opacity:0.8}}
}}

/* トップバー */
.topbar {{ position:absolute; top:0; left:0; right:0; height:6px;
  background:linear-gradient(90deg,{s['accent']},{s['accent2']},transparent); }}

/* ボトムバー */
.bottombar {{ position:absolute; bottom:0; left:0; right:0; height:6px;
  background:linear-gradient(90deg,transparent,{s['accent2']},{s['accent']}); }}

/* 進捗インジケーター */
.progress {{ position:absolute; top:20px; right:40px; display:flex; gap:10px; align-items:center; }}
.progress-dot {{ width:12px; height:12px; border-radius:50%; background:#ffffff22; }}
.progress-dot.active {{ background:{s['accent']}; box-shadow:0 0 10px {s['accent']}; }}

/* チャンネル名 */
.brand {{ position:absolute; bottom:30px; left:50%; transform:translateX(-50%);
  font-size:34px; color:#ffffff33; letter-spacing:4px; font-weight:700; }}

/* 汎用アニメーション初期値 */
.hook-text,.step-text,.result-text,.why-text,.why-emphasis,.cta-main {{ transform:translateY(30px); }}
.step-title {{ transform:translateX(-30px); }}
.cta-arrow {{ transform:translateX(-20px); }}

{extra_css}
</style>
</head>
<body>
<div data-composition-id="scene_{idx:02d}" data-width="{W}" data-height="{H}" data-duration="{dur:.1f}">

<div class="grid"></div>
{particles}
<div class="topbar"></div>
<div class="bottombar"></div>

<!-- 進捗ドット -->
<div class="progress">
{''.join([f'<div class="progress-dot{" active" if i <= idx else ""}"></div>' for i in range(total)])}
</div>

{content}

<div class="brand">AI CONDUIT</div>

</div>
<script>
const tl = gsap.timeline();
{anim_js}
window.__timelines = window.__timelines || {{}};
window.__timelines['scene_{idx:02d}'] = tl;
</script>
</body>
</html>"""
    return html

def render_scene_html(html_content: str, scene_id: str, audio_path: str) -> str:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    proj_dir = WORK_DIR / f"proj_{scene_id}"
    proj_dir.mkdir(exist_ok=True)
    (proj_dir / "index.html").write_text(html_content, encoding="utf-8")

    video_path = str(WORK_DIR / f"scene_{scene_id}_silent.mp4")
    r = subprocess.run(
        ["hyperframes", "render", str(proj_dir), "-o", video_path],
        capture_output=True, text=True, timeout=180
    )
    if not os.path.exists(video_path):
        print(f"  ⚠️ HyperFrames失敗: {r.stderr[:100]}")
        return None

    final_path = str(WORK_DIR / f"scene_{scene_id}.mp4")
    _run(["ffmpeg", "-y", "-i", video_path, "-i", audio_path,
          "-c:v", "libx264", "-c:a", "aac", "-shortest",
          "-pix_fmt", "yuv420p", final_path])
    return final_path if os.path.exists(final_path) else None

def generate_video(plan: dict, audio_files: list, ass_files: list = None) -> str:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    scenes = plan.get("scenes", [])
    total = len(scenes)
    scene_videos = []

    for i, (scene, audio_path) in enumerate(zip(scenes, audio_files)):
        if not os.path.exists(audio_path): continue
        dur = probe_dur(audio_path)
        html = generate_scene_html(scene, i, total, dur)
        print(f"  Scene {i+1}/{total}: {scene.get('title','?')} ({dur:.1f}秒)")
        video = render_scene_html(html, f"{i:02d}", audio_path)
        if video:
            scene_videos.append(video)
            print(f"    ✅")
        else:
            print(f"    ❌")

    if not scene_videos:
        raise Exception("シーン動画が生成されませんでした")

    concat_file = str(WORK_DIR / "concat.txt")
    with open(concat_file, "w") as f:
        for sv in scene_videos:
            f.write(f"file '{sv}'\n")

    output = str(WORK_DIR / "pipeline3_final.mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
          "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
          "-c:v", "libx264", "-preset", "fast", "-crf", "20",
          "-c:a", "aac", "-pix_fmt", "yuv420p", output])
    return output

if __name__ == "__main__":
    print("✅ hyperframes_engine.py v2 loaded")
