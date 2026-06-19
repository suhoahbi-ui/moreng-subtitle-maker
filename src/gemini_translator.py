from __future__ import annotations

import json
import time
from dataclasses import replace
from pathlib import Path
from typing import Callable

from .config import (
    GEMINI_FALLBACK_MODELS,
    GEMINI_MODEL,
    GEMINI_TRANSLATION_BATCH_SIZE,
    GEMINI_TRANSLATION_RETRY_DELAYS_SECONDS,
)
from .models import SrtBlock
from .utils import wrap_subtitle_text

ProgressCallback = Callable[[str, float], None]


class GeminiTranslationError(RuntimeError):
    pass


class GeminiQuotaError(GeminiTranslationError):
    pass


class GeminiTranslator:
    def __init__(
        self,
        api_key: str,
        model_name: str = GEMINI_MODEL,
        fallback_models: tuple[str, ...] = GEMINI_FALLBACK_MODELS,
        batch_size: int = GEMINI_TRANSLATION_BATCH_SIZE,
        retry_delays: tuple[float, ...] = GEMINI_TRANSLATION_RETRY_DELAYS_SECONDS,
    ) -> None:
        if not api_key.strip():
            raise GeminiTranslationError("Gemini API Key가 비어 있습니다.")

        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise GeminiTranslationError(
                "google-genai가 설치되어 있지 않습니다. requirements.txt 설치를 확인해주세요."
            ) from exc

        self._types = types
        self._client = genai.Client(api_key=api_key.strip())
        self._model_names = self._dedupe_models((model_name, *fallback_models))
        self._batch_size = batch_size
        self._retry_delays = retry_delays

    def translate_blocks(
        self,
        blocks: list[SrtBlock],
        target_language_name: str,
        progress_callback: ProgressCallback | None = None,
    ) -> tuple[list[SrtBlock], list[str]]:
        if not blocks:
            raise GeminiTranslationError("번역할 SRT 블록이 없습니다.")

        translated_blocks: list[SrtBlock] = []
        failures: list[str] = []
        total = len(blocks)

        for start in range(0, total, self._batch_size):
            batch = blocks[start : start + self._batch_size]
            if progress_callback:
                progress_callback("번역 중", start / total)

            try:
                translated_text_by_id = self._translate_batch_with_retry(
                    batch,
                    target_language_name,
                    progress_callback=progress_callback,
                    progress_ratio=start / total,
                )
            except GeminiTranslationError:
                raise
            except Exception as exc:
                raise GeminiTranslationError(
                    f"블록 {batch[0].index}-{batch[-1].index}: 번역 요청 실패 - {exc}"
                ) from exc

            for block in batch:
                translated_text = translated_text_by_id.get(block.index)
                if translated_text:
                    translated_blocks.append(
                        replace(block, text=wrap_subtitle_text(translated_text))
                    )
                else:
                    translated_blocks.append(block)
                    failures.append(f"블록 {block.index}: 번역 결과 없음, 원문 유지")

        if progress_callback:
            progress_callback("번역 완료", 1.0)

        return translated_blocks, failures

    def _translate_batch_with_retry(
        self,
        blocks: list[SrtBlock],
        target_language_name: str,
        progress_callback: ProgressCallback | None = None,
        progress_ratio: float = 0.0,
    ) -> dict[int, str]:
        quota_errors: list[str] = []

        for model_index, model_name in enumerate(self._model_names):
            if progress_callback and model_index > 0:
                progress_callback(f"Gemini 모델 전환: {model_name}", progress_ratio)

            for attempt_index in range(len(self._retry_delays) + 1):
                try:
                    return self._translate_batch(blocks, target_language_name, model_name)
                except Exception as exc:
                    if self._is_quota_error(exc):
                        quota_errors.append(f"{model_name}: {exc}")
                        break

                    if not self._is_retryable_error(exc) or attempt_index >= len(self._retry_delays):
                        if model_index < len(self._model_names) - 1:
                            break
                        raise

                    delay = self._retry_delays[attempt_index]
                    if progress_callback:
                        retry_number = attempt_index + 1
                        progress_callback(
                            f"Gemini 혼잡으로 {int(delay)}초 후 재시도 {retry_number}",
                            progress_ratio,
                        )
                    time.sleep(delay)

        if quota_errors:
            raise GeminiQuotaError(
                "Gemini 요청 한도에 도달했습니다. 잠시 후 다시 시도하거나 Google/Gemini 사용량과 결제 설정을 확인해주세요."
            )

        raise GeminiTranslationError("Gemini 번역 요청 재시도에 실패했습니다.")

    def _translate_batch(
        self,
        blocks: list[SrtBlock],
        target_language_name: str,
        model_name: str,
    ) -> dict[int, str]:
        payload = [{"id": block.index, "text": block.text} for block in blocks]
        system_instruction = (
            "You are a professional subtitle translator. "
            "Translate only the subtitle text. Do not add commentary. "
            "Do not merge, split, reorder, remove, or invent entries. "
            "Return valid JSON only."
        )
        prompt = (
            f"Target language: {target_language_name}\n"
            "Translate each item into the target language.\n"
            "Return a JSON array with exactly this shape:\n"
            '[{"id": 1, "text": "translated subtitle"}]\n'
            "The id values must match the input id values.\n"
            "Keep terminology consistent across the batch.\n"
            "Input JSON:\n"
            f"{json.dumps(payload, ensure_ascii=False)}"
        )

        response = self._client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=self._types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        return self._parse_translation_response(response.text or "")

    @staticmethod
    def _parse_translation_response(response_text: str) -> dict[int, str]:
        text = response_text.strip()
        if not text:
            raise GeminiTranslationError("Gemini 응답이 비어 있습니다.")

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("[")
            end = text.rfind("]")
            if start == -1 or end == -1 or end <= start:
                raise
            data = json.loads(text[start : end + 1])

        if isinstance(data, dict):
            data = data.get("translations") or data.get("items") or data.get("data")

        if not isinstance(data, list):
            raise GeminiTranslationError("Gemini 응답이 JSON 배열이 아닙니다.")

        result: dict[int, str] = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                block_id = int(item.get("id"))
            except (TypeError, ValueError):
                continue
            translated_text = item.get("text")
            if isinstance(translated_text, str) and translated_text.strip():
                result[block_id] = translated_text.strip()
        return result

    @staticmethod
    def _dedupe_models(model_names: tuple[str, ...]) -> tuple[str, ...]:
        deduped: list[str] = []
        for model_name in model_names:
            value = model_name.strip()
            if value and value not in deduped:
                deduped.append(value)
        return tuple(deduped)

    @staticmethod
    def _is_quota_error(exc: Exception) -> bool:
        message = str(exc).lower()
        quota_markers = (
            "429",
            "resource_exhausted",
            "quota exceeded",
            "exceeded your current quota",
            "requestsperday",
            "free_tier_requests",
        )
        return any(marker in message for marker in quota_markers)

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        message = str(exc).lower()
        retryable_markers = (
            "503",
            "unavailable",
            "high demand",
            "temporarily",
            "timeout",
            "deadline",
        )
        return any(marker in message for marker in retryable_markers)


def write_failure_log(failures: list[str], output_srt_path: str | Path) -> Path | None:
    if not failures:
        return None
    path = Path(output_srt_path)
    log_path = path.with_name(f"{path.stem}.translation_failures.log")
    log_path.write_text("\n".join(failures) + "\n", encoding="utf-8")
    return log_path
