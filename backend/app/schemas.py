"""Pydantic-схемы запросов и ответов."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    """Базовые поля пользователя."""

    email: str


class UserCreate(UserBase):
    """Регистрация пользователя."""

    password: str


class UserRead(UserBase):
    """Ответ с данными пользователя."""

    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DealBase(BaseModel):
    """Базовые поля сделки."""

    title: str
    description: Optional[str] = None


class DealCreate(DealBase):
    """Создание сделки."""

    pass


class DealUpdate(BaseModel):
    """Частичное обновление сделки."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class DealRead(DealBase):
    """Ответ со сделкой."""

    id: int
    status: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentRead(BaseModel):
    """Ответ с документом."""

    id: int
    deal_id: int
    doc_type: Optional[str] = None
    filename: str
    file_path: str
    ocr_text: Optional[str] = None
    confidence: Optional[float] = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}
