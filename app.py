"""Streamlit-приложение Logist Docs Agent."""

import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.checker import check_completeness
from src.classifier import classify_document
from src.config_loader import load_config
from src.ocr import extract_text

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

st.set_page_config(page_title="Logist Docs Agent", layout="wide")
st.title("Logist Docs Agent")

try:
    config = load_config()
except Exception as exc:
    st.error(f"Ошибка загрузки конфига: {exc}")
    st.stop()

required = config["required_documents"]
document_types = config["document_types"]

uploaded = st.file_uploader(
    "Загрузите документы",
    type=["jpg", "jpeg", "png", "pdf"],
    accept_multiple_files=True,
)

if st.button("Проверить"):
    if not uploaded:
        st.warning("Загрузите хотя бы один файл")
    else:
        results: list[dict] = []
        for uploaded_file in uploaded:
            suffix = Path(uploaded_file.name).suffix
            tmp_path: str | None = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                text = extract_text(Path(tmp_path))
                cls = classify_document(text, document_types)
                results.append(
                    {
                        "filename": uploaded_file.name,
                        "type": cls["type"],
                        "confidence": cls["confidence"],
                        "text": text,
                    }
                )
            finally:
                if tmp_path is not None:
                    Path(tmp_path).unlink(missing_ok=True)

        st.session_state["results"] = results
        found_types = [r["type"] for r in results]
        st.session_state["check"] = check_completeness(found_types, required)

if "results" in st.session_state:
    results = st.session_state["results"]
    check = st.session_state["check"]

    st.subheader("Распознанные документы")
    st.dataframe(
        [
            {
                "Файл": r["filename"],
                "Тип": r["type"],
                "Уверенность": round(r["confidence"], 2),
            }
            for r in results
        ]
    )

    st.subheader("Чек-лист")
    for doc in check["present"]:
        st.success(f"✅ {doc}")
    for doc in check["missing"]:
        st.error(f"❌ {doc}")

    if st.button("Сохранить пакет"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path("output") / ts
        out_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": ts,
            "results": [
                {
                    "filename": r["filename"],
                    "type": r["type"],
                    "confidence": r["confidence"],
                }
                for r in results
            ],
            "check": check,
        }
        with (out_dir / "result.json").open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        st.success(f"Сохранено в {out_dir}")
