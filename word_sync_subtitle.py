import os
import json
import xml.etree.ElementTree as ET
import subprocess
import tempfile
from typing import List, Tuple
from dataclasses import dataclass

import requests
from PIL import Image, ImageDraw, ImageFont


@dataclass
class WordTimestamp:
    word: str
    start_sec: float
    end_sec: float


@dataclass
class SubtitleFrame:
    png_path: str
    start_sec: float
    end_sec: float


FONT_PATH = "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"
FONT_SIZE = 56
CANVAS_W = 1080
CANVAS_H = 1920
TEXT_Y = 960


def _load_font(size: int = FONT_SIZE) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def generate_word_timestamps(text: str, api_key: str) -> List[WordTimestamp]:
    words = text.split()
    ssml_parts = []
    for i, w in enumerate(words):
        ssml_parts.append(f'<mark name="w{i}"/>{w}')
    ssml = (
        '<speak>'
        + ' '.join(ssml_parts)
        + '</speak>'
    )

    resp = requests.post(
        f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}",
        headers={"Content-Type": "application/json"},
        json={
            "input": {"ssml": ssml},
            "voice": {"languageCode": "ja-JP", "name": "ja-JP-Neural2-B"},
            "audioConfig": {"audioEncoding": "LINEAR16"},
            "enableTimePointing": ["SSML_MARK"],
        },
    )
    resp.raise_for_status()
    data = resp.json()

    timepoints = data.get("timepoints", [])
    result: List[WordTimestamp] = []
    for i, w in enumerate(words):
        mark_name = f"w{i}"
        matching = [t for t in timepoints if t.get("markName") == mark_name]
        if not matching:
            continue
        start = float(matching[0]["timeSeconds"])
        end = start + 0.3
        if result:
            prev_end = result[-1].end_sec
            if start < prev_end:
                start = prev_end
            end = start + 0.3
        result.append(WordTimestamp(word=w, start_sec=start, end_sec=end))

    for i in range(len(result) - 1):
        result[i].end_sec = result[i + 1].start_sec

    if result:
        result[-1].end_sec = result[-1].start_sec + 0.3

    return result


