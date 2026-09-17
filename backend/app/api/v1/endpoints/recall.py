import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.recall_item import RecallItem
from app.schemas.recall import (
    RecallItemCreate,
    RecallReviewRequest,
    RecallItemResponse,
)
from app.services.user_service import get_or_create_default_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/items",
    response_model=RecallItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Active Recall item",
)
async def create_recall_item(
    payload: RecallItemCreate,
    db: AsyncSession = Depends(get_db),
) -> RecallItemResponse:
    """Creates a new Active Recall card scheduled for immediate first review."""
    user_id = payload.user_id
    if user_id is None:
        user = await get_or_create_default_user(db)
        user_id = user.id

    item = RecallItem(
        user_id=user_id,
        study_material_id=payload.study_material_id,
        question=payload.question,
        answer=payload.answer,
        context_clue=payload.context_clue,
        easiness_factor=2.5,
        interval=0,
        repetitions=0,
        lapses=0,
        state="new",
        next_review_at=datetime.now(timezone.utc),
    )

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return RecallItemResponse.model_validate(item)


@router.get(
    "/due",
    response_model=List[RecallItemResponse],
    summary="Fetch all Active Recall items currently due for review",
)
async def get_due_recall_items(
    db: AsyncSession = Depends(get_db),
) -> List[RecallItemResponse]:
    """Returns items whose next_review_at is in the past or now."""
    now = datetime.now(timezone.utc)
    stmt = (
        select(RecallItem)
        .where(RecallItem.next_review_at <= now)
        .order_by(RecallItem.next_review_at.asc())
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return [RecallItemResponse.model_validate(item) for item in items]


@router.post(
    "/items/{item_id}/review",
    response_model=RecallItemResponse,
    summary="Record review rating and update Spaced Repetition interval via SM-2",
)
async def record_recall_review(
    item_id: uuid.UUID,
    payload: RecallReviewRequest,
    db: AsyncSession = Depends(get_db),
) -> RecallItemResponse:
    """
    Applies the SuperMemo-2 (SM-2) algorithm to recalculate:
    - Repetitions
    - Interval (in days)
    - Easiness Factor (EF)
    - Next review timestamp
    """
    stmt = select(RecallItem).where(RecallItem.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recall item with ID {item_id} not found.",
        )

    grade = payload.rating
    now = datetime.now(timezone.utc)

    # 1. Update repetitions & intervals according to SM-2
    if grade < 3:
        # Failed recall: reset repetitions and schedule review tomorrow
        item.repetitions = 0
        item.interval = 1
        item.lapses += 1
        item.state = "relearning"
    else:
        # Successful recall
        if item.repetitions == 0:
            item.interval = 1
        elif item.repetitions == 1:
            item.interval = 6
        else:
            item.interval = max(1, round(item.interval * item.easiness_factor))
        item.repetitions += 1
        item.state = "review"

    # 2. Update Easiness Factor (EF)
    # Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    ef_delta = 0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)
    new_ef = item.easiness_factor + ef_delta
    item.easiness_factor = max(1.3, round(new_ef, 4))

    # 3. Schedule next review date
    item.last_reviewed_at = now
    item.next_review_at = now + timedelta(days=item.interval)

    await db.commit()
    await db.refresh(item)
    return RecallItemResponse.model_validate(item)
