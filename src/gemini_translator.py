from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Callable

from .config import GEMINI_MODEL, GEMINI_TRANSLATION_BATCH_SIZE
from .models import SrtBlock
from .utils import wrap_subtitle_text

ProgressCallback = Callable[[str, float], None]


class GeminiTranslationError(RuntimeError):
    pass


class GeminiTranslator:
    def __init__(
        self,
        api_key: str,
        model_name: str = GEMINI_MODEL,
        batch_size: int = GEMINI_TRANSLATION_BATCH_SIZE,
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
        self._model_name = model_name
        self._batch_size = batch_size

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
                translated_text_by_id = self._translate_batch(batch, target_language_name)
            except Exception as exc:
                translated_text_by_id = {}
                failures.append(
                    f"블록 {batch[0].index}-{batch[-1].index}: 번역 요청 실패 - {exc}"
                )

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

    def _translate_batch(self, blocks: list[SrtBlock], target_language_name: str) -> dict[int, str]:
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
            model=self._model_name,
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


def write_failure_log(failures: list[str], output_srt_path: str | Path) -> Path | None:
    if not failures:
        return None
    path = Path(output_srt_path)
    log_path = path.with_name(f"{path.stem}.translation_failures.log")
    log_path.write_text("\n".join(failures) + "\n", encoding="utf-8")
    return log_path

