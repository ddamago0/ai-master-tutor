import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class RecallItem(Base):
    __tablename__ = "recall_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    study_material_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_materials.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    # Active Recall Content
    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    context_clue: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Spaced Repetition Parameters (SM-2 / FSRS compatible)
    easiness_factor: Mapped[float] = mapped_column(
        Float,
        default=2.5,
        nullable=False,
    )  # EF in SuperMemo SM-2 (min 1.3, default 2.5)
    interval: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )  # Current interval in days until next review
    repetitions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )  # Consecutive successful recall count
    lapses: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )  # Count of times user failed after mastering
    state: Mapped[str] = mapped_column(
        String(20),
        default="new",
        nullable=False,
    )  # "new", "learning", "review", "relearning"

    next_review_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="recall_items",
    )
    study_material: Mapped[Optional["StudyMaterial"]] = relationship(
        "StudyMaterial",
        back_populates="recall_items",
    )
