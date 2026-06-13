from __future__ import annotations

import re
from pathlib import Path

from .models import SrtBlock
from .srt_writer import write_srt_blocks


TIMESTAMP_PATTERN = re.compile(
    r"^\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}"
)


class SrtParseError(ValueError):
    pass


def read_srt(path: str | Path) -> list[SrtBlock]:
    content = Path(path).read_text(encoding="utf-8-sig")
    return parse_srt(content)


def parse_srt(content: str) -> list[SrtBlock]:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        raise SrtParseError("SRT 파일이 비어 있습니다.")

    chunks = re.split(r"\n\s*\n", normalized)
    blocks: list[SrtBlock] = []
    fallback_index = 1

    for chunk in chunks:
        lines = [line.rstrip() for line in chunk.split("\n")]
        if len(lines) < 2:
            continue

        first_line = lines[0].strip().lstrip("\ufeff")
        if first_line.isdigit():
            index = int(first_line)
            timestamp_line_index = 1
        else:
            index = fallback_index
            timestamp_line_index = 0

        if len(lines) <= timestamp_line_index:
            continue

        timestamp = lines[timestamp_line_index].strip()
        if not TIMESTAMP_PATTERN.match(timestamp):
            raise SrtParseError(f"잘못된 SRT 시간 코드입니다: {timestamp}")

        text = "\n".join(lines[timestamp_line_index + 1 :]).strip()
        blocks.append(SrtBlock(index=index, timestamp=timestamp, text=text))
        fallback_index = index + 1

    if not blocks:
        raise SrtParseError("읽을 수 있는 SRT 블록이 없습니다.")
    return blocks


def save_srt_blocks(blocks: list[SrtBlock], path: str | Path) -> Path:
    return write_srt_blocks(blocks, path)