def _render_single_word(
    word: str,
    is_keyword: bool,
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont,
) -> Image.Image:
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)

    bbox = dr.textbbox((0, 0), word, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (CANVAS_W - tw) // 2
    y = TEXT_Y - th // 2

    text_color = (255, 255, 0) if is_keyword else (255, 255, 255)
    outline_color = (0, 0, 0)
    outline_width = 3

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx == 0 and dy == 0:
                continue
            dr.text((x + dx, y + dy), word, font=font, fill=outline_color)
    dr.text((x, y), word, font=font, fill=text_color)

    return img


def _render_hormozi_line(
    words_with_flags: List[Tuple[str, bool]],
) -> Image.Image:
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    font = _load_font()

    segments = []
    total_w = 0
    for w, is_kw in words_with_flags:
        bbox = dr.textbbox((0, 0), w, font=font)
        tw = bbox[2] - bbox[0]
        segments.append((w, is_kw, tw))
        total_w += tw

    gap = 8
    total_w += gap * (len(segments) - 1)
    x = (CANVAS_W - total_w) // 2
    y = TEXT_Y - (bbox[3] - bbox[1]) // 2

    outline_width = 3
    for w, is_kw, tw in segments:
        color = (255, 255, 0) if is_kw else (255, 255, 255)
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx == 0 and dy == 0:
                    continue
                dr.text((x + dx, y + dy), w, font=font, fill=(0, 0, 0))
        dr.text((x, y), w, font=font, fill=color)
        x += tw + gap

    return img


def create_subtitle_frames(
    timestamps: List[WordTimestamp],
    style: str = "hormozi",
    keywords: List[str] = None,
) -> List[SubtitleFrame]:
    if keywords is None:
        keywords = []

    frames: List[SubtitleFrame] = []
    tmpdir = tempfile.mkdtemp()

    kw_set = set(w.lower() for w in keywords)

    if style == "hormozi":
        n = len(timestamps)
        for i in range(n):
            visible = []
            for j in range(i + 1):
                is_kw = timestamps[j].word.lower() in kw_set
                visible.append((timestamps[j].word, is_kw))
            img = _render_hormozi_line(visible)
            path = os.path.join(tmpdir, f"sub_{i:04d}.png")
            img.save(path)
            s = timestamps[i].start_sec
            e = timestamps[i].end_sec if i + 1 < n else timestamps[i].start_sec + 0.5
            frames.append(SubtitleFrame(png_path=path, start_sec=s, end_sec=e))

    elif style == "word_by_word":
        for ts in timestamps:
            is_kw = ts.word.lower() in kw_set
            img = _render_single_word(ts.word, is_kw, ImageDraw.Draw(
                Image.new("RGBA", (1, 1))), _load_font())
            path = os.path.join(tmpdir, f"sub_{ts.start_sec:.3f}.png")
            img.save(path)
            frames.append(SubtitleFrame(
                png_path=path,
                start_sec=ts.start_sec,
                end_sec=ts.end_sec,
            ))

    return frames


def burn_subtitles(
    video_path: str,
    subtitle_frames: List[SubtitleFrame],
    output_path: str,
) -> str:
    if not subtitle_frames:
        raise ValueError("no subtitle frames to burn")

    filter_parts = []
    for i, sf in enumerate(subtitle_frames):
        dur = sf.end_sec - sf.start_sec
        if dur <= 0:
            dur = 0.1
        filter_parts.append(
            f"movie={sf.png_path}:loop=1:format=png,"
            f"setpts=PTS-STARTPTS+{sf.start_sec}/TB,"
            f"trim=duration={dur}[sub{i}]"
        )

    overlay_parts = []
    for i in range(len(subtitle_frames)):
        overlay_parts.append(f"[sub{i}]")

    if overlay_parts:
        ov_concat = ("{" + "}[over].format(" + ",".join(
            f"[sub{j}]" for j in range(len(subtitle_frames))
        ).lstrip(",") + "})")
        pass

    valid_parts = [p for p in filter_parts if p.strip()]
    if not valid_parts:
        valid_parts = [
            f"movie={sf.png_path}:loop=1:format=png,"
            f"setpts=PTS-STARTPTS+{sf.start_sec}/TB,"
            f"trim=duration={max(sf.end_sec - sf.start_sec, 0.1)}[sub{i}]"
            for i, sf in enumerate(subtitle_frames)
        ]

    ov_inputs = "".join(f"[sub{i}]" for i in range(len(subtitle_frames)))
    filter_complex = (
        "nullsrc=size=1080x1920:rate=30[base];"
        + ";".join(valid_parts)
        + f";{ov_inputs}overlay=0:0:shortest=1[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        output_path,
    ]

    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output_path


if __name__ == "__main__":
    api_key = os.environ.get("GOOGLE_TTS_KEY", "")
    text = "これはテスト用の文章です。注目キーワードは黄色になります。"
    keywords = ["注目", "黄色"]

    if not api_key:
        print("GOOGLE_TTS_KEY not set; skipping API call, using synthetic timestamps")
        timestamps = [
            WordTimestamp("これは", 0.0, 0.3),
            WordTimestamp("テスト用の", 0.3, 0.6),
            WordTimestamp("文章です。", 0.6, 0.9),
            WordTimestamp("注目", 0.9, 1.2),
            WordTimestamp("キーワードは", 1.2, 1.5),
            WordTimestamp("黄色に", 1.5, 1.8),
            WordTimestamp("なります。", 1.8, 2.2),
        ]
    else:
        timestamps = generate_word_timestamps(text, api_key)

    print("timestamps:", timestamps)

    frames = create_subtitle_frames(timestamps, style="hormozi", keywords=keywords)
    print(f"generated {len(frames)} subtitle frames")

    for sf in frames[:3]:
        print(f"  {sf.png_path}: {sf.start_sec:.2f}s - {sf.end_sec:.2f}s")
