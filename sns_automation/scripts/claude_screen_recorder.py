#!/usr/bin/env python3
"""
claude_screen_recorder.py
Playwrightでclaude.aiを操作して画面録画する
台本のStep1/Step2シーンに合わせたClaude Code実画面を録画
"""
import subprocess, os, sys, asyncio, json, re
from pathlib import Path


async def record_claude_interaction(
    prompt: str,
    output_path: str,
    duration: float = 8.0,
    cookie_string: str = "",
) -> bool:
    """
    claude.aiを開いてプロンプトを入力し画面録画する
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("  playwright未インストール")
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1280,720",
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )

        # Cookieを設定
        if cookie_string:
            cookies = []
            for part in cookie_string.split(";"):
                part = part.strip()
                if "=" in part:
                    name, value = part.split("=", 1)
                    cookies.append({
                        "name": name.strip(),
                        "value": value.strip(),
                        "domain": ".claude.ai",
                        "path": "/",
                    })
            if cookies:
                await context.add_cookies(cookies)

        page = await context.new_page()

        # claude.aiを開く
        print(f"  claude.ai接続中...")
        await page.goto("https://claude.ai/new", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # ffmpegで画面録画開始（バックグラウンド）
        import tempfile
        tmp_video = str(Path(output_path).parent / f"raw_{Path(output_path).name}")
        
        ffmpeg_proc = subprocess.Popen([
            "ffmpeg", "-y",
            "-f", "x11grab",
            "-r", "30",
            "-s", "1280x720",
            "-i", ":99",  # Xvfb display
            "-t", str(duration + 3),
            "-c:v", "libx264", "-preset", "fast",
            "-pix_fmt", "yuv420p",
            tmp_video
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        await asyncio.sleep(1)

        # テキスト入力欄を探してプロンプトを入力
        try:
            # 入力欄を待つ
            await page.wait_for_selector(
                "div[contenteditable=\'true\'], textarea, div[data-testid=\'chat-input\']",
                timeout=10000
            )
            input_box = page.locator(
                "div[contenteditable=\'true\'], textarea, div[data-testid=\'chat-input\']"
            ).first
            
            print(f"  入力中: {prompt[:50]}")
            await input_box.click()
            await asyncio.sleep(0.5)
            
            # ゆっくりタイピング（リアルな感じ）
            for char in prompt:
                await input_box.type(char, delay=50)
            
            await asyncio.sleep(1)
            
            # Enterで送信
            await input_box.press("Enter")
            print("  送信完了")
            
            # 応答を待つ
            await asyncio.sleep(duration)
            
        except Exception as e:
            print(f"  入力エラー: {e}")
            await asyncio.sleep(duration)

        # ffmpegを停止
        ffmpeg_proc.terminate()
        ffmpeg_proc.wait()

        await browser.close()

        # 縦型（1080x1920）にクロップ・リサイズ
        if Path(tmp_video).exists():
            subprocess.run([
                "ffmpeg", "-y", "-i", tmp_video,
                "-vf", "crop=720:720:280:0,scale=1080:1080,pad=1080:1920:0:420:black",
                "-t", str(duration),
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-pix_fmt", "yuv420p",
                output_path
            ], capture_output=True)
            os.unlink(tmp_video)
            
            if Path(output_path).exists():
                size = Path(output_path).stat().st_size // 1024
                print(f"  ✅ 録画完了: {output_path} ({size}KB)")
                return True

        return False


def make_claude_prompt(scene_title: str, narration: str, script_content: str) -> str:
    """シーンに合ったClaude Codeへの入力プロンプトを生成"""
    
    # コマンドを抽出
    commands = []
    patterns = [
        r"\.claude/[\w/.-]+",
        r"disallowedTools:[^。、\n]+",
        r"name:[^。、\n]+",
        r"/[a-z][a-z0-9-]+",
    ]
    for pattern in patterns:
        for m in re.findall(pattern, narration):
            if m.strip() not in commands:
                commands.append(m.strip())
    
    if scene_title.lower() == "step1":
        if commands:
            return f"Create a file at {commands[0]} with the following content and explain what it does"
        return f"Explain how to: {narration[:80]}"
    elif scene_title.lower() == "step2":
        if commands:
            return f"Add {commands[0]} configuration to the Claude Code setup"
        return f"Show me how to configure: {narration[:80]}"
    elif scene_title.lower() == "solution":
        return f"What is the best way to {narration[:80]}"
    else:
        return narration[:100]


def generate_claude_recording(
    scene_title: str,
    narration: str,
    duration: float,
    output_path: str,
    cookie_string: str = "",
    script_content: str = "",
) -> bool:
    """Claude画面録画を生成（同期ラッパー）"""
    
    if scene_title.lower() not in ["step1", "step2", "solution"]:
        return False
    
    prompt = make_claude_prompt(scene_title, narration, script_content)
    print(f"  📹 Claude録画: {scene_title}")
    print(f"  プロンプト: {prompt[:60]}")
    
    try:
        return asyncio.run(record_claude_interaction(
            prompt=prompt,
            output_path=output_path,
            duration=duration,
            cookie_string=cookie_string,
        ))
    except Exception as e:
        print(f"  ❌ 録画失敗: {e}")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", required=True)
    parser.add_argument("--narration", required=True)
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--out", required=True)
    parser.add_argument("--cookie", default="")
    args = parser.parse_args()
    
    result = generate_claude_recording(
        args.scene, args.narration, args.duration, args.out, args.cookie
    )
    print("✅ 成功" if result else "❌ 失敗")
