"""Word-level transcription, used to time captions against the voiceover.

Two backends are supported. ``faster-whisper`` is the default: same models,
roughly 4x quicker on CPU, and it does not need PyTorch. ``whisper`` is the
reference implementation. Both are optional installs, and both return the same
shape, so the rest of the pipeline does not care which one ran.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

from shortsmith.config import TranscriptionConfig
from shortsmith.utils import log


class Word(TypedDict):
    """One transcribed word with its timing, in seconds from the start."""

    word: str
    start: float
    end: float


class TranscriptionError(RuntimeError):
    """Raised when the requested backend is unavailable or fails to load."""


def transcribe(audio_path: Path | str, config: TranscriptionConfig) -> list[Word]:
    """Transcribe ``audio_path`` to word-level timings.

    Returns an empty list if transcription is disabled or the backend fails —
    a video without captions is a better outcome than a failed render.
    """
    backend = (config.backend or "none").strip().lower()
    if backend in ("none", "off", "disabled"):
        return []

    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"audio file not found: {audio_path}")

    try:
        if backend in ("faster-whisper", "faster_whisper", "fasterwhisper"):
            return _faster_whisper(audio_path, config)
        if backend == "whisper":
            return _openai_whisper(audio_path, config)
    except TranscriptionError:
        raise
    except Exception as exc:  # noqa: BLE001 - degrade to no captions, keep the render
        log.warning("transcription failed (%s): %s - rendering without captions", backend, exc)
        return []

    raise TranscriptionError(
        f"unknown transcription backend {backend!r} (expected 'faster-whisper', 'whisper' or 'none')"
    )


def _faster_whisper(audio_path: Path, config: TranscriptionConfig) -> list[Word]:
    try:
        from faster_whisper import WhisperModel
    except ModuleNotFoundError as exc:
        raise TranscriptionError(
            "faster-whisper is not installed. Install it with:\n"
            "    pip install 'shortsmith[faster-whisper]'\n"
            'or switch backends with: transcription.backend = "whisper"'
        ) from exc

    log.info("transcribing with faster-whisper (%s, %s)", config.model, config.device)
    model = WhisperModel(config.model, device=config.device, compute_type=config.compute_type)
    segments, _info = model.transcribe(
        str(audio_path),
        word_timestamps=True,
        language=config.language,
    )

    words: list[Word] = []
    for segment in segments:
        for word in segment.words or []:
            text = str(word.word).strip()
            if text:
                words.append({"word": text, "start": float(word.start), "end": float(word.end)})
    return words


def _openai_whisper(audio_path: Path, config: TranscriptionConfig) -> list[Word]:
    try:
        import whisper
    except ModuleNotFoundError as exc:
        raise TranscriptionError(
            "openai-whisper is not installed. Install it with:\n"
            "    pip install 'shortsmith[whisper]'\n"
            'or use the faster default: transcription.backend = "faster-whisper"'
        ) from exc

    log.info("transcribing with openai-whisper (%s)", config.model)
    model = whisper.load_model(config.model, device=config.device)
    result: dict[str, Any] = model.transcribe(
        str(audio_path),
        word_timestamps=True,
        language=config.language,
        fp16=(config.device != "cpu"),
    )

    words: list[Word] = []
    for segment in result.get("segments", []):
        for word in segment.get("words") or []:
            text = str(word.get("word", "")).strip()
            if text:
                words.append(
                    {
                        "word": text,
                        "start": float(word.get("start", 0.0)),
                        "end": float(word.get("end", 0.0)),
                    }
                )
    return words

