"""Распознавание текста из изображений и PDF через Tesseract."""

import logging
from pathlib import Path

import pytesseract
from PIL import Image
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

OCR_LANG = "rus+eng"


def _ocr_image(image: Image.Image) -> str:
    """Распознать текст на одном изображении."""
    return pytesseract.image_to_string(image, lang=OCR_LANG)


def extract_text(file_path: Path) -> str:
    """Извлечь текст из файла (jpg/jpeg/png/pdf)."""
    suffix = file_path.suffix.lower()

    if suffix in {".jpg", ".jpeg", ".png"}:
        with Image.open(file_path) as image:
            text = _ocr_image(image)
    elif suffix == ".pdf":
        pages = convert_from_path(str(file_path))
        text = "\n".join(_ocr_image(page) for page in pages)
    else:
        raise ValueError(f"Неподдерживаемый формат: {suffix}")

    logger.info("OCR выполнен для %s, длина текста: %d", file_path.name, len(text))
    return text
