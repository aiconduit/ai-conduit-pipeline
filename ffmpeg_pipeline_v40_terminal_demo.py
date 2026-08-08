#!/usr/bin/env python3
"""
v40 - Claude Codeターミナルデモ動画生成
PIL + FFmpegでリアルなターミナル画面をアニメーション生成
完全無料・外部API不要
"""
import os, sys, json, subprocess, time, random, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
WORK_DIR = Path("/tmp/ai_conduit_v40")
FRAMES_DIR = WORK_DIR / "frames"
for d in [OUTPUT_DIR, WORK_DIR, FRAMES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 解像度（YouTube Shorts縦型）
W, H = 1080, 1920
FPS = 15  # 処理速度優先

# カラーテーマ（Dracula風）
BG = (40, 42, 54)         # 背景
TERMINAL_BG = (30, 31, 41) # ターミナル背景
GREEN = (80, 250, 123)     # 成功
CYAN = (139, 233, 253)     # コマンド
YELLOW = (241, 250, 140)   # ファイル名
WHITE = (248, 248, 242)    # テキスト
PURPLE = (189, 147, 249)   # 強調
GRAY = (98, 114, 164)      # コメント
PROMPT = (255, 121, 198)   # プロンプト($)

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-71eab12699f047a5891e62268c66c241")

def generate_tts(text, output_path, voice="ja-JP-KeitaNeural"):
    """Edge TTSで音声生成"""
    import asyncio, edge_tts
    async def _gen():
        tts = edge_tts.Communicate(text, voice=voice, rate="+10%")
        await tts.save(output_path)
    asyncio.run(_gen())
    return output_path

def get_font(size, mono=False):
    """日本語対応フォント取得"""
    jp_paths = [
        '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
        '/System/Library/Fonts/ヒラギノ角ゴ ProN W6.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf',
    ]
    mono_paths = [
        '/System/Library/Fonts/Menlo.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    ]
    paths = (mono_paths + jp_paths) if mono else (jp_paths + mono_paths)
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

def generate_demo_script(topic, category):
    """DeepSeekでカテゴリに応じたデモスクリプトを生成"""
    import requests
    
    category_prompts = {
        "claude_code": f"""You are a Claude Code expert. Create a realistic terminal demo for "{topic}".
Show 5 steps of actual Claude Code usage that would impress Japanese developers.

STRICT RULES:
- command: Real claude CLI commands only. Examples:
  $ claude --dangerously-skip-permissions "Create REST API in app.py"
  $ claude "review src/main.py and fix bugs"
  $ cat app.py | claude "optimize this code"
  DO NOT use fake commands like /config
- output: 2-3 lines realistic terminal output. NO emoji. ASCII only.
  Examples: "Writing app.py...", "Tests: 12 passed", "Committed: feat: add auth"
- comment: Japanese max 10 chars. Show VALUE not action.
  BAD: "バージョン確認" GOOD: "8秒でAPI完成"
- Tell a story: problem to solution to result
Output ONLY valid JSON array:
[{{"step":1,"command":"$ claude --dangerously-skip-permissions \"Create a REST API\"","output":["Writing app.py...","Created 3 endpoints","[OK] Ready on :3000"],"comment":"8秒でAPI完成"}}]""",
        
        "gemini": f"""Gemini CLIを使った「{topic}」のデモ手順を6ステップで。
実際のgeminiコマンドと出力。
Output ONLY JSON array:
[{{"step":1,"command":"$ gemini --version","output":["Gemini CLI v1.5.0"],"comment":"バージョン確認"}},...]""",
        
        "codex": f"""OpenAI Codexを使った「{topic}」のデモ手順を6ステップで。
Output ONLY JSON array:
[{{"step":1,"command":"$ codex --version","output":["codex 0.1.0"],"comment":"バージョン確認"}},...]""",
    }
    
    prompt = category_prompts.get(category, category_prompts["claude_code"])
    
    import requests as rq
    r = rq.post("https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
        json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
              "max_tokens": 800, "temperature": 0.3},
        timeout=30)
    
    text = r.json()["choices"][0]["message"]["content"]
    import re
    m = re.search(r'\[.*\]', text, re.DOTALL)
    if m:
        return json.loads(m.group())
    return []

def make_terminal_frame(lines, cursor_line=-1, title="Claude Code", progress=0):
    """ターミナル画面のフレームを生成"""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    
    # タイトルバー（上部グラデーション風）
    d.rectangle([0, 0, W, 80], fill=(50, 52, 66))
    d.text((W//2, 40), title, fill=CYAN, font=get_font(32), anchor="mm")
    
    # ターミナルウィンドウ
    margin = 40
    term_y = 100
    term_h = H - 300
    d.rectangle([margin, term_y, W-margin, term_y+term_h], fill=TERMINAL_BG)
    
    # ウィンドウボタン（macOS風）
    for i, c in enumerate([(255,95,86), (255,189,46), (39,201,63)]):
        d.ellipse([margin+20+i*30, term_y+20, margin+35+i*30, term_y+35], fill=c)
    
    # ターミナルのタイトルバー
    d.text((W//2, term_y+27), "~/projects  —  claude", fill=GRAY, font=get_font(22), anchor="mm")
    
    # コンテンツエリア
    content_y = term_y + 60
    font_code = get_font(28)
    line_h = 42
    
    for i, line in enumerate(lines[-30:]):  # 最新30行を表示
        y = content_y + i * line_h
        if y > term_y + term_h - 20:
            break
        
        text = line.get("text", "")
        color = line.get("color", WHITE)
        
        # カーソル行をハイライト
        if i == cursor_line:
            d.rectangle([margin+5, y-3, W-margin-5, y+line_h-5], fill=(60, 62, 76))
        
        safe_t = "".join(c if (ord(c) < 0x2500 or 0x3000 <= ord(c) <= 0x9FFF or 0xFF00 <= ord(c) <= 0xFFEF or 0x30A0 <= ord(c) <= 0x30FF or 0x3040 <= ord(c) <= 0x309F) else "?" for c in (text or ""))
        d.text((margin+15, y), safe_t, fill=color, font=font_code)
        d.text((margin+15, y), safe_t, fill=color, font=font_code)
    
    # プログレスバー（下部）
    if progress > 0:
        pb_y = H - 200
        d.rectangle([margin, pb_y, W-margin, pb_y+8], fill=(60, 62, 76))
        d.rectangle([margin, pb_y, margin+int((W-2*margin)*progress), pb_y+8], fill=GREEN)
    
    # ロゴ（右下）
    d.text((W-margin, H-60), "AI Conduit", fill=GRAY, font=get_font(24), anchor="rm")
    
    return img

def render_terminal_animation(steps, output_path, topic):
    """ターミナルアニメーションを動画として生成"""
    frames = []
    lines = []
    frame_idx = 0
    
    # イントロ（0.5秒）
    intro_lines = [
        {"text": f"# {topic}", "color": PURPLE},
        {"text": "", "color": WHITE},
    ]
    for _ in range(int(FPS * 0.5)):
        img = make_terminal_frame(intro_lines, title=topic)
        frames.append(img)
    
    lines = intro_lines.copy()
    
    for step_idx, step in enumerate(steps):
        cmd = step.get("command", "")
        outputs = step.get("output", [])
        comment = step.get("comment", "")
        progress = (step_idx + 1) / len(steps)
        
        # プロンプト表示
        lines.append({"text": "", "color": WHITE})
        
        # コマンド表示（タイピングなし・高速化）
        display_lines = lines.copy()
        display_lines.append({"text": cmd + "_", "color": CYAN})
        img = make_terminal_frame(display_lines, cursor_line=len(display_lines)-1,
                                 title=topic, progress=progress)
        for _ in range(int(FPS * 0.3)):
            frames.append(img)
        
        lines.append({"text": cmd, "color": CYAN})
        
        # Enter後の間（0.3秒）
        for _ in range(int(FPS * 0.5)):
            img = make_terminal_frame(lines, title=topic, progress=progress)
            frames.append(img)
        
        # 出力を1行ずつ表示
        for out_line in outputs:
            # 出力の色を判断
            if "[OK]" in out_line or "success" in out_line.lower() or "完了" in out_line:
                color = GREEN
            elif "error" in out_line.lower() or "[ERR]" in out_line:
                color = (255, 85, 85)
            elif out_line.startswith("  ") or out_line.startswith("\t"):
                color = YELLOW
            else:
                color = WHITE
            
            lines.append({"text": out_line, "color": color})
            for _ in range(int(FPS * 0.5)):
                img = make_terminal_frame(lines, title=topic, progress=progress)
                frames.append(img)
        
        # ステップ間の間（0.5秒）
        for _ in range(int(FPS * 1.0)):
            img = make_terminal_frame(lines, title=topic, progress=progress)
            frames.append(img)
    
    # エンディング（1秒）
    lines.append({"text": "", "color": WHITE})
    lines.append({"text": "# 完了！詳細は概要欄をチェック", "color": GREEN})
    for _ in range(FPS):
        img = make_terminal_frame(lines, title=topic, progress=1.0)
        frames.append(img)
    
    # フレームをFFmpegでMP4に変換
    # TTS音声生成
    print(">> 音声生成中...")
    comments = [s.get("comment", "") for s in steps if s.get("comment")]
    narration_text = (
        f"{comments[0] if comments else topic}、その方法を解説します。"
        + "、".join(comments[1:4]) + f"。{topic}をマスターすれば開発速度が大幅に上がります。"
        + "詳細は概要欄のリンクから無料で受け取れます。コメントにAIと書いてください。"
    )
    try:
        generate_tts(narration_text, audio_path)
        print(f"[OK] 音声生成完了")
    except Exception as e:
        print(f"[WARN] TTS失敗: {e}")
        audio_path = None

    print(f">> {len(frames)}フレームをMP4に変換中...")
    
    # フレームを一時保存
    frame_paths = []
    for i, frame in enumerate(frames):
        p = str(FRAMES_DIR / f"frame_{i:05d}.png")
        frame.save(p)
        frame_paths.append(p)
    
    CINEMATIC_VF = "unsharp=lx=7:ly=7:la=1.5:cx=3:cy=3:ca=0.3,curves=r='0/0 0.25/0.28 0.75/0.78 1/1'\:g='0/0 0.5/0.49 1/0.96'\:b='0/0.04 0.4/0.44 1/0.92',eq=contrast=1.2:brightness=0.01:saturation=1.3:gamma=0.92,vignette=angle=PI/2.5,noise=alls=7:allf=t+u,gblur=sigma=1.5"
    # FFmpegでMP4生成
    import os as _os
    if _os.path.exists(audio_path):
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(FPS),
            "-i", str(FRAMES_DIR / "frame_%05d.png"),
            "-i", audio_path,
            "-vf", CINEMATIC_VF, "-preset", "slow", "-crf", "16",
"-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-shortest",
            str(output_path)
        ], capture_output=True)
    else:
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(FPS),
            "-i", str(FRAMES_DIR / "frame_%05d.png"),
            "-vf", CINEMATIC_VF, "-preset", "slow", "-crf", "16",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(output_path)
        ], capture_output=True)
    
    dur = len(frames) / FPS
    print(f"[OK] 完成: {output_path} ({dur:.1f}s)")
    return str(output_path)

def main():
    # news_content_plan.jsonを読み込み
    plan_path = ROOT_DIR / "sns_automation" / "news_content_plan.json"
    
    if plan_path.exists():
        with open(plan_path) as f:
            plan = json.load(f)
        topic = plan.get("selected_title", "Claude Code Tips")
        category = plan.get("category", "claude_code")
    else:
        topic = sys.argv[1] if len(sys.argv) > 1 else "Claude Code設定3選"
        category = sys.argv[2] if len(sys.argv) > 2 else "claude_code"
    
    print(f">> v40 ターミナルデモ動画生成")
    print(f"  トピック: {topic}")
    print(f"  カテゴリ: {category}")
    
    # DeepSeekでデモスクリプト生成
    print(">> デモスクリプト生成中...")
    steps = generate_demo_script(topic, category)
    
    if not steps:
        # フォールバック
        steps = [
            {"step":1,"command":f"$ claude '{topic}'","output":["処理中...","[OK] 完了"],"comment":"実行"},
            {"step":2,"command":"$ ls -la","output":["output.py  README.md","[OK] ファイル生成"],"comment":"確認"},
        ]
    
    print(f"[OK] {len(steps)}ステップのデモ生成完了")
    for s in steps:
        print(f"  [{s['step']}] {s.get('command','')[:50]}")
    
    # 動画生成
    output = OUTPUT_DIR / f"v2news_{topic[:30]}.mp4"
    render_terminal_animation(steps, output, topic)

if __name__ == "__main__":
    main()
