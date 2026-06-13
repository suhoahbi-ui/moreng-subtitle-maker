from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubtitleSegment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class SrtBlock:
    index: int
    timestamp: str
    text: str


@dataclass(frozen=True)
class TranscriptionResult:
    segments: list[SubtitleSegment]
    detected_language: str | None
    language_probability: float | None = None

