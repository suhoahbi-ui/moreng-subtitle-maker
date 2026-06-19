from __future__ import annotations

APP_TITLE = "MoReng Subtitle Maker"
APP_SUBTITLE = "모랭 자막 메이커"
APP_BRAND = "Made by MoneyCheck"
APP_DESCRIPTION = "MP4/MP3를 SRT/TXT로 변환하고, Gemini API Key로 다국어 자막을 생성합니다."
CONTACT_EMAIL = "moneychecktruck@gmail.com"
GITHUB_URL = "https://github.com/suhoahbi-ui/moreng-subtitle-maker"

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

GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_FALLBACK_MODELS = ("gemini-2.5-flash", "gemini-3.5-flash")
GEMINI_TRANSLATION_BATCH_SIZE = 50
GEMINI_TRANSLATION_RETRY_DELAYS_SECONDS = (5.0, 15.0, 35.0)

KNOWN_SUBTITLE_LANGUAGE_CODES = {
    "ko",
    "en",
    "ja",
    "zh",
    "vi",
    "zh-cn",
    "zh-tw",
}
