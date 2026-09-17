import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class RecallItemCreate(BaseModel):
    question: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Active recall challenge prompt or flashcard question.",
    )
    answer: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Expected target concept or model answer.",
    )
    context_clue: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Context hint or quote from original study material.",
    )
    study_material_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Associated study material ID.",
    )
    user_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Target student ID.",
    )

    @field_validator("question", "answer")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        return v.strip().replace("\x00", "")


class RecallReviewRequest(BaseModel):
    rating: int = Field(
        ...,
        ge=0,
        le=5,
        description="SuperMemo SM-2 grade from 0 (complete blackout) to 5 (perfect instant recall).",
    )


class RecallItemResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    study_material_id: Optional[uuid.UUID]
    question: str
    answer: str
    context_clue: Optional[str]
    easiness_factor: float
    interval: int
    repetitions: int
    lapses: int
    state: str
    next_review_at: datetime
    last_reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
