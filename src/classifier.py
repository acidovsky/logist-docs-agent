"""Классификация типа документа через DeepSeek (OpenAI-совместимый API)."""

import json
import logging
import os
import re
from typing import Any

from openai import OpenAI

logger = logging.getLogger(__name__)

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"


def _get_client() -> OpenAI:
    """Создать клиент OpenAI, настроенный на DeepSeek."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("Не задан DEEPSEEK_API_KEY")
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)


def _build_prompt(text: str, document_types: list[str]) -> str:
    """Сформировать промпт для классификатора."""
    types_str = ", ".join(document_types)
    truncated = text[:4000]
    return (
        "Ты — классификатор логистических документов.\n"
        f"Допустимые типы: {types_str}.\n"
        "Определи тип документа по тексту ниже.\n"
        "Верни СТРОГО JSON без пояснений и без markdown в формате:\n"
        '{"type": "<тип>", "confidence": <число от 0 до 1>}\n\n'
        f"Текст документа:\n{truncated}"
    )


def _parse_response(raw: str, allowed: list[str]) -> dict:
    """Распарсить ответ LLM и нормализовать поля."""
    data: Any = None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                data = None

    if not isinstance(data, dict):
        raise ValueError("Не удалось распарсить JSON от LLM")

    doc_type = data.get("type")
    if not isinstance(doc_type, str) or doc_type not in allowed:
        doc_type = "Другое"

    try:
        confidence = float(data.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    return {"type": doc_type, "confidence": confidence}


def classify_document(text: str, document_types: list[str]) -> dict:
    """Определить тип документа по тексту."""
    if not text.strip():
        return {"type": "Другое", "confidence": 0.0}

    allowed = list(document_types)
    if "Другое" not in allowed:
        allowed.append("Другое")

    try:
        client = _get_client()
        prompt = _build_prompt(text, allowed)
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = response.choices[0].message.content or ""
        return _parse_response(raw, allowed)
    except Exception:
        logger.exception("Ошибка классификации документа")
        return {"type": "Другое", "confidence": 0.0}
