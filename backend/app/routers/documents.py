"""Роутер документов сделки: загрузка, список, чек-лист и удаление."""

import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session, select

from ..auth import get_current_user
from ..database import get_session
from ..models import Deal, Document, User, utcnow
from ..schemas import ChecklistRead, DocumentRead
from ..services import classifier, ocr

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["documents"])

# Папка для файлов относительно рабочей директории backend.
UPLOAD_DIR = Path("uploads")

# Обязательные документы и допустимые типы (пока хардкод на бэкенде).
REQUIRED_DOCUMENTS = ["ТТН", "CMR", "Счёт", "Акт"]
DOCUMENT_TYPES = ["ТТН", "CMR", "Счёт", "Акт", "Другое"]
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


def _get_owned_deal(deal_id: int, current_user: User, session: Session) -> Deal:
    """Найти сделку, принадлежащую текущему пользователю."""
    deal = session.exec(
        select(Deal).where(
            Deal.id == deal_id,
            Deal.owner_id == current_user.id,
        )
    ).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав доступа к сделке",
        )
    return deal


@router.post(
    "/deals/{deal_id}/documents",
    response_model=list[DocumentRead],
    status_code=status.HTTP_201_CREATED,
)
def upload_documents(
    deal_id: int,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Document]:
    """Загрузить файлы: сохранить, распознать и классифицировать."""
    deal = _get_owned_deal(deal_id, current_user, session)

    deal_dir = UPLOAD_DIR / str(deal_id)
    deal_dir.mkdir(parents=True, exist_ok=True)

    created: list[Document] = []
    for file in files:
        original_name = file.filename or "unnamed"
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {suffix}",
            )

        # Префикс по времени защищает от перезаписи одноимённых файлов.
        unique_name = f"{utcnow().strftime('%Y%m%d%H%M%S%f')}_{original_name}"
        file_path = deal_dir / unique_name
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ocr_text = ""
        try:
            ocr_text = ocr.extract_text(file_path)
        except Exception:
            logger.exception("Не удалось распознать файл %s", unique_name)

        result = classifier.classify_document(ocr_text, DOCUMENT_TYPES)
        document = Document(
            deal_id=deal.id,
            doc_type=result["type"],
            filename=original_name,
            file_path=str(file_path),
            ocr_text=ocr_text or None,
            confidence=result["confidence"],
        )
        session.add(document)
        created.append(document)

    session.commit()
    for document in created:
        session.refresh(document)
    return created


@router.get("/deals/{deal_id}/documents", response_model=list[DocumentRead])
def list_documents(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Document]:
    """Список документов сделки."""
    deal = _get_owned_deal(deal_id, current_user, session)
    documents = session.exec(
        select(Document)
        .where(Document.deal_id == deal.id)
        .order_by(Document.uploaded_at)
    ).all()
    return list(documents)


@router.get("/deals/{deal_id}/checklist", response_model=ChecklistRead)
def get_checklist(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ChecklistRead:
    """Проверить комплектность пакета документов сделки."""
    deal = _get_owned_deal(deal_id, current_user, session)
    documents = session.exec(
        select(Document.doc_type).where(Document.deal_id == deal.id)
    ).all()
    found = {doc_type for doc_type in documents if doc_type}
    return ChecklistRead(
        present=[name for name in REQUIRED_DOCUMENTS if name in found],
        missing=[name for name in REQUIRED_DOCUMENTS if name not in found],
    )


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    """Удалить документ и его файл с диска."""
    document = session.exec(
        select(Document).where(Document.id == document_id)
    ).first()
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Проверяем, что сделка документа принадлежит текущему пользователю.
    _get_owned_deal(document.deal_id, current_user, session)

    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()

    session.delete(document)
    session.commit()
    return {"ok": True}
