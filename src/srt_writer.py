from __future__ import annotations

from pathlib import Path

from .models import SrtBlock, SubtitleSegment
from .utils import wrap_subtitle_text


def format_srt_timestamp(seconds: float) -> str:
    milliseconds_total = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds_total, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds_value, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds_value:02},{milliseconds:03}"


def segments_to_srt_blocks(segments: list[SubtitleSegment]) -> list[SrtBlock]:
    blocks: list[SrtBlock] = []
    for index, segment in enumerate(segments, start=1):
        timestamp = f"{format_srt_timestamp(segment.start)} --> {format_srt_timestamp(segment.end)}"
        blocks.append(SrtBlock(index=index, timestamp=timestamp, text=wrap_subtitle_text(segment.text)))
    return blocks


def write_srt(segments: list[SubtitleSegment], output_path: str | Path) -> Path:
    return write_srt_blocks(segments_to_srt_blocks(segments), output_path)


def write_srt_blocks(blocks: list[SrtBlock], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    chunks: list[str] = []
    for block in blocks:
        text = wrap_subtitle_text(block.text)
        chunks.append(f"{block.index}\n{block.timestamp}\n{text}")

    path.write_text("\n\n".join(chunks) + "\n", encoding="utf-8-sig")
    return path

