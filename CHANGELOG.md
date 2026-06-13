# Changelog

## 0.1.0 - 2026-06-13

- Renamed public product to MoReng Subtitle Maker / 모랭 자막 메이커.
- Added a cleaner Tkinter card-style UI for local subtitle generation and translation.
- Added MP4/MP3 to SRT/TXT generation with faster-whisper.
- Added Gemini API Key masked input, local save, overwrite, and delete flow.
- Added SRT translation that preserves subtitle numbers and time codes.
- Added ffmpeg preflight guidance through `run_windows.bat` and `install_ffmpeg_then_run.bat`.
- Added `설치전_필독.txt`, `LICENSE`, `DISCLAIMER.md`, and landing page copy draft.
- Added Windows ZIP release script for `MoReng-Subtitle-Maker-v0.1.0-windows.zip`.
- Added GitHub Release notes draft in `docs/release-v0.1.0.md`.
- Fixed Windows batch launch scripts to avoid Korean text parsing issues in `cmd.exe`.
- Clarified manual ffmpeg download guidance: use `release builds` > `ffmpeg-release-essentials.zip`.
- Added a cropped ffmpeg download page guide image for README and landing page copy.
