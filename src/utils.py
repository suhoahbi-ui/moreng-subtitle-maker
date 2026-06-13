from __future__ import annotations

import re
import textwrap
from pathlib import Path

from .config import KNOWN_SUBTITLE_LANGUAGE_CODES


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def clean_inline_text(text: str) -> str:
    return " ".join(text.replace("\r", "\n").replace("\n", " ").split())


def wrap_subtitle_text(text: str, width: int = 42) -> str:
    text = clean_inline_text(text)
    if not text:
        return ""

    if " " not in text and len(text) > width:
        return "\n".join(text[index : index + width] for index in range(0, len(text), width))

    lines = textwrap.wrap(
        text,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return "\n".join(lines) if lines else text


def normalize_language_code(language_code: str | None) -> str | None:
    if not language_code:
        return None
    code = language_code.strip().lower().replace("_", "-")
    if code.startswith("zh"):
        return "zh"
    if re.fullmatch(r"[a-z]{2,3}(-[a-z0-9]+)?", code):
        return code.split("-")[0]
    return None


def subtitle_output_paths(media_path: str | Path, output_dir: str | Path, language_code: str | None) -> tuple[Path, Path]:
    media = Path(media_path)
    output = ensure_directory(output_dir)
    suffix = f".{language_code}" if language_code else ""
    return output / f"{media.stem}{suffix}.srt", output / f"{media.stem}{suffix}.txt"


def translated_srt_output_path(source_srt_path: str | Path, output_dir: str | Path, target_code: str) -> Path:
    source = Path(source_srt_path)
    output = ensure_directory(output_dir)
    stem_parts = source.stem.split(".")

    if len(stem_parts) > 1 and stem_parts[-1].lower() in KNOWN_SUBTITLE_LANGUAGE_CODES:
        base_stem = ".".join(stem_parts[:-1])
    else:
        base_stem = source.stem

    return output / f"{base_stem}.{target_code}.srt"

