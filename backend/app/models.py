"""Модели SQLModel: пользователь, сделка, документ."""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Текущее время в UTC с часовым поясом."""
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """Пользователь сервиса."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)


class Deal(SQLModel, table=True):
    """Сделка — один пакет документов."""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = "open"  # open | complete
    owner_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column_kwargs={"onupdate": utcnow},
    )


class Document(SQLModel, table=True):
    """Документ внутри сделки."""

    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(foreign_key="deal.id", index=True)
    doc_type: Optional[str] = None
    filename: str
    file_path: str
    ocr_text: Optional[str] = None
    confidence: Optional[float] = None
    uploaded_at: datetime = Field(default_factory=utcnow)
