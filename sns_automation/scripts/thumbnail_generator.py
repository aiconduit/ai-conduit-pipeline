#!/usr/bin/env python3
"""
AI Conduit サムネイル生成システム
Pollinations.ai + Pillow でプロ品質のイントロフレームを生成
"""
import requests, os, sys, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-71eab12699f047a5891e62268c66c241")
CEREBRAS_API_KEY = "csk-t9j3w5ne42jphxcj54x532hn8hhcv8cvk4r96563xrvvfvnp"
OPENROUTER_API_KEY = "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"
FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def get_font(size):
    for p in FONT_PATHS:
        if Path(p).exists():
            try:
                from PIL import ImageFont
                return ImageFont.truetype(p, size)
            except: pass
    from PIL import ImageFont
    return ImageFont.load_default()

def generate_bg_prompt(title: str, category: str = "tech") -> str:
    """Cerebras/OpenRouterでサムネイル背景プロンプトを生成"""
    prompt_text = (
        f"Generate a short English image prompt (max 20 words) for a YouTube Short thumbnail background about: {title}. "
        f"Style: cinematic, dark, professional, tech, 4K. "
        f"NO text, NO faces. Only background visual. Output prompt only."
    )
    for api_url, api_key, model in [
        ("https://api.cerebras.ai/v1/chat/completions", CEREBRAS_API_KEY, "gpt-oss-120b"),
        ("https://openrouter.ai/api/v1/chat/completions", OPENROUTER_API_KEY, "meta-llama/llama-3.3-70b-instruct"),
    ]:
        try:
            r = requests.post(api_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt_text}],
                      "max_tokens": 60, "temperature": 0.7}, timeout=15)
            if r.status_code == 200:
                msg = r.json()["choices"][0]["message"]
                text = msg.get("content") or msg.get("reasoning") or ""
                if text:
                    return text.strip()
        except Exception:
            continue
    return f"cinematic dark tech background {title}"

def generate_bg_image(prompt: str, width=1080, height=1920) -> Image.Image:
    """Pollinations.aiで背景画像生成"""
    import urllib.parse
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)},dark,cinematic,4K?width={width}&height={height}&nologo=true&seed={hash(prompt) % 9999}"
    r = requests.get(url, timeout=60)
    if r.status_code == 200:
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        return img.resize((width, height), Image.LANCZOS)
    return None

def add_overlay(img: Image.Image, title: str, hook_text: str = "") -> Image.Image:
    """プロ品質のテキストオーバーレイを追加"""
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 下部グラデーション（テキスト可読性向上）
    for y in range(H // 2, H):
        alpha = int(180 * (y - H // 2) / (H // 2))
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    
    # ブランドバー（上部）
    draw.rectangle([(0, 0), (W, 80)], fill=(0, 0, 0, 160))
    logo_font = get_font(36)
    draw.text((30, 22), "AI Conduit", font=logo_font, fill=(0, 200, 255, 255))
    
    # メインタイトル（下部・大きく）
    title_font = get_font(90)
    # タイトルを2行に分割
    words = title[:40]
    mid = len(words) // 2
    # スペースで分割
    parts = words.split(" ")
    line1 = " ".join(parts[:len(parts)//2])
    line2 = " ".join(parts[len(parts)//2:])
    
    for line, y_pos in [(line1, H - 280), (line2, H - 180)]:
        if not line: continue
        # 縁取り
        for dx, dy in [(-3,-3),(3,-3),(-3,3),(3,3),(0,-3),(0,3),(-3,0),(3,0)]:
            draw.text((30 + dx, y_pos + dy), line, font=title_font, fill=(0, 0, 0, 255))
        draw.text((30, y_pos), line, font=title_font, fill=(255, 255, 255, 255))
    
    # フックテキスト（黄色・強調）
    if hook_text:
        hook_font = get_font(60)
        draw.text((30, H - 370), hook_text[:20], font=hook_font, fill=(255, 220, 0, 255))
    
    # 合成
    result = Image.alpha_composite(img.convert("RGBA"), overlay)
    return result.convert("RGB")

def generate_thumbnail(title: str, hook_text: str = "", output_path: str = "/tmp/thumbnail.jpg", category: str = "tech") -> str:
    """メイン関数：タイトルからサムネイルを生成"""
    print(f"[Thumbnail] タイトル: {title[:30]}")
    
    # 背景プロンプト生成
    bg_prompt = generate_bg_prompt(title, category)
    print(f"[Thumbnail] 背景プロンプト: {bg_prompt}")
    
    # 背景画像生成
    bg = generate_bg_image(bg_prompt)
    if bg is None:
        # フォールバック：グラデーション背景
        bg = Image.new("RGBA", (1080, 1920), (10, 10, 30, 255))
        draw = ImageDraw.Draw(bg)
        for y in range(1920):
            r_val = int(10 + 20 * y / 1920)
            g_val = int(10 + 30 * y / 1920)
            b_val = int(30 + 60 * y / 1920)
            draw.line([(0, y), (1080, y)], fill=(r_val, g_val, b_val, 255))
    
    # テキストオーバーレイ追加
    result = add_overlay(bg, title, hook_text)
    
    # 保存
    result.save(output_path, "JPEG", quality=95)
    size = Path(output_path).stat().st_size // 1024
    print(f"[Thumbnail] 完成: {output_path} ({size}KB)")
    return output_path

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "Claude Codeで残業が消えた"
    hook = sys.argv[2] if len(sys.argv) > 2 else "99%が知らない"
    generate_thumbnail(title, hook, "/tmp/test_thumbnail_final.jpg")
    print("完了")
