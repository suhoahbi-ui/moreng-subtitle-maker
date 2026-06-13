from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


VERSION = "v0.1.0"
ZIP_NAME = f"MoReng-Subtitle-Maker-{VERSION}-windows.zip"
PACKAGE_DIR_NAME = f"MoReng-Subtitle-Maker-{VERSION}-windows"

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
STAGING_DIR = DIST_DIR / PACKAGE_DIR_NAME
ZIP_PATH = DIST_DIR / ZIP_NAME

FILES_TO_INCLUDE = [
    "app.py",
    "README.md",
    "LICENSE",
    "DISCLAIMER.md",
    "CHANGELOG.md",
    "THIRD_PARTY_NOTICES.md",
    "설치전_필독.txt",
    "requirements.txt",
    "run_windows.bat",
    "install_ffmpeg_then_run.bat",
    "tools/ffmpeg/bin/.gitkeep",
    "docs/landing-copy.md",
]

DIRECTORIES_TO_INCLUDE = [
    "src",
]

FORBIDDEN_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".env",
    "ffmpeg.exe",
    "ffprobe.exe",
}

FORBIDDEN_SUFFIXES = {
    ".mp4",
    ".mp3",
    ".wav",
    ".m4a",
    ".srt",
    ".pyc",
}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & FORBIDDEN_NAMES:
        return True
    if path.name in FORBIDDEN_NAMES:
        return True
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        return True
    return False


def copy_file(relative_path: str) -> None:
    source = ROOT / relative_path
    if not source.exists():
        raise FileNotFoundError(f"Required release file is missing: {relative_path}")
    target = STAGING_DIR / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_directory(relative_path: str) -> None:
    source_dir = ROOT / relative_path
    if not source_dir.exists():
        raise FileNotFoundError(f"Required release directory is missing: {relative_path}")

    for source in source_dir.rglob("*"):
        if source.is_dir() or should_skip(source.relative_to(ROOT)):
            continue
        relative = source.relative_to(ROOT)
        target = STAGING_DIR / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def validate_staging() -> None:
    required_in_package = [
        "run_windows.bat",
        "README.md",
        "LICENSE",
        "DISCLAIMER.md",
        "app.py",
        "src/audio.py",
        "tools/ffmpeg/bin/.gitkeep",
    ]
    for relative_path in required_in_package:
        if not (STAGING_DIR / relative_path).exists():
            raise RuntimeError(f"Release package is missing required file: {relative_path}")

    forbidden_found: list[str] = []
    for path in STAGING_DIR.rglob("*"):
        if path.is_file() and should_skip(path.relative_to(STAGING_DIR)):
            forbidden_found.append(str(path.relative_to(STAGING_DIR)))

    if forbidden_found:
        joined = "\n".join(f" - {item}" for item in forbidden_found)
        raise RuntimeError(f"Forbidden files found in release package:\n{joined}")


def make_zip() -> Path:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    for relative_path in FILES_TO_INCLUDE:
        copy_file(relative_path)
    for relative_path in DIRECTORIES_TO_INCLUDE:
        copy_directory(relative_path)

    validate_staging()

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in STAGING_DIR.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(DIST_DIR))

    return ZIP_PATH


if __name__ == "__main__":
    zip_path = make_zip()
    print(f"Created release ZIP: {zip_path}")

