"""Mix the voiceover with optional background music."""

from __future__ import annotations

import random
from pathlib import Path

from shortsmith.config import AudioConfig
from shortsmith.utils import log
from shortsmith.video.clips import _moviepy

MUSIC_SUFFIXES = (".mp3", ".wav", ".m4a", ".ogg", ".flac")


def voice_duration(audio_path: Path) -> float:
    """Length of the voiceover, trimmed slightly.

    MP3 decoders routinely report a duration a frame or two past the last
    real sample; reading that far produces a click or a hang. Backing off
    80ms is cheap insurance.
    """
    editor = _moviepy()
    clip = editor.AudioFileClip(str(audio_path))
    try:
        return max(0.1, clip.duration - 0.08)
    finally:
        clip.close()


def build_mix(
    voice_path: Path,
    duration: float,
    music_dir: Path | None,
    config: AudioConfig,
    *,
    rng: random.Random | None = None,
):
    """Return the final audio track: voice, plus music underneath if available."""
    editor = _moviepy()
    rng = rng or random.Random()

    voice = editor.AudioFileClip(str(voice_path)).volumex(config.voice_volume)
    voice = voice.audio_fadein(config.voice_fade_in).audio_fadeout(config.voice_fade_out)

    track = _pick_music(music_dir, rng)
    if track is None:
        return voice

    music = editor.AudioFileClip(str(track)).volumex(config.music_volume)

    # Loop short tracks, then take a random window so repeat renders do not
    # all open on the same bar.
    if music.duration < duration:
        loops = int(duration / music.duration) + 1
        music = editor.concatenate_audioclips([music] * loops)

    slack = music.duration - duration - 0.5
    start = rng.uniform(0, slack) if slack > 0 else 0.0
    music = music.subclip(start, start + duration)
    music = music.audio_fadein(config.music_fade_in).audio_fadeout(config.music_fade_out)

    log.info("mixed background music: %s", track.name)
    return editor.CompositeAudioClip([music, voice])


def _pick_music(music_dir: Path | None, rng: random.Random) -> Path | None:
    if music_dir is None or not Path(music_dir).is_dir():
        return None
    tracks = [
        path
        for path in sorted(Path(music_dir).iterdir())
        if path.is_file() and path.suffix.lower() in MUSIC_SUFFIXES
    ]
    return rng.choice(tracks) if tracks else None

