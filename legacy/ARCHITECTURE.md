# Архитектура Logist Docs Agent (MVP)

## Поток данных
1. Streamlit: загрузка файлов.
2. Для каждого: PDF → изображения (pdf2image); OCR (Tesseract, rus+eng) → текст.
3. DeepSeek: classify(text) → {"type": str, "confidence": float}.
4. Загрузка config.yaml (обязательные типы).
5. Сверка: present / missing.
6. UI: чек-лист.
7. Кнопка «Сохранить пакет» → output/<timestamp>/ + result.json.

## Модули

### app.py
- st.file_uploader (multiple).
- Кнопка «Проверить».
- Чек-лист (st.success / st.error).
- Кнопка «Сохранить пакет».

### src/ocr.py
def extract_text(file_path: Path) -> str
- jpg/png: Pillow + pytesseract.
- pdf: pdf2image + pytesseract.
- lang="rus+eng".

### src/classifier.py
def classify_document(text: str) -> dict
- OpenAI-клиент, base_url=https://api.deepseek.com.
- Промпт: тип из config + «Другое».
- Возврат: {"type": str, "confidence": float}.

### src/checker.py
def check_completeness(found: list[str], required: list[str]) -> dict
- Возврат: {"present": [...], "missing": [...]}.

### src/config_loader.py
def load_config(path: Path = "config.yaml") -> dict
- Читает YAML, валидирует.

## config.yaml
required_documents:
  - ТТН
  - CMR
  - Счёт
  - Акт
document_types:
  - ТТН
  - CMR
  - Счёт
  - Акт
  - Другое

## requirements.txt
streamlit
pytesseract
pdf2image
Pillow
pyyaml
openai
python-dotenv

## Ограничения MVP
- Нет БД (всё в памяти + output/).
- Нет авторизации.
- Нет интеграций.

## После MVP
- Почта / SAP / 1С.
- Yandex Vision для рукописного.
- Деплой на Streamlit Cloud / VPS.
