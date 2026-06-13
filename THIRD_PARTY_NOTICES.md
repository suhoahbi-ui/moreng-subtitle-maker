# Third-Party Notices

MoReng Subtitle Maker uses or integrates with the following third-party projects and services.

This file is a practical notice summary, not legal advice. Before commercial or large-scale distribution, review each dependency's current license and terms.

## faster-whisper

- Purpose: local speech-to-text inference
- Project: https://github.com/SYSTRAN/faster-whisper
- License: MIT License

## OpenAI Whisper model

- Purpose: speech recognition model family used through faster-whisper-compatible model files
- Project: https://github.com/openai/whisper
- License: MIT License for Whisper code and model weights

## Google Gen AI Python SDK

- Purpose: Gemini API requests for SRT translation
- Project: https://github.com/googleapis/python-genai
- License: Apache-2.0 License
- Note: Gemini API use is also subject to Google/Gemini API terms and the user's own API account limits, billing, and policies.

## keyring

- Purpose: storing the user's Gemini API Key in the local OS credential store when available
- Project: https://github.com/jaraco/keyring
- License: MIT License

## FFmpeg

- Purpose: extracting audio from MP4/MP3 files
- Project: https://ffmpeg.org/
- Legal information: https://www.ffmpeg.org/legal.html
- Note: ffmpeg and ffprobe executables are not bundled with this app. Users install them separately or place `ffmpeg.exe` and `ffprobe.exe` under `tools\ffmpeg\bin\`.

## Tkinter

- Purpose: local desktop GUI
- Project: included with Python standard library distributions

