"""Core data types passed between the planning, provider and render layers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from shortsmith.utils import clean_keyword, safe_stem


class MediaKind(str, Enum):
    """What a stock asset actually is, once downloaded."""

    VIDEO = "video"
    IMAGE = "image"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


@dataclass(slots=True)
class MediaCandidate:
    """A stock result that has not been downloaded yet."""

    kind: MediaKind
    url: str
    width: int = 0
    height: int = 0
    #: Free-form provider attribution, surfaced in the render sidecar JSON.
    credit: str = ""


@dataclass(slots=True)
class MediaAsset:
    """A stock result that now exists on local disk."""

    kind: MediaKind
    path: Path
    query: str
    source: str = "unknown"
    credit: str = ""


@dataclass(slots=True)
class VisualSegment:
    """One B-roll beat: show something matching ``keyword`` from ``start`` to ``end``."""

    start: float
    end: float
    keyword: str

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    def to_dict(self) -> dict[str, Any]:
        return {"start": round(self.start, 2), "end": round(self.end, 2), "keyword": self.keyword}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> VisualSegment | None:
        """Build a segment from loose external JSON, or ``None`` if unusable.

        Accepts ``keyword``/``search``/``query`` for the search term, since
        upstream tools (n8n, LLM planners) all spell it differently.
        """
        if not isinstance(raw, dict):
            return None
        keyword = clean_keyword(raw.get("keyword") or raw.get("search") or raw.get("query") or "")
        if not keyword:
            return None
        try:
            start = float(raw.get("start", 0.0))
            end = float(raw.get("end", 0.0))
        except (TypeError, ValueError):
            start, end = 0.0, 0.0
        return cls(start=start, end=end, keyword=keyword)


@dataclass(slots=True)
class CaptionGroup:
    """A chunk of words shown on screen together."""

    text: str
    start: float
    end: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass(slots=True)
class Job:
    """One render request.

    ``name`` is used for the output filename and cache keys, so it is
    sanitised on construction — external callers (webhooks, queue files) can
    put anything in there.
    """

    name: str
    audio: Path | str
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    visual_plan: list[VisualSegment] = field(default_factory=list)
    #: Extra keywords used to pad the plan when it is shorter than the audio.
    keywords: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = safe_stem(self.name)
        if not self.name:
            raise ValueError("Job.name must contain at least one alphanumeric character")
        self.audio = Path(self.audio)
        if not self.title:
            self.title = self.name

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Job:
        """Build a Job from a plain dict (CLI JSON file, webhook payload, queue entry).

        Legacy key names from the original assembler (``filename``, ``body``,
        ``hashtags``, ``audioFile``) are accepted as aliases.
        """
        name = raw.get("name") or raw.get("filename") or ""
        audio = raw.get("audio") or raw.get("audioFile") or raw.get("localAudioFile") or ""
        if not audio:
            raise ValueError("job is missing an 'audio' path")

        tags = raw.get("tags") or raw.get("hashtags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        keywords = raw.get("keywords") or raw.get("search_keywords") or []
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",") if k.strip()]

        plan_raw = raw.get("visual_plan") or []
        plan = [seg for seg in (VisualSegment.from_dict(s) for s in plan_raw) if seg is not None]

        return cls(
            name=name,
            audio=audio,
            title=raw.get("title") or "",
            description=raw.get("description") or raw.get("body") or "",
            tags=list(tags),
            visual_plan=plan,
            keywords=list(keywords),
        )

    @classmethod
    def from_json_file(cls, path: Path | str) -> Job:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

