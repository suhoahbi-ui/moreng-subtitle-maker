from __future__ import annotations

from pathlib import Path

from .models import SubtitleSegment
from .utils import clean_inline_text


def write_transcript(segments: list[SubtitleSegment], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [clean_inline_text(segment.text) for segment in segments if clean_inline_text(segment.text)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    return path

