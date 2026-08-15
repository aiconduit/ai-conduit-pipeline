#!/usr/bin/env python3
"""
台本の内容に合わせてClaude Codeターミナルデモ動画を自動生成
Gemini APIでトピック連動コマンドを生成
asciinema + agg + ffmpeg を使用
"""
import os, sys, json, subprocess, tempfile, requests, re
from pathlib import Path

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def generate_commands_with_gemini(title: str, step1: str, step2: str) -> list:
    """GeminiでトピックにあったClaude Codeコマンドを生成"""
    if not GEMINI_API_KEY:
        return None
    
    prompt = f"""以下のClaude Code動画のタイトルと手順に合わせて、
リアルなターミナルデモ用のコマンドシーケンスを生成してください。
WEB/UI系のスキル紹介動画です。視聴者が「おお！」と思えるような具体的なコマンドを使ってください。

タイトル: {title}
手順1: {step1}
手順2: {step2}

以下のJSON形式のみで出力してください（説明不要）:
{{
  "commands": [
    {{"type": "cmd", "text": "$ コマンド", "delay": 1.0}},
    {{"type": "out", "text": "  出力テキスト", "delay": 0.5}}
  ]
}}

ルール:
- commandsは5〜8行
- cmdは黄色で表示（実際のClaude Codeコマンド）
- outは緑色で表示（出力・結果）
- 日本語可
- 記号は最小限（ASCII文字優先）
- 最後は成功メッセージで終わる
"""
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        if r.status_code == 200:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            text = re.sub(r"```json\s*|```\s*", "", text).strip()
            m = re.search(r'\{[\s\S]*\}', text)
            if m:
                data = json.loads(m.group())
                return data.get("commands", [])
    except Exception as e:
        print(f"Gemini生成失敗: {e}")
    return None

def generate_terminal_demo(plan: dict, output_path: str, duration: int = 20):
    """台本からターミナルデモ動画を生成"""
    
    title = plan.get("selected_title", "Claude Code設定")
    scenes = plan.get("scenes", plan.get("script", {}).get("scenes", []))
    
    hook = scenes[0].get("narration", "") if scenes else ""
    step1 = scenes[3].get("caption", scenes[3].get("narration", "")) if len(scenes) > 3 else ""
    step2 = scenes[4].get("caption", scenes[4].get("narration", "")) if len(scenes) > 4 else ""
    result = scenes[5].get("narration", "") if len(scenes) > 5 else ""

    # Geminiでコマンド生成
    commands = generate_commands_with_gemini(title, step1, step2)
    
    if commands:
        # Gemini生成コマンドを使用
        script_lines = []
        script_lines.append('sleep 0.3')
        script_lines.append('echo "  Claude Code v2.1.183"')
        script_lines.append('echo ""')
        for cmd in commands:
            text = cmd.get("text", "").replace('"', '\\"').replace('`', '\\`')
            delay = cmd.get("delay", 0.5)
            script_lines.append(f'echo "{text}"')
            script_lines.append(f'sleep {delay}')
        demo_script = "#!/bin/bash\n" + "\n".join(script_lines)
    else:
        # フォールバック：固定パターン
        demo_script = f"""#!/bin/bash
sleep 0.3
echo "  Claude Code v2.1.183"
echo ""
echo "\\$ claude"
sleep 0.8
echo ""
echo "  > {hook[:45]}"
sleep 1.2
echo "  処理中..."
sleep 0.8
echo "  OK {step1[:40]}"
sleep 0.8
echo "  OK {step2[:40]}"
sleep 0.8
echo ""
echo "  完了: {result[:35]}"
sleep 1.5
echo ""
echo "  \\$ _"
sleep 1
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(demo_script)
        script_path = f.name
    os.chmod(script_path, 0o755)
    
    cast_path = output_path.replace('.mp4', '.cast')
    gif_path = output_path.replace('.mp4', '.gif')
    
    try:
        subprocess.run([
            "asciinema", "rec",
            "--command", f"bash {script_path}",
            "--cols", "60", "--rows", "18",
            "--overwrite", cast_path
        ], check=True, capture_output=True)
        
        agg_path = "/usr/local/bin/agg"
        if not os.path.exists(agg_path):
            agg_path = "agg"
        
        subprocess.run([
            agg_path,
            "--theme", "monokai",
            "--font-size", "22",
            "--cols", "60", "--rows", "18",
            cast_path, gif_path
        ], check=True, capture_output=True)
        
        subprocess.run([
            "ffmpeg", "-y", "-i", gif_path,
            "-vf", "scale=1080:-2:flags=lanczos,pad=1080:960:(ow-iw)/2:(oh-ih)/2:color=black",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-t", str(duration),
            output_path
        ], check=True, capture_output=True)
        
        print(f"✅ ターミナルデモ動画生成完了: {output_path}")
        return True
        
    except Exception as e:
        print(f"⚠️ ターミナルデモ生成失敗: {e}")
        return False
    finally:
        os.unlink(script_path)

if __name__ == "__main__":
    test_plan = {
        "selected_title": "Claude CodeのMCPでGitHub操作が自動になった",
        "scenes": [
            {"narration": "MCPでGitHubを自然言語で操作できます", "mood": "hook"},
            {"narration": "Why", "mood": "value"},
            {"narration": "Solution", "mood": "value"},
            {"narration": "設定完了", "caption": "claude mcp add github", "mood": "value"},
            {"narration": "手順2", "caption": "GITHUB_TOKEN を設定する", "mood": "value"},
            {"narration": "PRが自動で作成されるようになります", "mood": "value"},
            {"narration": "CTA", "mood": "cta"},
        ]
    }
    generate_terminal_demo(test_plan, "/tmp/test_demo2.mp4")
