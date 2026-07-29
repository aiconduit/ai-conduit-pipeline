"""Configuration: dataclass defaults, file overrides (TOML/YAML), env overrides.

Precedence, lowest to highest::

    dataclass defaults  <  config file  <  SHORTSMITH_* environment variables

Every default here is brand-neutral. Nothing in this module knows about any
particular channel, niche, or storage backend.
"""

from __future__ import annotations

import os
import types
import typing
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any, get_args, get_origin, get_type_hints

#: Both spellings of a union — ``Optional[str]`` and ``str | None``.
_UNION_ORIGINS = (typing.Union, types.UnionType)

ENV_PREFIX = "SHORTSMITH_"

Color = tuple[int, int, int, int]


@dataclass(slots=True)
class VideoConfig:
    """Output geometry and B-roll pacing."""

    width: int = 1080
    height: int = 1920
    fps: int = 30
    #: Each B-roll beat lasts a random duration in this range.
    min_segment: float = 3.0
    max_segment: float = 5.0
    #: Crossfade length between beats, in seconds.
    transition: float = 0.32
    #: Subtle push-in applied to video clips (fraction of frame over the beat).
    video_zoom_min: float = 0.004
    video_zoom_max: float = 0.012
    #: Ken Burns zoom range applied to stills.
    image_zoom_start: float = 1.0
    image_zoom_end: float = 1.07
    codec: str = "libx264"
    audio_codec: str = "aac"
    preset: str = "veryfast"
    threads: int = 4
    #: Passed to ffmpeg verbatim, after the codec flags.
    ffmpeg_params: list[str] = field(
        default_factory=lambda: ["-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    )

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)


@dataclass(slots=True)
class CaptionConfig:
    """Karaoke-style caption styling.

    Sizes are tuned for a 1080x1920 frame; they are scaled automatically if the
    output size differs (see :meth:`scaled_for`).
    """

    enabled: bool = True
    #: Font search order. First existing file wins; falls back to a bundled
    #: DejaVu / PIL default if none are found.
    font_candidates: list[str] = field(default_factory=list)
    font_size: int = 82
    min_font_size: int = 58
    stroke_width: int = 7
    #: Vertical position as a fraction of frame height.
    y_fraction: float = 0.66
    #: Text must fit inside this fraction of frame width.
    safe_width_fraction: float = 0.82
    #: Canvas is wider than the safe area so italic overhang is not clipped.
    canvas_width_fraction: float = 0.94
    word_gap: int = 20
    line_gap: int = 6
    max_lines: int = 2
    #: Group breaks: whichever limit is hit first ends the on-screen chunk.
    max_words_per_group: int = 5
    min_words_per_group: int = 3
    max_group_seconds: float = 1.25
    max_group_chars: int = 28
    color: Color = (255, 255, 255, 255)
    highlight_color: Color = (255, 214, 10, 255)
    stroke_color: Color = (0, 0, 0, 255)
    #: Highlight the first word containing a digit, currency or percent sign.
    #: When no such word exists, the last word of the group is highlighted.
    highlight_numbers: bool = True
    uppercase: bool = True
    #: Scale-up "pop" applied over the first 100ms of each group.
    pop_scale: float = 0.035

    def scaled_for(self, width: int, height: int) -> CaptionConfig:
        """Return a copy with pixel sizes scaled from the 1080x1920 reference."""
        if width == 1080 and height == 1920:
            return self
        factor = width / 1080
        clone = _replace(self)
        clone.font_size = max(1, round(self.font_size * factor))
        clone.min_font_size = max(1, round(self.min_font_size * factor))
        clone.stroke_width = max(1, round(self.stroke_width * factor))
        clone.word_gap = max(0, round(self.word_gap * factor))
        clone.line_gap = max(0, round(self.line_gap * factor))
        return clone


@dataclass(slots=True)
class TranscriptionConfig:
    """Speech-to-text settings for caption timing."""

    #: "faster-whisper", "whisper", or "none" to disable transcription.
    backend: str = "faster-whisper"
    model: str = "small"
    language: str | None = None
    #: faster-whisper only; "int8" is a good CPU default.
    compute_type: str = "int8"
    device: str = "cpu"


@dataclass(slots=True)
class AudioConfig:
    """Voice/music mixing."""

    voice_volume: float = 1.0
    music_volume: float = 0.06
    music_fade_in: float = 1.1
    music_fade_out: float = 1.5
    voice_fade_in: float = 0.04
    voice_fade_out: float = 0.25


@dataclass(slots=True)
class WatermarkConfig:
    """Optional channel handle burned into a corner."""

    text: str = ""
    font_size: int = 34
    opacity: int = 150
    #: Pixel offset from the top-left corner.
    x: int = 36
    y: int = 36

    @property
    def enabled(self) -> bool:
        return bool(self.text.strip())


@dataclass(slots=True)
class PathsConfig:
    """Where inputs are read from and outputs are written to."""

    work_dir: str = "./workdir"
    output_dir: str = "./workdir/output"
    cache_dir: str = "./workdir/cache"
    music_dir: str = "./workdir/music"
    fonts_dir: str = "./fonts"

    def resolved(self) -> dict[str, Path]:
        return {name: Path(getattr(self, name)).expanduser() for name in _field_names(self)}


@dataclass(slots=True)
class ProvidersConfig:
    """Stock-footage lookup."""

    #: Tried in order until a usable asset is found.
    order: list[str] = field(default_factory=lambda: ["local", "pexels"])
    pexels_api_key: str = ""
    #: Directory scanned by the "local" provider for pre-downloaded media.
    local_media_dir: str = ""
    results_per_query: int = 8
    #: Keywords used to pad a plan that is shorter than the audio. Empty means
    #: "reuse the job's own keywords only" — set these for your niche.
    fallback_keywords: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Config:
    """Top-level config object. Build with :meth:`load`."""

    video: VideoConfig = field(default_factory=VideoConfig)
    captions: CaptionConfig = field(default_factory=CaptionConfig)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    watermark: WatermarkConfig = field(default_factory=WatermarkConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    providers: ProvidersConfig = field(default_factory=ProvidersConfig)
    #: Deterministic renders for tests/reproducibility. None means "random".
    seed: int | None = None

    # ── construction ─────────────────────────────────────────────────────────
    @classmethod
    def load(
        cls,
        path: Path | str | None = None,
        *,
        env: dict[str, str] | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> Config:
        """Build a Config from defaults, an optional file, env vars and overrides.

        ``path`` may be a ``.toml`` or ``.yaml``/``.yml`` file. If omitted, the
        first of ``shortsmith.toml`` / ``shortsmith.yaml`` / ``shortsmith.yml``
        found in the working directory is used, if any.
        """
        data: dict[str, Any] = {}

        resolved_path = Path(path) if path else _discover_config_file()
        if resolved_path is not None:
            if not resolved_path.exists():
                raise FileNotFoundError(f"config file not found: {resolved_path}")
            data = _read_config_file(resolved_path)

        if overrides:
            data = _deep_merge(data, overrides)

        config = _build(cls, data)
        config.apply_env(env if env is not None else os.environ)
        return config

    def apply_env(self, env: dict[str, str]) -> None:
        """Overlay ``SHORTSMITH_SECTION_KEY`` variables onto this config.

        Example: ``SHORTSMITH_PROVIDERS_PEXELS_API_KEY=abc123`` sets
        ``config.providers.pexels_api_key``. Values are coerced to the
        annotated type of the target field; list fields accept comma-separated
        values.
        """
        for section_field in fields(self):
            section = getattr(self, section_field.name)
            if not is_dataclass(section):
                continue
            prefix = f"{ENV_PREFIX}{section_field.name.upper()}_"
            hints = _hints(type(section))
            for leaf in fields(section):
                key = f"{prefix}{leaf.name.upper()}"
                if key in env:
                    setattr(section, leaf.name, _coerce(env[key], hints[leaf.name]))

    def to_dict(self) -> dict[str, Any]:
        """Plain-dict view, suitable for dumping into a render sidecar."""
        return _unstructure(self)


# ── file loading ─────────────────────────────────────────────────────────────
_CONFIG_FILENAMES = ("shortsmith.toml", "shortsmith.yaml", "shortsmith.yml")


def _discover_config_file() -> Path | None:
    for name in _CONFIG_FILENAMES:
        candidate = Path(name)
        if candidate.exists():
            return candidate
    return None


def _read_config_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".toml":
        try:
            import tomllib
        except ModuleNotFoundError:  # Python 3.10
            try:
                import tomli as tomllib  # type: ignore[no-redef]
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "TOML config needs Python 3.11+ or the 'tomli' package installed."
                ) from exc
        with open(path, "rb") as handle:
            return tomllib.load(handle)
    if suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "YAML config needs PyYAML. Install it with: pip install 'shortsmith[yaml]'"
            ) from exc
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if loaded is None:
            return {}
        if not isinstance(loaded, dict):
            raise ValueError(f"{path} must contain a mapping at the top level")
        return loaded
    raise ValueError(f"unsupported config format: {path.suffix} (use .toml, .yaml or .yml)")


# ── structuring helpers ──────────────────────────────────────────────────────
def _field_names(obj: Any) -> list[str]:
    return [f.name for f in fields(obj)]


def _replace(obj: Any) -> Any:
    """Shallow copy of a slots dataclass (``dataclasses.replace`` needs kwargs)."""
    return type(obj)(**{name: getattr(obj, name) for name in _field_names(obj)})


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


_HINTS: dict[type, dict[str, Any]] = {}


def _hints(cls: type) -> dict[str, Any]:
    """Resolved type hints for a dataclass.

    ``field.type`` is a plain string under ``from __future__ import
    annotations``, so we resolve once against this module's namespace and
    cache the result.
    """
    if cls not in _HINTS:
        _HINTS[cls] = get_type_hints(cls)
    return _HINTS[cls]


def _build(cls: type, data: dict[str, Any]) -> Any:
    """Recursively instantiate a dataclass tree from nested dicts."""
    kwargs: dict[str, Any] = {}
    known = {f.name: f for f in fields(cls)}
    hints = _hints(cls)

    unknown = set(data) - set(known)
    if unknown:
        raise ValueError(
            f"unknown config key(s) for [{cls.__name__}]: {', '.join(sorted(unknown))}"
        )

    for name, spec in known.items():
        if name not in data:
            if spec.default is MISSING and spec.default_factory is MISSING:  # type: ignore[misc]
                raise ValueError(f"missing required config key: {name}")
            continue

        value = data[name]
        target = hints[name]
        if is_dataclass(target) and isinstance(value, dict):
            kwargs[name] = _build(target, value)  # type: ignore[arg-type]
        elif is_dataclass(target):
            raise ValueError(
                f"config key '{name}' must be a table/mapping, got {type(value).__name__}"
            )
        else:
            try:
                kwargs[name] = _coerce(value, target)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"bad value for config key '{name}': {exc}") from exc

    return cls(**kwargs)


