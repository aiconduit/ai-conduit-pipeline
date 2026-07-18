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
    """drawtextフィルターでウォーターマーク追加(ASSより安定)"""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", "drawtext=text='@AI_Conduit':fontsize=28:fontcolor=white@0.6:x=20:y=20:box=0",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "copy", "-pix_fmt", "yuv420p", output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        # 失敗した場合はコピーのみ
        import shutil
        shutil.copy(video_path, output_path)
    return output_path
