"""Роутер управления сделками."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..auth import get_current_user
from ..database import get_session
from ..models import Deal, User, utcnow
from ..schemas import DealCreate, DealRead, DealUpdate

router = APIRouter(prefix="/api/deals", tags=["deals"])

ALLOWED_STATUSES = {"open", "complete"}


def _get_owned_deal(
    deal_id: int,
    current_user: User,
    session: Session,
) -> Deal:
    """Найти сделку, принадлежащую текущему пользователю."""
    deal = session.exec(
        select(Deal).where(
            Deal.id == deal_id,
            Deal.owner_id == current_user.id,
        )
    ).first()
    if deal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found",
        )
    return deal


@router.get("", response_model=list[DealRead])
def list_deals(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Deal]:
    """Список сделок текущего пользователя."""
    deals = session.exec(
        select(Deal)
        .where(Deal.owner_id == current_user.id)
        .order_by(Deal.created_at.desc())
    ).all()
    return list(deals)


@router.post("", response_model=DealRead, status_code=status.HTTP_201_CREATED)
def create_deal(
    payload: DealCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Deal:
    """Создать сделку."""
    deal = Deal(
        title=payload.title,
        description=payload.description,
        owner_id=current_user.id,
    )
    session.add(deal)
    session.commit()
    session.refresh(deal)
    return deal


@router.get("/{deal_id}", response_model=DealRead)
def get_deal(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Deal:
    """Получить сделку по идентификатору."""
    return _get_owned_deal(deal_id, current_user, session)


@router.patch("/{deal_id}", response_model=DealRead)
def update_deal(
    deal_id: int,
    payload: DealUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Deal:
    """Обновить сделку частично."""
    deal = _get_owned_deal(deal_id, current_user, session)
    updates: dict[str, Optional[str]] = payload.model_dump(exclude_unset=True)

    if "status" in updates and updates["status"] not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status",
        )

    for field, value in updates.items():
        setattr(deal, field, value)

    deal.updated_at = utcnow()
    session.add(deal)
    session.commit()
    session.refresh(deal)
    return deal


@router.delete("/{deal_id}")
def delete_deal(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    """Удалить сделку."""
    deal = _get_owned_deal(deal_id, current_user, session)
    session.delete(deal)
    session.commit()
    return {"ok": True}
