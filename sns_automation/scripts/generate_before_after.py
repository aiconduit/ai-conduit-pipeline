#!/usr/bin/env python3
"""
台本トピックに合わせたWEB UI Before/After動画を自動生成
Gemini → HTML生成 → Playwright SS → ffmpeg動画化
"""
import os, re, subprocess, requests, tempfile
from pathlib import Path

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def gemini_generate(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return ""
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30
    )
    if r.status_code != 200:
        return ""
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    # マークダウン除去
    text = re.sub(r"```html\s*|```\s*", "", text).strip()
    # 説明文除去
    text = re.sub(r'^.*?<!DOCTYPE', '<!DOCTYPE', text, flags=re.DOTALL)
    return text

def generate_before_after_video(plan: dict, output_path: str) -> bool:
    """台本からBefore/After動画を生成"""
    
    title = plan.get("selected_title", "Claude Code UI改善")
    scenes = plan.get("scenes", [])
    topic = scenes[2].get("narration", "") if len(scenes) > 2 else title
    
    print(f"   [Before/After] トピック: {topic[:40]}")
    
    # Before HTML生成
    before_prompt = f"""以下のトピックに関連したシンプルなWebフォームまたはUIコンポーネントを
スタイルなしの素のHTMLで生成してください。
トピック: {topic}
- CSSは最小限（ダサいデザイン）
- 日本語テキスト
- HTMLのみ出力（説明不要）"""
    
    before_html = gemini_generate(before_prompt)
    if not before_html or ("<!DOCTYPE" not in before_html and "<html" not in before_html and "<form" not in before_html and "<div" not in before_html):
        before_html = """<!DOCTYPE html><html><body style="font-family:sans-serif;padding:20px">
<h2>お問い合わせフォーム</h2>
<form>
<div><label>お名前: <input type="text" style="border:1px solid #ccc;padding:4px"></label></div><br>
<div><label>メール: <input type="email" style="border:1px solid #ccc;padding:4px"></label></div><br>
<div><label>メッセージ:<br><textarea style="border:1px solid #ccc;padding:4px" rows="4" cols="30"></textarea></label></div><br>
<button type="submit" style="background:#333;color:white;padding:8px 16px">送信する</button>
</form></body></html>"""
    
    # After HTML生成（Tailwind適用）
    after_prompt = f"""以下のHTMLをTailwind CSSを使って美しくモダンなデザインにしてください。
- Tailwind CDN: <script src="https://cdn.tailwindcss.com"></script>
- 角丸・シャドウ・グラデーションを使用
- 日本語テキスト維持
- HTMLのみ出力（説明不要）

{before_html[:800]}"""
    
    after_html = gemini_generate(after_prompt)
    if not after_html or "tailwind" not in after_html.lower():
        after_html = before_html  # フォールバック
    
    with tempfile.TemporaryDirectory() as tmpdir:
        before_file = f"{tmpdir}/before.html"
        after_file = f"{tmpdir}/after.html"
        before_png = f"{tmpdir}/before.png"
        after_png = f"{tmpdir}/after.png"
        before_clip = f"{tmpdir}/before_clip.mp4"
        after_clip = f"{tmpdir}/after_clip.mp4"
        
        Path(before_file).write_text(before_html, encoding='utf-8')
        Path(after_file).write_text(after_html, encoding='utf-8')
        
        # Playwrightでスクリーンショット
        ss_script = f"""
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={{"width": 540, "height": 960}})
        await page.goto("file://{before_file}")
        await page.screenshot(path="{before_png}")
        await page.goto("file://{after_file}")
        await page.screenshot(path="{after_png}")
        await browser.close()
asyncio.run(main())
"""
        r = subprocess.run(["python3", "-c", ss_script], capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            # Playwrightがない場合は自動インストール
            print(f"   Playwright未インストール → 自動インストール中...")
            subprocess.run(["python3", "-m", "playwright", "install", "chromium"], capture_output=True, timeout=60)
            subprocess.run(["python3", "-m", "playwright", "install-deps", "chromium"], capture_output=True, timeout=60)
            r = subprocess.run(["python3", "-c", ss_script], capture_output=True, text=True, timeout=30)
            if r.returncode != 0:
                print(f"   ⚠️ Playwright失敗: {r.stderr[:100]}")
                return False
        
        # Before/After動画生成
        vf = "scale=1080:960:force_original_aspect_ratio=decrease,pad=1080:960:(ow-iw)/2:(oh-ih)/2:color=white"
        subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", before_png, "-t", "2.5", "-vf", vf, "-r", "30", before_clip], capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", after_png, "-t", "2.5", "-vf", vf, "-r", "30", after_clip], capture_output=True)
        
        r2 = subprocess.run([
            "ffmpeg", "-y", "-i", before_clip, "-i", after_clip,
            "-filter_complex", "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=2.0[v]",
            "-map", "[v]", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", output_path
        ], capture_output=True)
        
        if r2.returncode == 0 and Path(output_path).exists():
            size = Path(output_path).stat().st_size
            print(f"   ✅ Before/After動画生成完了: {output_path} ({size//1024}KB)")
            return True
        else:
            print(f"   ❌ 動画生成失敗: {r2.stderr[:100]}")
            return False

if __name__ == "__main__":
    test_plan = {
        "selected_title": "Claude CodeのデザインシステムでUIが激変した",
        "scenes": [
            {"narration": "UIデザインが自動で改善されます", "mood": "hook"},
            {"narration": "Why", "mood": "value"},
            {"narration": "Tailwind CSSを使ってUIを自動で美しくします", "mood": "value"},
        ]
    }
    generate_before_after_video(test_plan, "/tmp/test_before_after.mp4")