def _coerce(value: Any, annotation: Any) -> Any:
    """Best-effort conversion of a config/env value to its annotated type."""
    if annotation is Any or annotation is None:
        return value

    origin = get_origin(annotation)

    # Optional[X] / X | None — an empty-ish value means None, otherwise unwrap.
    if origin in _UNION_ORIGINS:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if value in (None, "", "none", "null"):
            return None
        return _coerce(value, args[0]) if args else value

    if origin is list:
        item_args = get_args(annotation)
        items = _as_list(value)
        return [_coerce(item, item_args[0]) for item in items] if item_args else items

    if origin is tuple:
        return _as_color(value)

    if annotation is bool:
        return _as_bool(value)
    if annotation is int:
        return int(value)
    if annotation is float:
        return float(value)
    if annotation is str:
        return str(value)
    return value


def _as_color(value: Any) -> Color:
    """Accept ``[r, g, b]``, ``[r, g, b, a]`` or ``"255,214,10"``."""
    rgba = [int(part) for part in _as_list(value)]
    if len(rgba) == 3:
        rgba.append(255)
    if len(rgba) != 4:
        raise ValueError(f"colour needs 3 or 4 components, got {value!r}")
    return tuple(max(0, min(255, channel)) for channel in rgba)  # type: ignore[return-value]


def _as_list(value: Any) -> list:
    if isinstance(value, (list, tuple)):
        return list(value)
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [value]


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _unstructure(obj: Any) -> Any:
    if is_dataclass(obj):
        return {name: _unstructure(getattr(obj, name)) for name in _field_names(obj)}
    if isinstance(obj, (list, tuple)):
        return [_unstructure(item) for item in obj]
    if isinstance(obj, Path):
        return str(obj)
    return obj

