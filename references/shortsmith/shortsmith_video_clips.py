"""Turn a local media file into a frame-filling clip of an exact duration.

Both paths (video and still) end up cover-cropped to the output size with a
slow push-in, so a mixed sequence of clips and photos reads as one piece of
footage rather than a slideshow with video spliced in.
"""

from __future__ import annotations

import random
from pathlib import Path

from shortsmith.config import VideoConfig

_MOVIEPY_HINT = (
    "Rendering needs moviepy and ffmpeg. Install them with:\n    pip install 'shortsmith[render]'"
)


def _moviepy():
    """Import moviepy on demand, with a useful message when it is missing.

    Also restores ``Image.ANTIALIAS``: Pillow 10 removed the constant, but
    moviepy 1.x still refers to it in its resize effect. Aliasing it to
    LANCZOS (the same filter, renamed) keeps the 1.x line usable on modern
    Pillow without pinning anyone to an ancient release.
    """
    from PIL import Image

    if not hasattr(Image, "ANTIALIAS"):
        Image.ANTIALIAS = Image.Resampling.LANCZOS  # type: ignore[attr-defined]

    try:
        from moviepy import editor
    except ModuleNotFoundError as exc:
        if exc.name in ("moviepy", "moviepy.editor"):
            raise RuntimeError(_MOVIEPY_HINT) from exc
        raise
    return editor


def video_clip(path: Path, duration: float, config: VideoConfig, rng: random.Random):
    """Cover-crop a video file to the output frame with a slow push-in.

    A random in-point is used so the same stock clip appearing in two renders
    does not show the identical few seconds.
    """
    editor = _moviepy()
    clip = editor.VideoFileClip(str(path), audio=False)

    if clip.duration is None or clip.duration <= 0.5:
        clip.close()
        raise ValueError(f"clip too short to use: {path}")

    latest_start = max(0.0, clip.duration - duration - 0.1)
    start = rng.uniform(0, latest_start) if latest_start > 0 else 0.0
    clip = clip.subclip(start, min(start + duration, clip.duration))

    clip = _cover_crop(clip, config.size, editor)

    zoom = rng.uniform(config.video_zoom_min, config.video_zoom_max)
    clip = clip.resize(lambda t: 1 + zoom * (t / max(duration, 0.1)))
    clip = _center_crop(clip, config.size)

    return clip.set_duration(duration)


def image_clip(path: Path, duration: float, config: VideoConfig, rng: random.Random):
    """Ken Burns: a still, zoomed and drifted so it reads as motion."""
    import numpy as np
    from PIL import Image

    editor = _moviepy()
    target_w, target_h = config.size

    with Image.open(path) as handle:
        image = handle.convert("RGB")
        # Oversize slightly so there is room to drift without exposing edges.
        scale = max(target_w / image.width, target_h / image.height) * 1.15
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
        frame = np.array(image)

    base = editor.ImageClip(frame).set_duration(duration)

    zoom_start = rng.uniform(config.image_zoom_start, config.image_zoom_start + 0.018)
    zoom_end = rng.uniform(config.image_zoom_end, config.image_zoom_end + 0.015)
    base = base.resize(lambda t: zoom_start + (zoom_end - zoom_start) * (t / max(duration, 0.1)))

    # Drift between two random offsets, bounded by the slack from oversizing.
    max_dx = min(90, max(0, base.w - target_w) // 4)
    max_dy = min(120, max(0, base.h - target_h) // 4)
    centre_x = -((base.w - target_w) / 2)
    centre_y = -((base.h - target_h) / 2)

    x0 = centre_x + rng.uniform(-max_dx, max_dx)
    y0 = centre_y + rng.uniform(-max_dy, max_dy)
    x1 = centre_x + rng.uniform(-max_dx, max_dx)
    y1 = centre_y + rng.uniform(-max_dy, max_dy)

    moving = base.set_position(
        lambda t: (
            x0 + (x1 - x0) * (t / max(duration, 0.1)),
            y0 + (y1 - y0) * (t / max(duration, 0.1)),
        )
    )

    backdrop = editor.ColorClip(config.size, color=(0, 0, 0)).set_duration(duration)
    return editor.CompositeVideoClip([backdrop, moving], size=config.size).set_duration(duration)


def filler_clip(duration: float, config: VideoConfig, colour: tuple[int, int, int] = (18, 18, 20)):
    """Neutral dark card, used when no asset could be found for a beat."""
    editor = _moviepy()
    return editor.ColorClip(config.size, color=colour).set_duration(duration)


# ── framing helpers ──────────────────────────────────────────────────────────
def _cover_crop(clip, size: tuple[int, int], editor):
    """Scale to cover the target frame, then crop the overflow evenly."""
    target_w, target_h = size
    scale = max(target_w / clip.w, target_h / clip.h)
    clip = clip.resize(scale)
    return _center_crop(clip, size)


def _center_crop(clip, size: tuple[int, int]):
    target_w, target_h = size
    return clip.crop(
        x_center=clip.w / 2,
        y_center=clip.h / 2,
        width=min(target_w, clip.w),
        height=min(target_h, clip.h),
    )

