"""Загрузка и валидация config.yaml."""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def load_config(path: Path = Path("config.yaml")) -> dict:
    """Загрузить конфиг из YAML и провалидировать обязательные ключи."""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("config.yaml пуст или имеет неверный формат")

    for key in ("required_documents", "document_types"):
        if key not in data:
            raise ValueError(f"В config.yaml отсутствует ключ: {key}")

        value = data[key]
        if not isinstance(value, list) or not value:
            raise ValueError(f"Ключ {key} должен быть непустым списком")

        for item in value:
            if not isinstance(item, str):
                raise ValueError(f"Все элементы {key} должны быть строками")

    logger.info(
        "Конфиг загружен: %d обязательных, %d типов",
        len(data["required_documents"]),
        len(data["document_types"]),
    )
    return data
