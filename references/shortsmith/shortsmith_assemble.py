"""The top-level render: job in, MP4 out."""

from __future__ import annotations

import contextlib
import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from shortsmith.assets import AssetResolver
from shortsmith.captions import group_words, transcribe
from shortsmith.captions.render import CaptionRenderer, render_watermark
from shortsmith.config import Config
from shortsmith.models import Job
from shortsmith.plan import build_plan
from shortsmith.providers import build as build_providers
from shortsmith.utils import log
from shortsmith.video.audio import build_mix, voice_duration
from shortsmith.video.clips import _moviepy
from shortsmith.video.sequence import build_sequence


@dataclass(slots=True)
class RenderResult:
    """What a render produced."""

    video: Path
    sidecar: Path
    duration: float
    caption_count: int
    segments: list[dict] = field(default_factory=list)


def build_video(job: Job, config: Config | None = None) -> RenderResult:
    """Render ``job`` and return the output paths.

    Raises on genuinely fatal problems (missing audio, unwritable output).
    Recoverable ones — a dead provider, a corrupt download, a transcription
    backend that will not load — degrade instead: the render still completes,
    with a warning in the log and the shortfall recorded in the sidecar.
    """
    config = config or Config.load()
    editor = _moviepy()
    rng = random.Random(config.seed)
    started = time.monotonic()

    audio_path = Path(job.audio).expanduser()
    if not audio_path.exists():
        raise FileNotFoundError(f"job audio not found: {audio_path}")

    paths = config.paths.resolved()
    output_dir = paths["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{job.name}.mp4"

    duration = voice_duration(audio_path)
    log.info("rendering %r - %.1fs of audio", job.name, duration)

    # ── 1. plan the visuals ──────────────────────────────────────────────────
    plan = build_plan(job, duration, config, rng=rng)
    log.info("plan: %d segments (%s)", len(plan), ", ".join(s.keyword for s in plan[:4]))

    # ── 2. resolve assets and stitch the B-roll ──────────────────────────────
    providers = build_providers(config.providers.order, config.providers)
    if not providers:
        log.warning("no stock providers available - visuals will be filler cards")
    resolver = AssetResolver(providers, config, paths["cache_dir"] / "media", rng=rng)
    visual, manifest = build_sequence(plan, resolver, duration, config, rng=rng)

    # ── 3. captions ──────────────────────────────────────────────────────────
    caption_clips = _build_captions(audio_path, duration, config, paths["cache_dir"], editor)

    # ── 4. watermark ─────────────────────────────────────────────────────────
    overlays: list[Any] = list(caption_clips)
    watermark = _build_watermark(config, duration, paths["cache_dir"], editor)
    if watermark is not None:
        overlays.insert(0, watermark)

    # ── 5. mix and write ─────────────────────────────────────────────────────
    audio_mix = build_mix(audio_path, duration, paths["music_dir"], config.audio, rng=rng)
    final = (
        editor.CompositeVideoClip([visual, *overlays], size=config.video.size)
        .set_audio(audio_mix)
        .set_duration(duration)
    )

    log.info("encoding to %s", output_path)
    final.write_videofile(
        str(output_path),
        fps=config.video.fps,
        codec=config.video.codec,
        audio_codec=config.video.audio_codec,
        preset=config.video.preset,
        threads=config.video.threads,
        ffmpeg_params=list(config.video.ffmpeg_params),
        logger=None,
    )

    for clip in (final, visual, audio_mix):
        # Cleanup only — a handle that will not close must not fail a render
        # that has already written its output.
        with contextlib.suppress(Exception):
            clip.close()

    sidecar = _write_sidecar(job, config, output_path, plan, manifest, len(caption_clips), duration)
    log.info("done in %.1fs -> %s", time.monotonic() - started, output_path)

    return RenderResult(
        video=output_path,
        sidecar=sidecar,
        duration=duration,
        caption_count=len(caption_clips),
        segments=manifest,
    )


# ── stages ───────────────────────────────────────────────────────────────────
def _build_captions(audio_path: Path, duration: float, config: Config, cache_dir: Path, editor):
    if not config.captions.enabled:
        return []

    words = transcribe(audio_path, config.transcription)
    if not words:
        log.warning("no transcription - rendering without captions")
        return []

    groups = group_words(words, duration, config.captions, rng=random.Random(config.seed))
    renderer = CaptionRenderer(config.captions, config.video.size, cache_dir / "captions")
    y_position = int(config.video.height * config.captions.y_fraction)
    pop = config.captions.pop_scale

    clips = []
    for group in groups:
        image = renderer.render(group.text)
        clip = (
            editor.ImageClip(str(image))
            .set_start(group.start)
            .set_duration(max(0.15, group.duration))
            .set_position(("center", y_position))
        )
        if pop > 0:
            # Scale up over the first 100ms so each group lands with a beat.
            clip = clip.resize(lambda t, pop=pop: (1 - pop) + pop * min(1.0, t / 0.10))
        clips.append(clip)

    log.info("captions: %d groups", len(clips))
    return clips


def _build_watermark(config: Config, duration: float, cache_dir: Path, editor):
    if not config.watermark.enabled:
        return None
    image = render_watermark(
        config.watermark.text,
        config.captions.font_candidates,
        config.watermark.font_size,
        config.watermark.opacity,
        cache_dir / "captions",
    )
    return (
        editor.ImageClip(str(image))
        .set_duration(duration)
        .set_position((config.watermark.x, config.watermark.y))
    )


def _write_sidecar(
    job: Job,
    config: Config,
    output_path: Path,
    plan,
    manifest: list[dict],
    caption_count: int,
    duration: float,
) -> Path:
    """Write the render metadata next to the MP4.

    Includes the asset manifest so stock attribution can be assembled later,
    and the resolved config so a render can be reproduced.
    """
    sidecar = output_path.with_suffix(".json")
    sidecar.write_text(
        json.dumps(
            {
                "name": job.name,
                "title": job.title,
                "description": job.description,
                "tags": job.tags,
                "video": output_path.name,
                "duration": round(duration, 2),
                "caption_groups": caption_count,
                "visual_plan": [segment.to_dict() for segment in plan],
                "assets": manifest,
                "credits": sorted({item["credit"] for item in manifest if item.get("credit")}),
                "config": config.to_dict(),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return sidecar

