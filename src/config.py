from __future__ import annotations

APP_TITLE = "MoReng Subtitle Maker"
APP_SUBTITLE = "모랭 자막 메이커"
APP_DESCRIPTION = "MP4/MP3를 SRT/TXT로 변환하고, Gemini API Key로 다국어 자막을 생성합니다."
CONTACT_EMAIL = "moneychecktruck@gmail.com"

SUPPORTED_MEDIA_EXTENSIONS = {".mp4", ".mp3"}

SOURCE_LANGUAGES = {
    "자동감지": None,
    "한국어": "ko",
    "영어": "en",
    "일본어": "ja",
    "중국어": "zh",
}

TARGET_LANGUAGES = {
    "영어": ("en", "English"),
    "일본어": ("ja", "Japanese"),
    "중국어": ("zh", "Chinese"),
    "베트남어": ("vi", "Vietnamese"),
}

WHISPER_MODELS = ["small", "medium", "large-v3"]
DEFAULT_SOURCE_LANGUAGE = "자동감지"
DEFAULT_WHISPER_MODEL = "medium"
DEFAULT_TARGET_LANGUAGE = "영어"

GEMINI_MODEL = "gemini-3.5-flash"
GEMINI_TRANSLATION_BATCH_SIZE = 25

KNOWN_SUBTITLE_LANGUAGE_CODES = {
    "ko",
    "en",
    "ja",
    "zh",
    "vi",
    "zh-cn",
    "zh-tw",
}
