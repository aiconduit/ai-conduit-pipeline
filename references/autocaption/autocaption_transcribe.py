"""Speech-to-text with word-level timestamps via faster-whisper."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Word:
    text: str
    start: float
    end: float


def _default_model(device: str, language: str | None) -> str:
    size = "medium" if device == "cuda" else "small"
    return f"{size}.en" if language == "en" else size


def _add_nvidia_pip_dirs_to_path() -> None:
    """Let CUDA DLLs from `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12` be found."""
    import site

    roots: list[str] = []
    try:
        roots += site.getsitepackages()
    except Exception:
        pass
    bin_dirs = [str(d) for root in roots for d in Path(root).glob("nvidia/*/bin")]
    if bin_dirs:
        os.environ["PATH"] = os.pathsep.join(bin_dirs) + os.pathsep + os.environ.get("PATH", "")


def _cuda_usable() -> bool:
    """True when CUDA inference can actually work, so device="auto" never
    downloads a GPU-sized model just to fail loading it."""
    try:
        import ctranslate2

        if ctranslate2.get_cuda_device_count() == 0:
            return False
    except Exception:
        return False
    if sys.platform == "win32":
        # a visible GPU is not enough: ctranslate2 also needs these runtime DLLs
        import ctypes

        _add_nvidia_pip_dirs_to_path()
        for dll in ("cublas64_12.dll", "cudnn64_9.dll"):
            try:
                ctypes.CDLL(dll)
            except OSError:
                return False
    return True


def transcribe(
    media_path: str | Path,
    model_name: str | None = None,
    device: str = "auto",
    language: str | None = "en",
    verbose: bool = True,
) -> list[Word]:
    """Transcribe an audio or video file into one Word per spoken word.

    device="auto" tries CUDA first and falls back to CPU int8 — GPU inference
    needs cuBLAS/cuDNN DLLs that are not installed by default on Windows.
    """
    attempts: list[tuple[str, str]] = []
    if device == "cuda" or (device == "auto" and _cuda_usable()):
        attempts.append(("cuda", "float16"))
    if device in ("auto", "cpu"):
        attempts.append(("cpu", "int8"))

    last_error: Exception | None = None
    for i, (dev, compute_type) in enumerate(attempts):
        name = model_name or _default_model(dev, language)
        try:
            if verbose:
                print(
                    f"[transcribe] loading model '{name}' on {dev} ({compute_type})..."
                    " (first use downloads it - one time)"
                )
            return _run(media_path, name, dev, compute_type, language, verbose)
        except Exception as error:  # CUDA/CTranslate2 failures surface here
            last_error = error
            if i + 1 < len(attempts):
                print(f"[transcribe] {dev} failed ({error}); falling back...", file=sys.stderr)
    raise last_error  # type: ignore[misc]


def _run(
    media_path: str | Path,
    model_name: str,
    device: str,
    compute_type: str,
    language: str | None,
    verbose: bool,
) -> list[Word]:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        str(media_path),
        language=language,
        word_timestamps=True,
        vad_filter=True,
    )
    words: list[Word] = []
    for segment in segments:
        if verbose:
            print(f"  [{segment.start:6.2f}s] {segment.text.strip()}")
        for w in segment.words or []:
            text = w.word.strip()
            if text:
                words.append(Word(text=text, start=float(w.start), end=float(w.end)))
    if verbose:
        print(f"[transcribe] {len(words)} words (language: {info.language})")
    return words

