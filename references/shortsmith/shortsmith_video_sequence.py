"""Stitch resolved assets into one continuous B-roll track."""

from __future__ import annotations

import random

from shortsmith.assets import AssetResolver
from shortsmith.config import Config
from shortsmith.models import MediaAsset, MediaKind, VisualSegment
from shortsmith.utils import log
from shortsmith.video.clips import _moviepy, filler_clip, image_clip, video_clip

#: Every Nth beat prefers a still. Mixing in Ken Burns stills breaks up the
#: uniform "stock video montage" texture and widens the usable asset pool.
STILL_EVERY = 3


def build_sequence(
    plan: list[VisualSegment],
    resolver: AssetResolver,
    duration: float,
    config: Config,
    *,
    rng: random.Random | None = None,
) -> tuple[object, list[dict]]:
    """Render ``plan`` into a single clip of exactly ``duration`` seconds.

    Returns the clip and a manifest describing what was actually used, which
    the caller writes into the render sidecar for attribution and debugging.
    """
    editor = _moviepy()
    rng = rng or random.Random(config.seed)
    video_config = config.video
    transition = video_config.transition

    clips: list[object] = []
    manifest: list[dict] = []
    elapsed = 0.0

    for index, segment in enumerate(plan):
        if elapsed >= duration - 0.2:
            break

        # Overlapping crossfades means each clip must be longer than its slot.
        length = min(segment.duration, duration - elapsed + (transition if clips else 0.0))
        if length < 1.0:
            break

        prefer = MediaKind.IMAGE if index % STILL_EVERY == 1 else MediaKind.VIDEO
        asset = resolver.resolve(segment.keyword, prefer=prefer)
        clip = _clip_for(asset, length, video_config, rng)

        if clips:
            clip = clip.crossfadein(transition)
        clip = clip.fx(editor.vfx.fadein, 0.06).fx(editor.vfx.fadeout, 0.10)

        clips.append(clip)
        manifest.append(
            {
                "keyword": segment.keyword,
                "start": round(elapsed, 2),
                "duration": round(length, 2),
                "asset": str(asset.path.name) if asset else None,
                "source": asset.source if asset else "filler",
                "credit": asset.credit if asset else "",
            }
        )
        elapsed += length - (transition if len(clips) > 1 else 0.0)

    if not clips:
        log.warning("no visual segments produced - rendering a plain background")
        return filler_clip(duration, video_config), manifest

    sequence = editor.concatenate_videoclips(clips, method="compose", padding=-transition)

    # Concatenation with negative padding can land a few frames short.
    if sequence.duration < duration:
        tail = filler_clip(duration - sequence.duration, video_config)
        sequence = editor.concatenate_videoclips([sequence, tail], method="compose")

    return sequence.subclip(0, duration), manifest


def _clip_for(asset: MediaAsset | None, length: float, video_config, rng: random.Random):
    """Build the clip for one beat, degrading to a filler card on any failure."""
    if asset is None:
        return filler_clip(length, video_config)
    try:
        if asset.kind is MediaKind.VIDEO:
            return video_clip(asset.path, length, video_config, rng)
        return image_clip(asset.path, length, video_config, rng)
    except Exception as exc:  # noqa: BLE001 - a corrupt download must not fail the render
        log.warning("could not use %s (%s): %s", asset.path.name, asset.query, exc)
        return filler_clip(length, video_config)

