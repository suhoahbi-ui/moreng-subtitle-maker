from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .models import SubtitleSegment, TranscriptionResult

ProgressCallback = Callable[[str, float], None]


class WhisperEngineError(RuntimeError):
    pass


class WhisperEngine:
    def __init__(self, model_size: str, device: str = "cpu", compute_type: str = "int8") -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise WhisperEngineError(
                "faster-whisper가 설치되어 있지 않습니다. requirements.txt 설치를 확인해주세요."
            ) from exc

        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(
        self,
        audio_path: str | Path,
        language_code: str | None,
        duration_seconds: float | None = None,
        progress_callback: ProgressCallback | None = None,
    ) -> TranscriptionResult:
        if progress_callback:
            progress_callback("음성 인식 준비 중", 0.0)

        try:
            segments_iterable, info = self.model.transcribe(
                str(audio_path),
                language=language_code,
                beam_size=5,
                vad_filter=True,
                word_timestamps=False,
            )
        except Exception as exc:
            raise WhisperEngineError(f"음성 인식 시작에 실패했습니다: {exc}") from exc

        segments: list[SubtitleSegment] = []
        for segment in segments_iterable:
            text = segment.text.strip()
            if text:
                segments.append(
                    SubtitleSegment(
                        start=float(segment.start),
                        end=float(segment.end),
                        text=text,
                    )
                )

            if progress_callback and duration_seconds:
                ratio = min(1.0, max(0.0, float(segment.end) / duration_seconds))
                progress_callback("음성 인식 중", ratio)

        if progress_callback:
            progress_callback("음성 인식 완료", 1.0)

        return TranscriptionResult(
            segments=segments,
            detected_language=getattr(info, "language", None),
            language_probability=getattr(info, "language_probability", None),
        )

