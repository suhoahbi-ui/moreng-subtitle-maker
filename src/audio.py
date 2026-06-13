from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import SUPPORTED_MEDIA_EXTENSIONS


class AudioProcessingError(RuntimeError):
    pass


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_tool_path(tool_name: str) -> str | None:
    candidates = [
        _project_root() / "tools" / "ffmpeg" / "bin" / f"{tool_name}.exe",
        _project_root() / f"{tool_name}.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return shutil.which(tool_name)


def require_ffmpeg() -> str:
    ffmpeg_path = resolve_tool_path("ffmpeg")
    if ffmpeg_path is None:
        raise AudioProcessingError(
            "ffmpeg를 찾을 수 없습니다. README의 ffmpeg 설치 방법을 확인해주세요."
        )
    return ffmpeg_path


def require_ffprobe() -> str:
    ffprobe_path = resolve_tool_path("ffprobe")
    if ffprobe_path is None:
        raise AudioProcessingError(
            "ffprobe를 찾을 수 없습니다. ffmpeg 설치 후 PATH 설정을 확인해주세요."
        )
    return ffprobe_path


def get_duration_seconds(media_path: str | Path) -> float | None:
    ffprobe_path = require_ffprobe()
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(media_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return None
    try:
        return float(completed.stdout.strip())
    except ValueError:
        return None


def extract_audio_to_wav(media_path: str | Path, temp_dir: str | Path) -> Path:
    ffmpeg_path = require_ffmpeg()
    media = Path(media_path)
    if media.suffix.lower() not in SUPPORTED_MEDIA_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_MEDIA_EXTENSIONS))
        raise AudioProcessingError(f"지원하지 않는 파일 형식입니다. 지원 형식: {supported}")

    output_path = Path(temp_dir) / f"{media.stem}.stt.wav"
    command = [
        ffmpeg_path,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(media),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-map",
        "0:a:0",
        str(output_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise AudioProcessingError(f"오디오 추출에 실패했습니다: {detail}")
    return output_path
