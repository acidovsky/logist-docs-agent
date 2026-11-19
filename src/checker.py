"""Сверка найденных документов с обязательным списком."""

import logging

logger = logging.getLogger(__name__)


def check_completeness(found: list[str], required: list[str]) -> dict:
    """Вернуть списки присутствующих и отсутствующих документов."""
    found_set = set(found)
    present = [doc for doc in required if doc in found_set]
    missing = [doc for doc in required if doc not in found_set]
    logger.info("Сверка: найдено %d, отсутствует %d", len(present), len(missing))
    return {"present": present, "missing": missing}
