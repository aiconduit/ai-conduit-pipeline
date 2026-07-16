import subprocess

BRAND = {
    "accent_color": "#22D3EE",
    "secondary_color": "#F59E0B",
    "bg_color": "#0B0F1A",
    "text_color": "#FFFFFF",
    "font_size_caption": 68,
    "caption_margin_v": 130,
    "watermark_text": "@AI_Conduit",
    "cta_text": "コメントに「conduit」で無料テンプレート",
    "handle": "@AI_Conduit",
}

def get_scene_template(scene_type="normal"):
    templates = {
        "hook": {"accent": BRAND["secondary_color"], "bg": BRAND["bg_color"], "font_size": 80},
        "normal": {"accent": BRAND["accent_color"], "bg": BRAND["bg_color"], "font_size": BRAND["font_size_caption"]},
        "cta": {"accent": BRAND["accent_color"], "bg": BRAND["bg_color"], "font_size": BRAND["font_size_caption"]},
    }
    return templates.get(scene_type, templates["normal"])

def add_watermark(video_path, output_path):
    watermark_ass = f"""[Script Info]
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, Bold, Alignment, MarginL, MarginR, MarginV
Style: WM,Arial,32,&H88FFFFFF,&H00000000,-1,7,20,20,20

[Events]
Format: Layer, Start, End, Style, Text
Dialogue: 0,0:00:00.00,9:59:59.99,WM,{BRAND["watermark_text"]}
"""
    wm_path = "/tmp/watermark.ass"
    with open(wm_path, "w") as f:
        f.write(watermark_ass)
    cmd = ["ffmpeg", "-y", "-i", video_path,
           "-vf", f"ass={wm_path}:fontsdir=/usr/share/fonts",
           "-c:v", "libx264", "-preset", "fast", "-crf", "22",
           "-c:a", "copy", "-pix_fmt", "yuv420p", output_path]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path
